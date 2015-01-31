import bleach
import bleach_whitelist
from bs4 import BeautifulSoup

def _canonical_link_predicate(tag):
    return tag.name == u'link' and \
        tag.has_attr('rel') and \
        u'canonical' in tag['rel']

def sanitize_html(raw_html, canonical_rel=None):
    """
    Arguments:

    unclean: raw html to be cleaned
    canonical_rel: optional fully qualified URL to set as canonical link.
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

def set_canonical_rel(raw_html, canonical_rel):
    soup = BeautifulSoup(raw_html)
    canonical_tags = soup.find_all(_canonical_link_predicate)
    if canonical_tags:
        for tag in canonical_tags:
            tag['href'] = canonical_rel
    else:
        new_tag = soup.new_tag('link', rel='canonical', href=canonical_rel)
        head = soup.find('head')
        head.append(new_tag)
    return unicode(soup)
