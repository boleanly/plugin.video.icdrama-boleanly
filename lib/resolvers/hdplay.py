import re

import urlresolver
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from urlresolver.plugins.lib import helpers

import xbmc

class Hdplay(UrlResolver):
    name = 'Hdplay'
    domains = ['hdplay.se']
    pattern = '(?://|\.)(hdplay\.se)/(.+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}
        
    
    def get_media_url(self, host, media_id):
        """
        source scraping to get resolved uri goes here
        return |str| : resolved/playable uri or raise ResolverError
        ___
        helpers.get_media_url result_blacklist: |list of str| : list of strings to blacklist in source results
        """

        url = self.get_url(host, media_id)
        
        #Urlresolver fails to extract header with hls=1
        if '?hls=1' in url:
            url = url.replace('?hls=1','') 
        
        headers = self.headers
        headers['Referer'] = url
        headers['Origin'] = 'http://hdplay.se'
        
        html = common.Net().http_GET(url, headers=self.headers).content
        
        results = re.findall(r'file: *"(.*?)" *,', html)
        media_url = results[0] + '|'
        
        for header in headers:
            media_url = media_url + header + '=' + headers[header] + '&'
        media_url = media_url[0:-2] #Removes trailing &
        
        return media_url

    def get_url(self, host, media_id):
        """
        return |str| : uri to be used by get_media_url
        ___
        _default_get_url template: |str| : 'http://{host}/embed-{media_id}.html'
        """
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}')

        
    @classmethod
    def _is_enabled(cls):
        return True
