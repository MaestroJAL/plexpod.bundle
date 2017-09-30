ART = 'art-default.jpg'
ICON = 'icon-default.png'
PLUS = 'plus.png'
MINUS = 'minus.png'
HUGEM = 'hugem.png'

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'PlexPod'
	TrackObject.thumb = R(ICON)

	# Initialize Dict if it does not exist yet
	if not Dict['feed']:
		Dict['feed'] = []

####################################################################################################     
@handler('/music/PlexPod', 'PlexPod', thumb=ICON, art=ART)
def MainMenu(nameofshow=None, urlofshow=None, artofshow=None):

	oc = ObjectContainer()

	if (nameofshow != None) and (urlofshow != None) and (artofshow != None):

		ugly = [nameofshow, urlofshow, artofshow]

		if ugly not in Dict['feed']:
			Dict['feed'].append(ugly)

		Dict['feed'].sort(key=lambda x: x[0])
		oc = ObjectContainer()
		Dict.Save()

	for x in Dict['feed']:

		try:
			oc.add(DirectoryObject(key=Callback(SecondMenu, title=x[1], offset=0), title=x[0], thumb = x[2]))
		except:
			pass

	oc.add(InputDirectoryObject(key=Callback(Search), title="Add a Podcast", thumb = R(PLUS)))
	oc.add(DirectoryObject(key=Callback(DelMenu, title=None), title="Delete a Podcast", thumb = R(MINUS)))

	return oc

####################################################################################################
def DelMenu(title):

	oc = ObjectContainer()

	try:	
		Dict['feed'].remove(title)
		Dict.Save()
	except:
		pass

	for x in Dict['feed']:

		try:
			oc.add(DirectoryObject(key=Callback(DelMenu, title=x), title=x[0], thumb = x[2]))
		except:
			pass

	oc.add(DirectoryObject(key=Callback(MainMenu), title="Main Menu", thumb = R(HUGEM)))
	return oc

####################################################################################################
def SecondMenu(title, offset):

	oc = ObjectContainer()
	feed = RSS.FeedFromURL(title)

	if Prefs["Sortord"]:
		mal = 1
	else:
		mal = -1

	for item in feed.entries[::mal][offset:offset+26]:

		url = item.enclosures[0]['url']
		showtitle = item.title
		summary = String.StripTags(item.summary)

		try:
			image = str(feed.channel.image.url)
			oc.add(CreateTrackObject(url=url, title=showtitle, thumb=image, summary=summary))
			oc.art=image
			oc.title1=feed.channel.title
		except:
			pass

	oc.add(DirectoryObject(key=Callback(SecondMenu, title=title, offset=offset+26), title="Next Page", thumb = image))
	return oc

####################################################################################################
def CreateTrackObject(url, title, thumb, summary, include_container=False, includeBandwidths=0):

	if url.endswith('.mp3'):
		container = Container.MP3
		audio_codec = AudioCodec.MP3
	else:
		container = Container.MP4
		audio_codec = AudioCodec.AAC

	track_object = TrackObject(
		key = Callback(CreateTrackObject, url=url, title=title, thumb=thumb, summary=summary, include_container=True),
		rating_key = url,
		title = title,
		thumb = thumb,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=url)
				],
				container = container,
				audio_codec = audio_codec,
				audio_channels = 2
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[track_object])
	else:
		return track_object

####################################################################################################
def Search(query):

	oc = ObjectContainer()
	neary = str(query.replace (" ", "+"))
	pod = JSON.ObjectFromURL("https://itunes.apple.com/search?term=%s&entity=podcast&limit=25" % neary)['results']

	for x in pod:
		oc.add(DirectoryObject(key=Callback(MainMenu, urlofshow=[x][0]['feedUrl'], nameofshow=[x][0]['collectionName'], artofshow=[x][0]['artworkUrl600']), title=[x][0]['collectionName'], thumb=[x][0]['artworkUrl600']))

	return oc
