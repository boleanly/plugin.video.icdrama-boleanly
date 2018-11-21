import re
import urllib2
import urllib
import config
import cPickle as pickle
from os import makedirs, remove
from os.path import isfile, dirname, exists
from urlresolver import common
import time
import xbmcaddon

if xbmcaddon.Addon().getSetting('prioritize_1080p') == 'true':
    priority_list = [u'Picasaweb 1080p',
                    u'Picasaweb 720p',
                    u'VideoBug',
                    u'Picasaweb 360p',
                    u'Uptobox']
else:
    priority_list = [u'Picasaweb 720p',
                    u'VideoBug',
                    u'Picasaweb 360p',
                    u'Uptobox']

def read_blacklist():
    list = [[],[]]
    
    if isfile(config.blacklist_file):
        try:
            with open(config.blacklist_file, 'rb') as f:
                list = pickle.load(f)
                if list[0] is not None and isinstance(list[0], str):
                    list = [[],[]]
                    
        except Exception:
            # if anything goes wrong, remove file
            try:
                remove(config.blacklist_file)
            except OSError:
                pass
            # TODO: log exception
            list = [[],[]]
    else:
        write_blacklist(list)
    
    return list

def write_blacklist(list):
    try:
        # create directory for file if not exists
        parent = dirname(config.blacklist_file)
        if not exists(parent):
            makedirs(parent)

        with open(config.blacklist_file, 'wb+') as f:
            pickle.dump(list, f)
    except Exception:
        # TODO: log exception
        pass

def add_blacklist(url):
    if blacklist is not None and not check_blacklist(url):
        print('Icdrama: Appending to blacklist...')
        print(url)
        blacklist[0].append(url)
        blacklist[1].append(time.time())
        write_blacklist(blacklist)
    
def reset_blacklist():
    blacklist = [[],[]]
    write_blacklist(blacklist)

def check_blacklist(url):
    print('Check blacklist')
    print(url)
    
    index = -1
    
    for i in range(len(blacklist[0])):
        if url == blacklist[0][i]:
            index = i
            break
    
    if index < 0:
        return False
    elif time.time() - blacklist[1][index] > 7 * 86400:
        print('expired')
        blacklist[0].pop(index)
        blacklist[1].pop(index)
        write_blacklist(blacklist)
        return False
    else:
        print(url in blacklist[0])
        return True

def sort_sources(urls):
    
    def comp(a, b):
        if a[0] in priority_list and b[0] in priority_list:
            return priority_list.index(a[0]) - priority_list.index(b[0])
        elif a[0] in priority_list:
            return -1
        elif b[0] in priority_list:
            return 1
        else:
            return 0
    
    def key(a):
        if a[0] in priority_list:
            return priority_list.index(a[0])
        else:
            return ""
    
    urls.sort(key = key)

def pick_source(sources):
    sort_sources(sources)
    source = ''
    index = 0
    
    if len(sources) >= 1:
        source = sources[0][1]
        while (check_blacklist(source) or not test_stream(source)) and index < len(sources):
            index = index + 1
            source = sources[index][1]
        
        return source
    else:
        raise Exception("No video link")

def test_stream(stream_url):
    '''
    Returns True if the stream_url gets a non-failure http status (i.e. <400) back from the server
    otherwise return False

    Intended to catch stream urls returned by resolvers that would fail to playback
    
    From UrlResolver but modified
    '''
    common.logger.log_debug('Testing Url: %s' % (stream_url))
    
    try:
        headers = {}
        for item in (stream_url.split('|')[1]).split('&'):
            results = re.findall(r'(.+?)=(.*)', item)
            header = results[0][0]
            value = results[0][1]
            headers[header] = urllib.unquote_plus(value)
    except:
        headers = {}
    common.logger.log_debug('Setting Headers on UrlOpen: %s' % (headers))
    
    try:
        msg = ''
        request = urllib2.Request(stream_url.split('|')[0], headers=headers)
        #  set urlopen timeout to 3 seconds
        http_code = urllib2.urlopen(request, timeout=3).getcode()
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            # treat an unhandled url type as success
            if 'unknown url type' in str(e.reason).lower():
                return True
            else:
                msg = e.reason
                
        if isinstance(e, urllib2.HTTPError):
            http_code = e.code
        else:
            http_code = 600
        if not msg: msg = str(e)
    except Exception as e:
        http_code = 601
        msg = str(e)
        
    if int(http_code) >= 400:
        common.logger.log_warning('Stream UrlOpen Failed: Url: %s HTTP Code: %s Msg: %s' % (stream_url, http_code, msg))
    return int(http_code) < 400

blacklist = read_blacklist()