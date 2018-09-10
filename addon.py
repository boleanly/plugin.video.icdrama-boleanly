import sys
from urlparse import parse_qsl
from urllib import unquote
from lib import actions
from lib import cache
import xbmcaddon
'''
title_language = xbmcaddon.Addon().getSetting('title_language')
language_override = xbmcaddon.Addon().getSetting('language_override')

addon_settings = {}
try:
    addon_settings = cache.get('addon_settings')
    print("Icdrama: " + "Obtained addon settings")
    print("Icdrama: " + str(addon_settings))

except:
    addon_settings = {'title_language': title_language, 'language_override': language_override}
    cache.put('addon_settings', addon_settings)
    print("Icdrama: " + "Inserted addon settings")

if addon_settings['title_language'] != title_language or addon_settings['language_override'] != language_override:
    cache.reset_cache()
    print("Icdrama: " + "Reset cache")
    addon_settings = {'title_language': title_language, 'language_override': language_override}
    cache.put('addon_settings', addon_settings)
'''
if __name__ == '__main__':    
    qs = sys.argv[2]
    #print("Icdrama: " + str(sys.argv))

    kargs = dict((k, unquote(v))for k, v in parse_qsl(qs.lstrip('?')))
    #print("Icdrama: " + str(kargs))
    
    action_name = kargs.pop('action', 'index') # popped
    
    if action_name in actions.actions:
        action_func = getattr(actions, action_name)
        action_func(**kargs)
    else:
        raise Exception('Invalid action: %s' % action_name)
