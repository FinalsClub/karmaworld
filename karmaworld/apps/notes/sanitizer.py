import bleach
import bleach_whitelist
from bs4 import BeautifulSoup

def _canonical_link_predicate(tag):
    return tag.name == u'link' and \
        tag.has_attr('rel') and \
        u'canonical' in tag['rel']

def sanitize_html(raw_html):
    """
    Sanitize the given raw_html.
    """
    # Strip tags to the few that we like
    clean = bleach.clean(raw_html,
        bleach_whitelist.markdown_tags,
        bleach_whitelist.markdown_attrs,
        strip=True)

    # Set anchor tags' targets
    clean = bleach.linkify(clean, callbacks=[
        bleach.callbacks.nofollow,
        bleach.callbacks.target_blank
    ])
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
