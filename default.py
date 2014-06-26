### ############################################################################################################
###	#	
### # Project: 			#		Infowars.com Plugin
###	#	
### ############################################################################################################
### ############################################################################################################
### Plugin Settings ###

def ps(x):
	return {
		'__plugin__': 					"Infowars"
		,'__authors__': 				"Prafit"
		,'__credits__': 				""
		,'_addon_id': 					"plugin.video.infowars"
		,'_plugin_id': 					"plugin.video.infowars"
		,'_domain_url': 				"infowars.com"
		,'_database_name': 			"infowars"
		,'_addon_path_art': 		"art"
		,'special.home.addons': 'special:'+os.sep+os.sep+'home'+os.sep+'addons'+os.sep
		,'special.home': 				'special:'+os.sep+os.sep+'home'
		,'content_movies': 			"movies"
		,'content_tvshows': 		"tvshows"
		,'content_episodes': 		"episodes"
		,'content_links': 			"list"
		,'common_word': 				"Anime"
		,'common_word2': 				"Watch"
		,'default_art_ext': 		'.png'
		,'default_cFL_color': 	'green'
		,'cFL_color': 					'lime'
		,'cFL_color2': 					'yellow'
		,'cFL_color3': 					'red'
		,'cFL_color4': 					'grey'
		,'cFL_color5': 					'white'
		,'cFL_color6': 					'blanchedalmond'
		,'default_section': 		'movies'
		,'section.wallpaper':		'wallpapers'
		,'section.movie': 			'movies'
		,'section.trailers':		'trailers'
		,'section.trailers.popular':			'trailerspopular'
		,'section.trailers.releasedate':	'trailersreleasedate'
		,'section.users':				'users'
		,'section.tv': 					'tv'
	}[x]



### ##### /\ ##### Plugin Settings ###
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Imports #####
##Notes-> Some Default imports so that you can use the functions that are available to them.
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
import urllib,urllib2,re,os,sys,htmllib,string,StringIO,logging,random,array,time,datetime
import plugintools
import copy
import HTMLParser, htmlentitydefs
##Notes-> Common script.module.___ that is used by many to resolve urls of many video hosters.
## ##Notes-> Sometimes you can will use this method.
## ##Notes-> Sometimes you'll have to parse out the direct/playabe url of a video yourself.
import urlresolver
##Notes-> I often use this in the cache-method for addon favorites.
try: 		import StorageServer
except: import storageserverdummy as StorageServer
##Notes-> t0mm0's common module for addon and net functions.
## ##Notes-> I sometimes toss a copy of these modules into my addon folders just incase they dont have them installed... even if that's not a great practice.  I use them a LOT, so in this case it's a habbit.
try: 		from t0mm0.common.addon 				import Addon
except: from t0mm0_common_addon 				import Addon
try: 		from t0mm0.common.net 					import Net
except: from t0mm0_common_net 					import Net

##Notes-> modules to import if you play to use SQL DB stuff in your addon.
try: 		from sqlite3 										import dbapi2 as sqlite; print "Loading sqlite3 as DB engine"
except: from pysqlite2 									import dbapi2 as sqlite; print "Loading pysqlite2 as DB engine"


##Notes-> how to import another .py file from your addon's folder.  Example: to import "config.py" you'd use: "from config import *"
#from teh_tools 		import *
#from config 			import *

##### /\ ##### Imports #####

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
__plugin__=ps('__plugin__'); 
__authors__=ps('__authors__'); 
__credits__=ps('__credits__'); 
_addon_id=ps('_addon_id'); 
_domain_url=ps('_domain_url'); 
_database_name=ps('_database_name'); 
_plugin_id=ps('_addon_id')
_database_file=os.path.join(xbmc.translatePath("special://database"),ps('_database_name')+'.db'); 
### 
_addon=Addon(ps('_addon_id'), sys.argv); addon=_addon; _plugin=xbmcaddon.Addon(id=ps('_addon_id')); cache=StorageServer.StorageServer(ps('_addon_id'))
### 
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##Notes-> I placed these here so that they would be before the stuff that they use during setup.
def addst(r,s=''): return _addon.get_setting(r)   ## Get Settings
def addpr(r,s=''): return _addon.queries.get(r,s) ## Get Params
def tfalse(r,d=False): ## Get True / False
	if   (r.lower()=='true' ): return True
	elif (r.lower()=='false'): return False
	else: return d
##### Paths #####
### # ps('')
_addonPath	=xbmc.translatePath(_plugin.getAddonInfo('path'))
_artPath		=xbmc.translatePath(os.path.join(_addonPath,ps('_addon_path_art')))
_datapath 	=xbmc.translatePath(_addon.get_profile()); _artIcon		=_addon.get_icon(); _artFanart	=_addon.get_fanart()
##### /\ ##### Paths #####
##### Important Functions with some dependencies #####
def art(f,fe=ps('default_art_ext')): return xbmc.translatePath(os.path.join(_artPath,f+fe)) ### for Making path+filename+ext data for Art Images. ###
##### /\ ##### Important Functions with some dependencies #####
##### Settings #####
_setting={}; 
##Notes-> options from the settings.xml file.
_setting['enableMeta']	=	_enableMeta			=tfalse(addst("enableMeta"))
_setting['debug-enable']=	_debugging			=tfalse(addst("debug-enable")); _setting['debug-show']	=	_shoDebugging		=tfalse(addst("debug-show"))
_setting['label-empty-favorites']=tfalse(addst('label-empty-favorites'))
##Notes-> some custom settings.
#_setting['meta.movie.domain']=ps('meta.movie.domain'); _setting['meta.movie.search']=ps('meta.movie.search')
#_setting['meta.tv.domain']   =ps('meta.tv.domain');    _setting['meta.tv.search']   =ps('meta.tv.search')
#_setting['meta.tv.page']=ps('meta.tv.page'); _setting['meta.tv.fanart.url']=ps('meta.tv.fanart.url'); 
#_setting['meta.tv.fanart.url2']=ps('meta.tv.fanart.url2'); 
##### /\ ##### Settings #####
##### Variables #####
_default_section_=ps('default_section'); net=Net(); DB=_database_file; BASE_URL=_domain_url;
### ############################################################################################################
##Notes-> Some important time saving functions to shorten your work later.
#def eod(): _addon.end_of_directory() ## used at the end of a folder listing to print the list to the screen.
def eod(): xbmcplugin.endOfDirectory(int(sys.argv[1]))
def myNote(header='',msg='',delay=5000,image=''): _addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def cFL( t,c=ps('default_cFL_color')): return '[COLOR '+c+']'+t+'[/COLOR]' ### For Coloring Text ###
def cFL_(t,c=ps('default_cFL_color')): return '[COLOR '+c+']'+t[0:1]+'[/COLOR]'+t[1:] ### For Coloring Text (First Letter-Only) ###
def notification(header="", message="", sleep=5000 ): xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i)" % ( header, message, sleep ) )
def WhereAmI(t): ### for Writing Location Data to log file ###
	if (_debugging==True): print 'Where am I:  '+t
def deb(s,t): ### for Writing Debug Data to log file ###
	if (_debugging==True): print s+':  '+t
def debob(t): ### for Writing Debug Object to log file ###
	if (_debugging==True): print t
def nolines(t):
	it=t.splitlines(); t=''
	for L in it: t=t+L
	t=((t.replace("\r","")).replace("\n",""))
	return t
def isPath(path): return os.path.exists(path)
def isFile(filename): return os.path.isfile(filename)
def askSelection(option_list=[],txtHeader=''):
	if (option_list==[]): 
		if (debugging==True): print 'askSelection() >> option_list is empty'
		return None
	dialogSelect = xbmcgui.Dialog();
	index=dialogSelect.select(txtHeader, option_list)
	return index
def iFL(t): return '[I]'+t+'[/I]' ### For Italic Text ###
def bFL(t): return '[B]'+t+'[/B]' ### For Bold Text ###
def _FL(t,c,e=''): ### For Custom Text Tags ###
	if (e==''): d=''
	else: d=' '+e
	return '['+c.upper()+d+']'+t+'[/'+c.upper()+']'

#Metahandler
try: 		from script.module.metahandler 	import metahandlers
except: from metahandler 								import metahandlers
grab=metahandlers.MetaData(preparezip=False)
def GRABMETA(name,types):
	type=types
	EnableMeta=tfalse(addst("enableMeta"))
	if (EnableMeta==True):
		if ('movie' in type):
			### grab.get_meta(media_type, name, imdb_id='', tmdb_id='', year='', overlay=6)
			meta=grab.get_meta('movie',name,'',None,None,overlay=6)
			infoLabels={'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],'director': meta['director'],'cast': meta['cast'],'backdrop': meta['backdrop_url'],'backdrop_url': meta['backdrop_url'],'tmdb_id': meta['tmdb_id'],'year': meta['year'],'votes': meta['votes'],'tagline': meta['tagline'],'premiered': meta['premiered'],'trailer_url': meta['trailer_url'],'studio': meta['studio'],'imdb_id': meta['imdb_id'],'thumb_url': meta['thumb_url']}
			#infoLabels={'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url'],'backdrop_url': meta['backdrop_url'],'tmdb_id': meta['tmdb_id'],'year': meta['year']}
		elif ('tvshow' in type):
			meta=grab.get_meta('tvshow',name,'','',None,overlay=6)
			#print meta
			infoLabels={'rating': meta['rating'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],'backdrop_url': meta['backdrop_url'],'status': meta['status'],'premiered': meta['premiered'],'imdb_id': meta['imdb_id'],'tvdb_id': meta['tvdb_id'],'year': meta['year'],'imgs_prepacked': meta['imgs_prepacked'],'overlay': meta['overlay'],'duration': meta['duration']}
			#infoLabels={'rating': meta['rating'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],'backdrop_url': meta['backdrop_url'],'status': meta['status']}
		else: infoLabels={}
	else: infoLabels={}
	return infoLabels
### ############################################################################################################
### ############################################################################################################
##### Queries #####
_param={}
##Notes-> add more here for whatever params you want to use then you can just put the tagname within _param[''] to fetch it later.  or you can use addpr('tagname','defaultvalue').
_param['mode']=addpr('mode',''); _param['url']=addpr('url',''); _param['pagesource'],_param['pageurl'],_param['pageno'],_param['pagecount']=addpr('pagesource',''),addpr('pageurl',''),addpr('pageno',0),addpr('pagecount',1)
_param['img']=addpr('img',''); _param['fanart']=addpr('fanart',''); _param['thumbnail'],_param['thumbnail'],_param['thumbnail']=addpr('thumbnail',''),addpr('thumbnailshow',''),addpr('thumbnailepisode','')
_param['section']=addpr('section','movies'); _param['title']=addpr('title',''); _param['year']=addpr('year',''); _param['genre']=addpr('genre','')
_param['by']=addpr('by',''); _param['letter']=addpr('letter',''); _param['showtitle']=addpr('showtitle',''); _param['showyear']=addpr('showyear',''); _param['listitem']=addpr('listitem',''); _param['infoLabels']=addpr('infoLabels',''); _param['season']=addpr('season',''); _param['episode']=addpr('episode','')
_param['pars']=addpr('pars',''); _param['labs']=addpr('labs',''); _param['name']=addpr('name',''); _param['thetvdbid']=addpr('thetvdbid','')
_param['plot']=addpr('plot',''); _param['tomode']=addpr('tomode',''); _param['country']=addpr('country','')
_param['thetvdb_series_id']=addpr('thetvdb_series_id',''); _param['dbid']=addpr('dbid',''); _param['user']=addpr('user','')
_param['subfav']=addpr('subfav',''); _param['episodetitle']=addpr('episodetitle',''); _param['special']=addpr('special',''); _param['studio']=addpr('studio','')
##Notes-> another way to do it which my custom function just shortens down.
#_param['']=_addon.queries.get('','')

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Player Functions #####
def PlayURL(url):
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	try: _addon.resolve_url(url)
	except: t=''
	try: play.play(url)
	except: t=''
	
def play(params):
    plugintools.play_resolved_url( params.get("url") )	
    
### ############################################################################################################
### ############################################################################################################

def Menu_MainMenu(): #The Main Menu
	WhereAmI('@ the Main Menu')
	_addon.add_directory({'mode': 'PlayURL','url':'http://cdn.rbm.tv:1935/rightbrainmedia-originpull-2/_definst_/mp4:247daily2/playlist.m3u8'},{'title':  cFL_('Infowars.com Live Video(Loops After Airing)',ps('cFL_color'))},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'http://www.infowars.com/stream.pls'},{'title':  cFL_('Infowars.com Live Audio(Loops After Airing)',ps('cFL_color'))},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'NightlyNewsSubMenu','title':'Infowars Nightly News'},{'title':  cFL_('Infowars Nightly News',ps('cFL_color3'))},is_folder=True,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'ClipsSubMenu','title':'Infowars Nightly News'},{'title':  cFL_('Infowars Clips',ps('cFL_color3'))},is_folder=True,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'DocSubMenu','title':'Acclaimed Documentaries'},{'title':  cFL_('Acclaimed Documentaries',ps('cFL_color6'))},is_folder=True,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'HistoricShowsSubMenu','title':'Historic Shows(video)'},{'title':  cFL_('Historic Shows(Video)',ps('cFL_color2'))},is_folder=True,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'HistoricShowsAudioSubMenu','title':'Historic Shows(video)'},{'title':  cFL_('Historic Shows(Audio)',ps('cFL_color2'))},is_folder=True,img=_artIcon,fanart=_artFanart)
	eod()


def Documentary_Sub_Menu(title=''): #The Main Menu
	WhereAmI('@ Documentaries')
	#mode left blank for main menu.
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=eAaQNACwaLw'},{'title':'The Obama Deception'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=t-yscpNIxjI'},{'title':'The 9/11 Chronicles Part One: Truth Rising'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=x-CrNlilZho'},{'title':'End Game'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=vrXgLhkv21Y'},{'title':'TerrorStorm'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=BqxUFVsmPcQ'},{'title':'Martial Law: 9/11 Rise of the Police State'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=OVMyH8eOHKs'},{'title':'911: The Road to Tyranny'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=nxllWCPw6sU'},{'title':'Matrix of Evil'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=vsKVyhuBf3c'},{'title':'America Destroyed by Design'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=1Fr5QC6u2EQ'},{'title':'American Dictators'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=FVtEvplXMLs'},{'title':'Dark Secrets: Inside Bohemian Grove'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=VhlRIH9iPD4'},{'title':'The Order of Death'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=GKty_3IlXOc'},{'title':'Police State 2000 Martial Law Posse Comitatus'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=4Cf_tZzABgE'},{'title':'Police State 2: The Takeover'},is_folder=False,img=_artIcon,fanart=_artFanart)
	_addon.add_directory({'mode': 'PlayURL','url':'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=K4RWRm-bgv8'},{'title':'Police State 3: Total Enslavement'},is_folder=False,img=_artIcon,fanart=_artFanart)
	eod() #Ends the directory listing and prints it to the screen.  if you dont use eod() or something like it, the menu items won't be put to the screen.

def Nightly_News_Sub_Menu(title=''): #The Main Menu
    WhereAmI('@ Nightly News')
    url = 'http://gdata.youtube.com/feeds/api/users/ConspiracyScope/uploads?start-index=1&max-results=30'
    response = urllib2.urlopen(url)
    if response and response.getcode() == 200:
        content = response.read()
        videos= plugintools.find_multiple_matches(content,"<entry>(.*?)</entry>")
        for entry in videos:
            title = plugintools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
            plot = plugintools.find_single_match(entry,"<media\:descriptio[^>]+>([^<]+)</media\:description>")
            thumbnail = plugintools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
            video_id = plugintools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([^\&]+)\&").replace("&amp;","&")
            url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid="+video_id
            if title.find('Nightly News') > -1:
                print title
                print plot
                print thumbnail
                print url
                plugintools.add_item( action="play" , title=title , plot=plot , url=url ,thumbnail=thumbnail , folder=False )
    else:
        util.showError(ADDON_ID, 'Could not open URL %s to create menu' % (url))

    eod()
	
def Historic_Shows_Sub_Menu(title=''): #The Main Menu
    WhereAmI('@ Historic Shows Video')
    url = 'http://gdata.youtube.com/feeds/api/users/ConspiracyScope/uploads?start-index=1&max-results=30'
    response = urllib2.urlopen(url)
    if response and response.getcode() == 200:
        content = response.read()
        videos= plugintools.find_multiple_matches(content,"<entry>(.*?)</entry>")
        for entry in videos:
            title = plugintools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
            plot = plugintools.find_single_match(entry,"<media\:descriptio[^>]+>([^<]+)</media\:description>")
            thumbnail = plugintools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
            video_id = plugintools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([^\&]+)\&").replace("&amp;","&")
            url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid="+video_id
            if title.find('Alex Jones Show') > -1:
                if title.find('Podcast') == -1:
                    plugintools.add_item( action="play" , title=title , plot=plot , url=url ,thumbnail=thumbnail , folder=False )
    else:
        util.showError(ADDON_ID, 'Could not open URL %s to create menu' % (url))

    eod()	
	
def Clips_Sub_Menu(title=''): #The Main Menu
    WhereAmI('@ Clips')
    url = 'http://gdata.youtube.com/feeds/api/users/TheAlexJonesChannel/uploads?start-index=1&max-results=30'
    response = urllib2.urlopen(url)
    if response and response.getcode() == 200:
        content = response.read()
        videos= plugintools.find_multiple_matches(content,"<entry>(.*?)</entry>")
        for entry in videos:
            title = plugintools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
            plot = plugintools.find_single_match(entry,"<media\:descriptio[^>]+>([^<]+)</media\:description>")
            thumbnail = plugintools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
            video_id = plugintools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([^\&]+)\&").replace("&amp;","&")
            url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid="+video_id
            plugintools.add_item( action="play" , title=title , plot=plot , url=url ,thumbnail=thumbnail , folder=False )
    else:
        util.showError(ADDON_ID, 'Could not open URL %s to create menu' % (url))

    eod()

def Historic_Shows_Audio_Sub_Menu(title=''): #The Main Menu
    WhereAmI('@ Historic Audio Shows')
    # url = 'http://xml.nfowars.net/Alex.rss'
    # response = urllib2.urlopen(url)
    # if response and response.getcode() == 200:
        # content = response.read()
        # videos= plugintools.find_multiple_matches(content,"<item>(.*?)</item>")
        # for entry in videos:
            # title = plugintools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
            # plot = plugintools.find_single_match(entry,"<descriptio[^>]+>([^<]+)</description>")
            # url = plugintools.find_single_match(entry,"<gui[^>]+>([^<]+)</guid>")
            # plugintools.add_item( action="mp3play" , title=title , plot=plot , url=url ,thumbnail=_artIcon , folder=False )
    # else:
        # util.showError(ADDON_ID, 'Could not open URL %s to create menu' % (url))

    # eod()	
    WhereAmI('@ Nightly News')
    url = 'http://gdata.youtube.com/feeds/api/users/ConspiracyScope/uploads?start-index=1&max-results=30'
    response = urllib2.urlopen(url)
    if response and response.getcode() == 200:
        content = response.read()
        videos= plugintools.find_multiple_matches(content,"<entry>(.*?)</entry>")
        for entry in videos:
            title = plugintools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
            plot = plugintools.find_single_match(entry,"<media\:descriptio[^>]+>([^<]+)</media\:description>")
            thumbnail = plugintools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
            video_id = plugintools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([^\&]+)\&").replace("&amp;","&")
            url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid="+video_id
            if title.find('Alex Jones Show') > -1:
                if title.find('Podcast') > -1:
                    plugintools.add_item( action="play" , title=title , plot=plot , url=url ,thumbnail=thumbnail , folder=False )
    else:
        util.showError(ADDON_ID, 'Could not open URL %s to create menu' % (url))

    eod()
    
    
def check_mode(mode=''):
	WhereAmI('@ Checking Mode')
	deb('Mode',mode)
	if (mode=='') or (mode=='main') or (mode=='MainMenu'):  Menu_MainMenu() ## Default Menu
	elif (mode=='PlayURL'): 							PlayURL(_param['url']) ## Play Video
	elif (mode=='DocSubMenu'): 						Documentary_Sub_Menu(_param['title']) ## Play Video
	elif (mode=='ClipsSubMenu'): 						Clips_Sub_Menu(_param['title']) ## Play Video
	elif (mode=='NightlyNewsSubMenu'): 						Nightly_News_Sub_Menu(_param['title']) ## Play Video
	elif (mode=='HistoricShowsSubMenu'): 						Historic_Shows_Sub_Menu(_param['title']) ## Play Video
	elif (mode=='HistoricShowsAudioSubMenu'): 						Historic_Shows_Audio_Sub_Menu(_param['title']) ## Play Video
	elif (mode=='Settings'): 							_addon.addon.openSettings() # Another method: _plugin.openSettings() ## Settings for this addon.
	elif (mode=='ResolverSettings'): 			urlresolver.display_settings()  ## Settings for UrlResolver script.module.
	#
	#
	#elif (mode=='YourMode'): 						YourFunction(_param['url'])
	#
	#
	#
	else: myNote(header='Mode:  "'+mode+'"',msg='[ mode ] not found.'); Menu_MainMenu() ## So that if a mode isn't found, it'll goto the Main Menu and give you a message about it.


deb('param >> title',_param['title'])
deb('param >> url',_param['url']) ### Simply Logging the current query-passed / param -- URL
check_mode(_param['mode']) ### Runs the function that checks the mode and decides what the plugin should do. This should be at or near the end of the file.
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
