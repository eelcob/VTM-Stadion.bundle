ART 			= 'art-default.jpg'
ICON 			= 'icon-default.png'
ICON_MORE		= 'icon-more.png'
NAME 			= L('Title')

stadionurl = 'http://stadion.vtm.be/'

#REGEX's
IMAGE_REGEX =  Regex('imageUrl: \"(.*?)"')
TITLES_REGEX = Regex('title: \'(.*?)\'')
VIDEOURL_REGEX = Regex('<a href="/(.*?)" class="videozone-item">')

## TODO: 
# - Thumbs fixen, almost there
# - dubbelcheck of functie more niet vervangen kan worden door videos
####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/vtmstadion", MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	DirectoryItem.thumb = R(ICON)

	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0) Gecko/20100101 Firefox/8.0'

####################################################################################################
def MainMenu():
	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(getClubs), title=L('Club')))
	oc.add(DirectoryObject(key = Callback(getCompetitie), title=L('Competition')))
	oc.add(DirectoryObject(key = Callback(getSpeeldag), title=L('Round')))
	
	return oc
		
####################################################################################################
def getClubs():
	oc = ObjectContainer()

	try:
		for team in HTML.ElementFromURL(stadionurl).xpath('//select[@name="teams"]/option'):
			club= team.text
			if club == 'PLOEG':
				continue
			teamid = team.get('value')
		
			speelronde=""
			competitie=""
			oc.add(DirectoryObject(key = Callback(getVideo, teamid=teamid, speelronde=speelronde, competitie=competitie), title=club))
	except:
		Log(L('WebError') + stadionurl)

	return oc

####################################################################################################
def getCompetitie():
	oc = ObjectContainer()
	
	try:
		for competitie in HTML.ElementFromURL(stadionurl).xpath('//select[@name="competition"]/option'):
			comp= competitie.text
			if comp == 'COMPETITIE':
				continue
			competitie = competitie.get('value')
		
			teamid = ""
			speelronde = ""
		
			oc.add(DirectoryObject(key = Callback(getVideo, teamid=teamid, speelronde=speelronde, competitie=competitie), title=comp))
	except:
			Log(L('WebError') + stadionurl)

	return oc

####################################################################################################
def getSpeeldag():
	oc = ObjectContainer()
	
	try:
		for speeldag in HTML.ElementFromURL(stadionurl).xpath('//select[@name="playday"]/option'):
			dag= speeldag.text
			if dag == 'SPEELDAG':
				continue
		
			teamid = ""
			competitie = ""
			speelronde = dag
			title = L('Round') + " " + dag
		
			oc.add(DirectoryObject(key = Callback(getVideo, teamid=teamid, speelronde=speelronde, competitie=competitie), title=title))
	except:
			Log(L('WebError') + stadionurl)

	return oc

####################################################################################################
def getVideo(teamid, speelronde, competitie, page=0):
	oc = ObjectContainer()

	if teamid != "":
		videourl = stadionurl + "?teams=" + teamid
	elif speelronde != "":
		videourl = stadionurl + "?playday=" + speelronde
	elif competitie != "":
		videourl = stadionurl + "?competition=" + competitie
	
	pageurl=str(page)
	if page == "0":
		videourl = videourl
	else:
		videourl = videourl + "&page=" + pageurl

	more = HTML.ElementFromURL(videourl)
	videos = HTTP.Request(videourl, cacheTime=0).content
				
	titles = TITLES_REGEX.findall(videos)
	#images = IMAGES_REGEX.findall(videos)
	video_url = VIDEOURL_REGEX.findall(videos)
	
	for num in range(len(video_url)):
		vid_url = stadionurl + video_url[num] 
		vid_title = titles[num]
		
		## onderstaande niet bekend, check plex manual for wat er wel nog bij kan, zie ook todo
		#summary = video.xpath('.//p[@class="description"]')[0].text
		#date = video.xpath('.//date')[0].text
		#date = Datetime.ParseDate(date).date()

		oc.add(VideoClipObject(
		url = vid_url,
		title = vid_title,
		thumb = Callback(GetThumb, url=vid_url)
		))

	if len(oc) == 0:
		return MessageContainer(L('NoVideo'))
		
	else:
		if len(more.xpath('//li[@class="pager-next"]')) > 0:
			oc.add(DirectoryObject(key=Callback(getVideo, teamid=teamid, speelronde=speelronde, competitie=competitie, page=page+1), title=L('More'), thumb=R(ICON_MORE)))
	
	return oc
	
####################################################################################################
def GetThumb(url):
	try:
		page = HTTP.Request(url, cacheTime=CACHE_1HOUR).content
		image_url = IMAGE_REGEX.findall(page)
		image_url=image_url[0]
		image_url = image_url.replace('\/', '/')
		image = HTTP.Request(image_url, cacheTime=CACHE_1HOUR).content
		return DataObject(image, 'image/jpeg')
	except:
		Log(L('ImageError'))
		return Redirect(R(ICON))