from bs4 import BeautifulSoup
import urlresolver
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from lib import common as cmn
import lib.localizer as lc


loc = lc.getLocalizer()

class Icdrama(UrlResolver):
    name = 'Icdrama'
    domains = [ 'icdrama.se' ]
    pattern = '(?://|\.)(icdrama\.se)/(.+)'


    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}


    def get_media_url(self, host, media_id):
        try:
            weburl = self.get_url(host, media_id)
            html   = self.net.http_GET(weburl, headers=self.headers).content
            
            iframe = BeautifulSoup(html, 'html5lib').find('iframe')
            if iframe:
                return urlresolver.resolve(iframe['src'])
            else:
                cmn.popup(loc.getLocalizedString(33305))
                return ''
                
        except Exception as e:
            if 'No link selected' in str(e):
                return ''
            raise ResolverError('Icdrama resolver: ' + str(e) + ' : ' + self.get_url(host, media_id))


    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}')


    @classmethod
    def _is_enabled(cls):
        return True
