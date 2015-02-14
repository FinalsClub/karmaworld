# -*- coding: utf-8 -*-

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

class SuppressingSanitizer(BleachSanitizer):
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
    """
    suppressed_elements = ["script", "style"]

    def __init__(self, *args, **kwargs):
        self.suppressing = None
        super(SuppressingSanitizer, self).__init__(*args, **kwargs)

    def sanitize_token(self, token):
        # Do sanitization on the parent.
        result = super(SuppressingSanitizer, self).sanitize_token(token)
        if "name" not in token:
            if self.suppressing:
                return None
            return result

        tag_name = token['name']

        # Suppress elements like script and style entirely.
        if tag_name in self.suppressed_elements:
            if token['type'] == tokenTypes['StartTag']:
                self.suppressing = tag_name
            elif token['type'] == tokenTypes['EndTag'] and tag_name == self.suppressing:
                self.suppressing = False

        elif tag_name in self.required_attributes:
            if result and result.get('type') == tokenTypes['StartTag']:
                attr_dict = dict(result.get('data', []) or [])
                for attr, val in self.required_attributes[tag_name].iteritems():
                    attr_dict[attr] = val
                result['data'] = attr_dict.items()

        if self.suppressing:
            return None
        else:
            return result

class EditableSanitizer(SuppressingSanitizer):
    """
    Sanitizer tokenizer optimized for producing HTML suitable for editing in
    client-side WYSIWYG's.
    """
    allowed_elements = bleach_whitelist.markdown_tags
    allowed_attributes = {
        "img": ["src", "width", "height"],
        "a": ["href", "target", "rel"],
    }
    required_attributes = {
        "a": { "rel": "nofollow", "target": "_blank" }
    }
    suppressed_elements = ["script", "style"]
    strip_disallowed_elements = True
    strip_html_comments = True

class PreserveFormattingSanitizer(SuppressingSanitizer):
    """
    Lax sanitizer tokenizer optimized for preserving the formatting in the
    incoming HTML, while still removing XSS threats.
    """
    allowed_elements = bleach_whitelist.generally_xss_safe
    allowed_attributes = {
        "*": ["class", "style"],
        "img": ["src", "width", "height"],
        "a": ["href", "target", "rel"],
    }
    required_attributes = {
        "a": { "rel": "nofollow", "target": "_blank" }
    }
    allowed_css_properties = bleach_whitelist.all_styles
    suppressed_elements = ["script"]
    strip_disallowed_elements = True
    strip_html_comments = True

class DataUriReplacer(HTMLTokenizer, HTMLSanitizerMixin):
    """
    Convert any valid image data URI's to files, and upload them to s3. Replace
    the data URI with a link to the file in s3.
    """
    VALID_IMAGE_URI = "^data:image/(png|gif|jpeg);base64,[A-Za-z0-9+/=]+$"
    VALID_FONT_FACE_FORMATS = ["woff"]

    def __init__(self, *args, **kwargs):
        self.in_style = False
        self.style_content = []
        self.font_face_cache = {}
        super(DataUriReplacer, self).__init__(*args, **kwargs)

    def sanitize_token(self, token):
        # Handle images
        tag_name = token.get("name")
        if tag_name == u"img":
            attrs = dict([(name, val) for name, val in token['data'][::-1]])
            if 'src' in attrs:
                src = attrs['src']
                if re.match(self.VALID_IMAGE_URI, src):
                    url = self._upload_image(src)
                    attrs['src'] = url
                    token['data'] = [(k,v) for k,v in attrs.iteritems()]

        # Handle font-faces.
        if self.in_style:
            if 'data' in token and token['type'] == 1:
                token['data'] = self._extract_and_upload_data_uri_fonts(token['data'])

        if tag_name == u"style":
            if token['type'] == tokenTypes['StartTag']:
                self.in_style = True
            elif token['type'] == tokenTypes['EndTag']:
                self.in_style = False

        return token

    def _extract_and_upload_data_uri_fonts(self, raw_css):
        # Might be better to use a full-fledged CSS parser, but it has to be
        # modern enough to support font-faces and data-uri's.
        pattern = r"""(?P<intro>
                @font-face\s*{      # font-face opening
                (?:[^\}]+;)?        # any parts before the src
                \s*src\s*:\s*             # src declaration
                  url\(['"])?data:      # url opener
                    (?P<mimetype>application/font-(?P<ext>%s)) # mimetype
                    ;base64, 
                    (?P<data_uri>[A-Za-z0-9+/=]+) # data-uri itself
                 (?P<outro>['"]?\)) # url closer 
        """ % "|".join(self.VALID_FONT_FACE_FORMATS)
        return re.sub(pattern,
                repl=self._upload_font_match,
                string=raw_css,
                flags=re.VERBOSE | re.DOTALL)

    def _upload_font_match(self, match):
        url = ""
        if match:
            ext = match.group('ext')
            mimetype = match.group('mimetype')
            data_uri = match.group('data_uri')
            if ext in self.VALID_FONT_FACE_FORMATS:
                filepath = "fonts/{}.{}".format(uuid.uuid4(), ext)
                sio = StringIO()
                sio.write(base64.b64decode(data_uri))
                sio.seek(0)
                value = sio.getvalue()
                if value in self.font_face_cache:
                    url = self.font_face_cache[value]
                else:
                    url = self._s3_upload(filepath, mimetype, sio.getvalue())
                    self.font_face_cache[value] = url
        return u"".join((match.group('intro'), url, match.group('outro')))

    def _upload_image(self, data_uri):
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
        return self._s3_upload(filepath, mimetype, image_data.getvalue())

    def _s3_upload(self, filepath, mimetype, data):
        from django.core.files.storage import default_storage
        from karmaworld.apps.notes.models import all_read_xml_acl
        from django.conf import settings

        new_key = default_storage.bucket.new_key(filepath)
        new_key.set_contents_from_string(data, {"Content-Type": mimetype})
        new_key.set_xml_acl(all_read_xml_acl)
        parts = [settings.S3_URL, filepath]
        if parts[0].startswith("//"):
            # Fully resolve the URL as https for happiness in all things. ॐ
            parts.insert(0, "https:")
        return "".join(parts)


    def __iter__(self):
        for token in HTMLTokenizer.__iter__(self):
            token = self.sanitize_token(token)
            if token:
                yield token

def _sanitize_html(raw_html, tokenizer):
    parser = html5lib.HTMLParser(tokenizer=tokenizer)
    clean = _render(parser.parseFragment(raw_html))
    return clean

def sanitize_html_to_editable(raw_html):
    """
    Sanitize the given raw_html, with the result in a format suitable for
    editing in client-side HTML WYSIWYG editors.
    """
    return _sanitize_html(raw_html, EditableSanitizer)

def sanitize_html_preserve_formatting(raw_html):
    """
    Sanitize the given HTML, preserving as much of the original formatting as
    possible.
    """
    return _sanitize_html(raw_html, PreserveFormattingSanitizer)

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
