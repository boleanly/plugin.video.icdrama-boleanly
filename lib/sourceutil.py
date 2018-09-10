import re
import urllib2
import urllib
from urlresolver import common
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
        while not test_stream(source) and index < len(sources):
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