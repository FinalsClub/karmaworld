import re
import bleach
import html5lib
from html5lib.constants import tokenTypes
from html5lib.sanitizer import HTMLSanitizerMixin
from html5lib.tokenizer import HTMLTokenizer
from bleach.sanitizer import BleachSanitizer
from bleach import _render
import bleach_whitelist
from bs4 import BeautifulSoup
from PIL import Image
from cStringIO import StringIO
import base64
import uuid

def _canonical_link_predicate(tag):
    return tag.name == u'link' and \
        tag.has_attr('rel') and \
        u'canonical' in tag['rel']

class Sanitizer(BleachSanitizer):
    """
    The default bleach clean method uses a sanitizer that handles disallowed
    tags either by escaping them. With the bad HTML 

        <script>alert('bad')</script>

    if ``strip=False``, bleach will output:
    
        &lt;script&gt;alert('bad')&lt;/script&gt;

    if ``strip=True``, bleach will output:

        alert('bad')

    But we want to strip both the tag and contents for certain tags like script
    and style.  This subclass does that.

    Also support data URI's for some mimetypes (image/png, image/gif, image/jpeg)
    """
    allowed_elements = bleach_whitelist.markdown_tags
    allowed_attributes = bleach_whitelist.markdown_attrs
    suppressed_elements = ["script", "style"]
    strip_disallowed_elements = True
    strip_html_comments = True

    def __init__(self, *args, **kwargs):
        self.suppressing = None
        super(Sanitizer, self).__init__(*args, **kwargs)

    def sanitize_token(self, token):
        # Do sanitization on the parent.
        result = super(Sanitizer, self).sanitize_token(token)

        # Suppress elements like script and style entirely.
        if token.get('name') and token['name'] in self.suppressed_elements:
            if token['type'] == tokenTypes['StartTag']:
                self.suppressing = token['name']
            elif token['type'] == tokenTypes['EndTag'] and token['name'] == self.suppressing:
                self.suppressing = False
        if self.suppressing:
            return {u'data': '', 'type': 2}
        else:
            return result

class DataUriReplacer(HTMLTokenizer, HTMLSanitizerMixin):
    """
    Convert any valid image data URI's to files, and upload them to s3. Replace
    the data URI with a link to the file in s3.
    """
    VALID_URI = "^data:image/(png|gif|jpeg);base64,[A-Za-z0-9+/=]+$"

    def sanitize_token(self, token):
        if token.get('name') == u"img":
            attrs = dict([(name, val) for name, val in token['data'][::-1]])
            if 'src' in attrs:
                src = attrs['src']
                if re.match(self.VALID_URI, src):
                    url = self._upload_image(src)
                    attrs['src'] = url
                    token['data'] = [(k,v) for k,v in attrs.iteritems()]
        return token

    def _upload_image(self, data_uri):
        from django.core.files.storage import default_storage
        from karmaworld.apps.notes.models import all_read_xml_acl
        from django.conf import settings

        mimetype, data = data_uri.split(";base64,")
        sio = StringIO()
        sio.write(base64.b64decode(data))
        sio.seek(0)
        try:
            image = Image.open(sio)
        except IOError:
            raise ValueError("Bad image data URI")

        fmt = mimetype.split("/")[1]

        image_data = StringIO()
        image.save(image_data, format=fmt)

        filepath = "images/{}.{}".format(uuid.uuid4(), fmt)
        new_key = default_storage.bucket.new_key(filepath)
        new_key.set_contents_from_string(image_data.getvalue(), {"Content-Type": mimetype})
        new_key.set_xml_acl(all_read_xml_acl)
        parts = [settings.S3_URL, filepath]
        if parts[0].startswith("//"):
            # Fully resolve the URL as https for happiness in all things.
            parts.insert(0, "https:")
        return "".join(parts)

    def __iter__(self):
        for token in HTMLTokenizer.__iter__(self):
            token = self.sanitize_token(token)
            if token:
                yield token

def sanitize_html(raw_html):
    """
    Sanitize the given raw_html.
    """
    # Strip tags to the few that we like
    parser = html5lib.HTMLParser(tokenizer=Sanitizer)
    clean = _render(parser.parseFragment(raw_html))

    # Set anchor tags' targets
    clean = bleach.linkify(clean, callbacks=[
        bleach.callbacks.nofollow,
        bleach.callbacks.target_blank
    ], tokenizer=Sanitizer)
    return clean

def data_uris_to_s3(raw_html):
    parser = html5lib.HTMLParser(tokenizer=DataUriReplacer)
    clean = _render(parser.parseFragment(raw_html))
    return clean

def set_canonical_rel(raw_html, href):
    """
    Add or update <link rel='canonical'...> in the given html to the given
    href. Note that this has the side effect of appending html/head/body tags
    to the given html fragment if it doesn't already have them.
    """
    soup = BeautifulSoup(raw_html)
    canonical_tags = soup.find_all(_canonical_link_predicate)
    if canonical_tags:
        for tag in canonical_tags:
            tag['href'] = href
    else:
        new_tag = soup.new_tag('link', rel='canonical', href=href)
        head = soup.find('head')
        head.append(new_tag)
    return unicode(soup)
