import re
import xbmcaddon
import localizer as lc


loc = lc.getLocalizer()
        
def show(eng, orig):
    eng = eng.strip(' -')
    orig = orig.strip(' -')
    title_lang = int(xbmcaddon.Addon().getSetting('title_language'))
    if not orig:
        return eng
    elif not eng:
        return orig
    elif title_lang == 1:
        return eng
    elif title_lang == 2:
        return orig
    else: # title_lang == 0
        return '%s - %s' % (eng, orig)

def page(page):
    match = re.match(r'Page (\d+)$', page)
    if match:
        page = loc.getLocalizedString(33102) % match.group(1)
    elif re.match(u'\u00ab First$', page):
        page = loc.getLocalizedString(33103)
    elif re.match(u'Last \u00bb$', page):
        page = loc.getLocalizedString(33104)
    else:
        pass
    return '[I][ %s ][/I]' % page

def version(version):
    if version == 'Watch online (Chinese Subtitles)':
        version = loc.getLocalizedString(33110)
    elif version == 'Watch online (English Subtitles)':
        version = loc.getLocalizedString(33111)
    elif version == 'Watch online (Cantonese)':
        version = loc.getLocalizedString(33112)
    elif version == 'Watch online (Mandarin)':
        version = loc.getLocalizedString(33113)
    else:
        match = re.match(r'Watch online \(([^\)]+)\)$', version)
        if match:
            version = match.group(1)
    return version

def episode(episode):
    match = re.match(r'(\d+)(?: \[END\]|)$', episode)
    if match:
        return loc.getLocalizedString(33105) % match.group(1)
    elif re.match(r'\d{4}-\d{2}-\d{2}', episode):
        return episode
    else:
        pass
    return episode

def mirror(mirror, part):
    match = re.match(r'(?:Part ?|)(\d+)$', part)
    if match:
        part = loc.getLocalizedString(33106) % match.group(1)
    elif part == 'Full':
        part = loc.getLocalizedString(33107)
    else:
        pass
    return '[B]%s[/B] : %s' % (mirror, part)
