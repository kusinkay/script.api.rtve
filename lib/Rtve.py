import json
import xbmc, xbmcplugin
from utils import getHtml, buildUrl
from xbmcgui import ListItem


class Rtve:
	
	def __init__(self, media, base_url):
		self.endpoint = 'http://www.rtve.es/api/'
		self.size=20 #60 is the max allowed by api.rtve.es
		self.page=1
		self.media = media
		self.debug = True
		self.base_url = base_url
		self.log("welcome Rtve")
		
	def get_media(self):
		self.log('HOLA')
		return self._get_content('medios.json')
       
	def get_channels(self, media=None):
		if media==None:
			media=self.media
		url = 'medios/' + str(media) + '/cadenas.json'
		result = []
		source = self._get_content(url)['items']
		for item in source:
			li = ListItem()
			li.setLabel(item.get('title', None))
			n = Node(li, self._build_url({'action':'channel','arg_id': item.get('id', None)}))
			result.append(n)
		return result
	
	def get_programs(self, channel, startsWithLetter = None):
		result = []
		letter = ''
		if startsWithLetter!= None:
			letter = "&startsWithLetter=" + startsWithLetter
		source = self._get_content('cadenas/'+ channel + '/programas', letter)
		for item in source['items']:
			li = ListItem()
			li.setLabel(item.get('name', None))
			li.setArt({
				'icon': item.get('logo', None),
				'thumb': item.get('thumbnail', None),
				'poster': item.get('imgPoster', None),
				'fanart': item.get('imgBackground', None)
			})
			if self.media == Media.RADIO:
				li.setInfo('music', {
	                'title': item.get('description', None)
	            })
			n  = Node(li, self._build_url({'action': 'program','arg_id': item.get('id', None)}))
			result.append(n)
		args = {'action': Branch.PROGRAMS, 'arg_id': channel}
		self._add_pager(result, args, source['page'])
			
		return result
	
	def get_audios(self, args):
		url_options          = ')ung-xunil(02%4.91.1F2%tegW=tnegA-resU|'[::-1]

		result = []
		url = args['branch']
		if args['id']!=None:
			url += '/' + args['id']
		if args['ranking']!=Ranking.RECENT:
			url += '/audios/'
		else:
			url += '/'
		if args['ranking']!=None:
			url += args['ranking']
		source = self._get_content(url)
		for item in source['items']:
			audio = item.get('qualities', [])[0].get('filePath')
			audio = audio.replace('://mvod.lvlt.', '://www.')
			audio = audio + url_options
			
			li = ListItem()
			li.setLabel(item.get('longTitle', None))
			li.setArt({
				'icon': item.get('imageSEO', None)
			})
			if self.media == Media.RADIO:
				li.setInfo('music', {
	                'title': item.get('description', None),
	                'duration': item.get('qualities', [])[0].get('duration')/1000,
	                'playcount': item.get('numVisits')
	            })
				li.addStreamInfo('music', {
					'language': item.get('language'),
					'codec': item.get('qualities', [])[0].get('type')
				})
			li.setProperty('IsPlayable', 'true')
			n = Node(li, self._build_url({'action': 'play','stream': audio}))
			result.append(n)
		args = {'action': args['action'], 'arg_id': args['id']}
		self._add_pager(result, args, source['page'])
			
		return result
			
	def get_a_to_z(self, channel):
		result = []
		#TODO parametrizar para programas u otros
		alphabet = [
			('a', 'A - C'),
			('d', 'D - E'),
			('f', 'F - I'),
			('j', 'J - L'),
			('m', 'M - P'),
			('q', 'Q - S'),
			('t', 'T - V'),
			('x', 'X - Z')
		]
		for Key, Value in alphabet:
			l = ListItem();
			l.setLabel(Value)
			n = Node(l, self._build_url({'action':'programs','arg_id': channel, 'start': Key}))
			result.append(n)
		return result
	
	def _add_pager(self, result, args, page):
		if page['totalPages']>1 and page['totalPages']>page['number']:
			li = ListItem()
			li.setLabel(str(page['number']+1) + '/' + str(page['totalPages']))
			args['page'] = page['number']+1
			n  = Node(li, self._build_url(args))
			result.append(n)
	
	
	def _build_url(self, params):
		url = buildUrl(params, self.base_url)
		return url
	
	def _get_content(self, url, params = None):
		if params==None:
			params = ''
		
		self.log('RQ: ' + url)
		url = self.endpoint + url + '?size=' + str(self.size) + '&page=' + str(self.page) +  params
		self.log('RQ: ' + url)
		link = getHtml(url)
		#link = link.decode("ISO-8859-1")
		data =json.loads(link)
		items = data.get('page',{}).get('items', {})
		
		page = data.get('page',{})
		result = {
			'page': {
				'number': page.get('number', None),
				'size': page.get('size', None),
				'offset': page.get('offset', None),
				'total': page.get('total', None),
				'totalPages': page.get('totalPages', None),
				'numElements': page.get('numElements', None)
			},
			'items': items
		}
		
		if items != None:
			return result
		return None
	
	def set_page(self, page):
		self.page = page
	
	def log(self, msg, level=xbmc.LOGDEBUG):
	    if level==xbmc.LOGDEBUG and self.debug==True:
	        xbmc.log("|| Rtve: " + msg, level)

    	

class Node:
	def __init__(self, li, url):
		self.listItem = li
		self.url = url

class Media():
	TV = 850
	RADIO = 851
	WEB = 414

class Branch():
	CHANNELS = "cadenas"
	PROGRAMS = "programas"
	
class Ranking():
	POPULAR = "mas-populares.json"
	MOREVISITED = "mas-vistos.json"
	RECENT = "audios.json"