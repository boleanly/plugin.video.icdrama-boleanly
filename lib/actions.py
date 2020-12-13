import urllib
import functools
import re
import xbmc
import xbmcgui
import xbmcaddon
from resolveurl.lib.net import get_ua
from lib import config, common, scrapers, store, cleanstring, cache
import localizer as lc
import sourceutil

loc = lc.getLocalizer()

actions = []
def _action(func):
    '''Decorator
    Mark the function as a valid action by
    putting the name of `func` into `actions`
    '''
    actions.append(func.__name__)
    return func

def _dir_action(func):
    '''Decorator
    Assumes `func` returns list of diritems
    Results from calling `func` are used to build plugin directory
    '''
    @_action # Note: must keep this order to get func name
    @functools.wraps(func)
    def make_dir(*args, **kargs):
        diritems = func(*args, **kargs)
        if not diritems:
            return
        for di in diritems:
            common.add_item(di)
        common.end_dir()
    return make_dir

@_dir_action
def index():
    return config.index_items

def _saved_to_list_context_menu(eng_name, ori_name, show_url, image):
    add_save_url = common.action_url('add_to_saved', eng_name=eng_name, ori_name=ori_name,
                                     show_url=show_url, image=image)
    builtin_url = common.run_plugin_builtin_url(add_save_url)
    context_menu = [(loc.getLocalizedString(33108), builtin_url)]
    return context_menu

@_dir_action
def shows(url):
    di_list = []
    for eng_name, ori_name, show_url, image in scrapers.shows(url):
        action_url = common.action_url('versions', url=show_url)
        name = cleanstring.show(eng_name, ori_name)
        cm = _saved_to_list_context_menu(eng_name, ori_name, show_url, image)
        di_list.append(common.diritem(name, action_url, image, context_menu=cm))
    for page, page_url in scrapers.pages(url):
        action_url = common.action_url('shows', url=page_url)
        page_label = cleanstring.page(page)
        di_list.append(common.diritem(page_label, action_url))
    return di_list

@_dir_action
def recent_updates(url):
    di_list = []
    for name, update_url in scrapers.recent_updates(url):
        action_url = common.action_url('mirrors', url=update_url)
        di_list.append(common.diritem(name, action_url))
    return di_list

@_dir_action
def versions(url):
    versions = scrapers.versions(url)
    if len(versions) == 1:
        ver, href = versions[0]
        return _episodes(href)
    else:
        auto_select = xbmcaddon.Addon().getSetting('auto_select_version')
        if auto_select == 'true':
            '''priorities = [('Cantonese', int(xbmcaddon.Addon().getSetting('cantonese_priority'))),
                          ('Mandarin', int(xbmcaddon.Addon().getSetting('mandarin_priority'))),
                          ('Chinese Subtitles', int(xbmcaddon.Addon().getSetting('ch_sub_priority'))),
                          ('English Subtitles', int(xbmcaddon.Addon().getSetting('eng_sub_priority')))]'''
            '''def sort_key(a):
                for priority in priorities:
                    if priority[0] in a[0]:
                        return priority[1]
                return ""
                for priority in priorities:
                    if priority[0] in versions[0][0]:# Fits the priority list above
                        version, href = versions[0]
                        return _episodes(href)'''
            def match_str(string):
                    match = re.match(r'Watch online \(([^\)]+)\)$', string)
                    if match:
                        return match.group(1)
                    else:
                        return ""
            
            priorities = {'Cantonese': int(xbmcaddon.Addon().getSetting('cantonese_priority')),
                          'Mandarin': int(xbmcaddon.Addon().getSetting('mandarin_priority')),
                          'Chinese Subtitles': int(xbmcaddon.Addon().getSetting('ch_sub_priority')),
                          'English Subtitles': int(xbmcaddon.Addon().getSetting('eng_sub_priority'))}
            
            def sort_key(a):
                try:
                    return priorities[cleanstring.version(a[0])]
                except Exception as e:
                    print("Icdrama: " + str(e))
                    return ""
            versions.sort(key = sort_key)
            
            priority_indices = {}
            for k, v in priorities.items():
                L = priority_indices.get(v, [])
                L.append(k)
                priority_indices[v] = L
            
            min_priority = min(priority_indices.keys())
            count = len([label for label, _ in versions if match_str(label) in priority_indices[min_priority]])

            if count == 1:
                version, href = versions[0]
                return _episodes(href)
            elif count > 1:
                di_list = []
                for i in range(count):
                    label, version_url = versions[i]
                    action_url = common.action_url('episodes', url=version_url)
                    ver = cleanstring.version(label)
                    di_list.append(common.diritem(ver, action_url))
                return di_list
            
            # Else create full directory
        
        di_list = []
        for label, version_url in versions:
            action_url = common.action_url('episodes', url=version_url)
            ver = cleanstring.version(label)
            di_list.append(common.diritem(ver, action_url))
        return di_list

@_dir_action
def episodes(url):
    return _episodes(url)

def _episodes(url):
    episodes = scrapers.episodes(url)
    if len(episodes) > 0:
        di_list = []
        for name, episode_url in episodes:
            action_url = common.action_url('mirrors', url=episode_url)
            epi = cleanstring.episode(name)
            di_list.append(common.diritem(epi, action_url))
        return di_list
    else:
        return _mirrors(url)

@_dir_action
def search(url=None):
    if not url:
        heading = loc.getLocalizedString(33301)
        s = common.input(heading)
        if s:
            if type(s) is unicode:
                s = url.encode('utf8')
            url = config.search_url % urllib.quote(s)
        else:
            return []
    di_list = []
    for eng_name, ori_name, show_url, image in scrapers.search(url):
        action_url = common.action_url('versions', url=show_url)
        name = cleanstring.show(eng_name, ori_name)
        cm = _saved_to_list_context_menu(eng_name, ori_name, show_url, image)
        di_list.append(common.diritem(name, action_url, image, context_menu=cm))
    for page, page_url in scrapers.pages(url):
        action_url = common.action_url('search', url=page_url)
        page_label = cleanstring.page(page)
        di_list.append(common.diritem(page_label, action_url))
    if not di_list:
        common.popup(loc.getLocalizedString(33304))
    return di_list


_saved_list_key = 'saved_list'
def _get_saved_list():
    try:
        return store.get(_saved_list_key)
    except KeyError:
        pass
    try: # backward compatible (try cache)
        return cache.get(_saved_list_key)
    except KeyError:
        return []


@_dir_action
def saved_list():
    sl = _get_saved_list()
    di_list = []
    for eng_name, ori_name, show_url, image in sl:
        action_url = common.action_url('versions', url=show_url)
        name = cleanstring.show(eng_name, ori_name)
        remove_save_url = common.action_url('remove_saved', eng_name=eng_name, ori_name=ori_name,
                                            show_url=show_url, image=image)
        builtin_url = common.run_plugin_builtin_url(remove_save_url)
        cm = [(loc.getLocalizedString(33109), builtin_url)]
        di_list.append(common.diritem(name, action_url, image, context_menu=cm))
    return di_list

@_action
def add_to_saved(eng_name, ori_name, show_url, image):
    with common.busy_indicator():
        sl = _get_saved_list()
        sl.insert(0, (eng_name, ori_name, show_url, image))
        uniq = set()
        sl = [x for x in sl if not (x in uniq or uniq.add(x))]
        store.put(_saved_list_key, sl)
    common.popup(loc.getLocalizedString(33302))

@_action
def remove_saved(eng_name, ori_name, show_url, image):
    sl = _get_saved_list()
    sl.remove((eng_name, ori_name, show_url, image))
    store.put(_saved_list_key, sl)
    common.refresh()
    common.popup(loc.getLocalizedString(33303))

@_action
def play_mirror(url):
    playing = False
    player = None
    orig_url = ''
    
    with common.busy_indicator():
        vidurl = common.resolve(url)
        orig_url = vidurl
        if vidurl:
            try:
                title, image = scrapers.title_image(url)
            except Exception:
                # we can proceed without the title and image
                title, image = ('', '')
            li = xbmcgui.ListItem(title)
            li.setArt({ 'thumb' : image })
            if 'User-Agent=' not in vidurl:
                vidurl = vidurl + '|User-Agent=' + urllib.quote(get_ua())
            
            # Instantiate own player class
            player = MyPlayer()
            
            player.play(vidurl, li)

            
            playing = True
    
    if player:
        counter = 0
        # Checks for a minimum of 60 seconds; keeps script alive for this time
        while player.alive and counter < 30:
            counter += 1
            xbmc.sleep(2000)
        
        if not player.hasStarted:
            common.debug('Icdrama: Player encountered a format that prevented it from starting')
            # Add to blacklist
            sourceutil.add_blacklist(orig_url)
            
            # Delete to free up reference
            del player
            
            # Try again
            play_mirror(url)
            
        else:
            # Delete to free up reference
            del player
    
    return playing

@_dir_action
def mirrors(url):
    return _mirrors(url)

def _mirrors(url):
    mirrors = scrapers.mirrors(url)
    num_mirrors = len(mirrors)
    if num_mirrors > 0:
        di_list = []
        if (xbmcaddon.Addon().getSetting('auto_select_mirror') == 'true'):
            for mirr_label, parts in mirrors:
                if "Full" in parts[0][0]:
                    if play_mirror(parts[0][1]):
                        return []
        else:
            for mirr_label, parts in mirrors:
                for part_label, part_url in parts:
                    label = cleanstring.mirror(mirr_label, part_label)
                    action_url = common.action_url('play_mirror', url=part_url)
                    di_list.append(common.diritem(label, action_url, isfolder=False))
            return di_list
    else:
        # if no mirror listing, try to resolve this page directly
        play_mirror(url)
        return []

@_action
def refresh():
    common.refresh()

# Player with callbacks to identify bad links
class MyPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)
        self.alive = True
        self.hasStarted = False
    
    # If Kodi cannot plays a link with an unplayable format, this never runs
    def onPlayBackStarted(self):
        self.hasStarted = True

    def onPlayBackError(self):
        self.alive = False

    def onPlayBackStopped(self):
        self.alive = False

    def onPlayBackEnded(self):
        self.onPlayBackStopped()
