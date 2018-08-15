import re
import os
import os.path as op
import xbmc
import xbmcaddon

def getLocalizer():
    loc = None
    if xbmcaddon.Addon().getSetting('language_override') == '0':
        loc = xbmcaddon.Addon()
    else:
        loc = Localizer()
        
        if xbmcaddon.Addon().getSetting('language_override') == '1':
            loc.setLanguage('English')
        else:
            loc.setLanguage('Chinese (Traditional)')
    return loc

class Localizer():
    _shared_dict = {}
    
    def __init__(self):
        self.__dict__ = self._shared_dict # makes a pseudo singleton
        
        try:
            if self.initialized:
                pass
        except Exception as e:
            if 'instance has no attribute' in str(e):
                self.currLanguage = xbmc.getLanguage()
                self.lang_dir = op.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'language')
                self.languages = {}
                self._parse_langs()
                
                self.initialized = True
            else:
                xbmc.log(str(e), xbmc.LOGERROR)
    
    def setLanguage(self, language):
        self.currLanguage = language
    
    def getLocalizedString(self, id):
        return self.getString(id, self.currLanguage)
    
    def getString(self, id, language):
        for msg_id, id_str, msg in self.languages[language]:
            if msg_id == id or id_str == id:
                return msg.decode('utf-8')
        xbmc.log('Icdrama: Localizer: Localized string not obtained!', xbmc.LOGERROR)
        return ''
    
    def _parse_langs(self):
        for language in os.listdir(self.lang_dir):
            string_file = open(op.join(self.lang_dir, language,'strings.po'), 'r')
            self.languages[language] = []
            
            idnum = None
            idstr = ''
            msg = ''
            
            for line in string_file:
                results = re.findall(u'msgctxt "#(.+?)"|msgid "(.+?)"|msgstr "(.+?)"', line)
                
                if results:
                    if not idnum:
                        idnum = int(results[0][0])
                    elif idstr == '':
                        idstr = results[0][1]
                    else:
                        msg = results[0][2]
                        self.languages[language].append((idnum, idstr, msg))
                        
                        idnum = None
                        idstr = ''