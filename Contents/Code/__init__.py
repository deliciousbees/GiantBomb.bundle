API_PATH = 'http://www.giantbomb.com/api'
API_KEY = '70d735e54938286d6d9142727877107ced20e5ff'

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

@handler('/video/unofficialgiantbomb', 'Unofficial Giant Bomb')
def MainMenu(cat_id=None, query=None, offset=0):
	oc = ObjectContainer()

	# Live stream
	try:
		response = JSON.ObjectFromURL(API_PATH + '/chats/?api_key=' + ApiKey() + '&format=json')
	except Ex.HTTPError as detail:
		Log.Error("Could not load list of live streams (server returned HTTP %d)", detail.code)
	else:
		oc.add(
			DirectoryObject(
				key='/video/unofficialgiantbomb/shows',
				title='[All Shows]',
				summary='Explore Giant Bomb content, organized by show.',
				thumb=R(ICON),
				art=R(ART)
			)
		)

		chats = response['results']

		for chat in chats:
			if chat['channel_name'] is not None:
				url = 'http://www.twitch.tv/' + chat['channel_name']
				try:
					thumb = chat['image']['super_url']
				except:
					thumb = R(ICON)

				oc.add(
					VideoClipObject(
						url=url,
						title='LIVE: ' + chat['title'],
						summary=chat['deck'],
						source_title='Twitch.tv',
						thumb=thumb,
						art=R(ART),
						rating_key=chat['channel_name']
					)
				)



	try:
		result = JSON.ObjectFromURL('%s/videos/?api_key=%s&format=json&offset=0' % (API_PATH, ApiKey()))
	except Ex.HTTPError as detail:
		Log.Error("Could not load list of latest videos (server returned HTTP %d)", detail.code)
	else:
		videos = result['results']

		for vid in videos:
			oc.add(
				VideoClipObject(
					url=vid['api_detail_url'] + '?api_key=' + ApiKey() + '&format=json',
					title=vid['name'],
					summary=vid['deck'],
					thumb=vid['image']['super_url'],
					art=R(ART),
					rating_key=vid['id']
				)
			)

		listedSoFar = result['offset'] + result['number_of_page_results']
		if listedSoFar < result['number_of_total_results']:
			oc.add(
				NextPageObject(
					key=Callback(Videos, cat_id=cat_id, query=query, offset=listedSoFar),
					title="Next Page"
				)
			)

	return oc


@route('/video/unofficialgiantbomb/shows', allow_sync=True)
def AllShows():
	oc = ObjectContainer()
	try:
		categories = JSON.ObjectFromURL(API_PATH + '/video_types/?api_key=' + ApiKey() + '&format=json')['results']
	except Ex.HTTPError as detail:
		Log.Error("Could not load list of video shows (server returned HTTP %d)", detail.code)
	else:
		for cat in categories:
			# Endurance Runs
			if cat['id'] == 5:
				route = '/video/unofficialgiantbomb/erun'
			else:
				route = '/video/unofficialgiantbomb/videos/?cat_id=' + str(cat['id'])

			oc.add(
				DirectoryObject(
					key=route,
					title=cat['name'],
					summary=cat['deck'],
					thumb=R(ICON),
					art=R(ART)
				)
			)

		oc.add(
			PrefsObject(
				title = L('Preferences')
			)
		)

		oc.add(
			InputDirectoryObject(
				key=Callback(Videos, cat_id=None),
				title='Search Videos',
				summary='Tired of pagination? Use this new fangled search thing to find the videos you\'re looking for!',
				thumb=R(ICON),
				prompt='Enter the video title'
			)
		)

	return oc

@route('/video/unofficialgiantbomb/erun', allow_sync=True)
def EnduranceRunMenu():
	oc = ObjectContainer(
		objects = [
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=5&query=Chrono%20Trigger',
				title='Chrono Trigger',
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=5&query=Deadly%20Premonition',
				title='Deadly Premonition',
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=5&query=Persona%204',
				title='Persona 4',
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=5&query=Matrix%20Online',
				title='The Matrix Online: Not Like This',
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=10&query=Breaking%20Brad%3A%20Demon%27s%20Souls',
				title="Breaking Brad: Demon's Souls (Premium)",
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=10&query=Load%20Our%20Last%20Souls',
				title="Load Our Last Souls (Premium)",
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=10&query=Metal%20Gear%20Scanlon',
				title="Metal Gear Scanlon (Premium)",
				art=R(ART)
			),
			DirectoryObject(
				key='/video/unofficialgiantbomb/videos/?cat_id=10&query=Bradley%20May%20Cry',
				title="Bradley May Cry (Premium)",
				art=R(ART)
			)
		]
	)

	return oc

@route('/video/unofficialgiantbomb/videos', allow_sync=True)
def Videos(cat_id=None, query=None, offset=0):
	oc = ObjectContainer()

	try:
		if cat_id and query: # for endurance runs
			result = JSON.ObjectFromURL('%s/videos/?api_key=%s&video_type=%s&format=json&sort=publish_date:asc&filter=name:%s&offset=%s' % (API_PATH, ApiKey(), cat_id, query, offset))
		elif cat_id: # for categories
			result = JSON.ObjectFromURL('%s/videos/?api_key=%s&video_type=%s&format=json&offset=%s' % (API_PATH, ApiKey(), cat_id, offset))
		elif query: # for search
			result = JSON.ObjectFromURL('%s/videos/?api_key=%s&format=json&filter=name:%s&offset=%s' % (API_PATH, ApiKey(), query, offset))
		else: # catch all
			result = JSON.ObjectFromURL('%s/videos/?api_key=%s&format=json&offset=%s' % (API_PATH, ApiKey(), offset))
	except Ex.HTTPError as detail:
		Log.Error("Could not load list of videos for category '%d' and query '%s' (server returned HTTP %d)", cat_id, query, detail.code)
	else:
		videos = result['results']

		for vid in videos:
			oc.add(
				VideoClipObject(
					url=vid['api_detail_url'] + '?api_key=' + ApiKey() + '&format=json',
					title=vid['name'],
					summary=vid['deck'],
					thumb=vid['image']['super_url'],
					art=R(ART),
					rating_key=vid['id']
				)
			)

		listedSoFar = result['offset'] + result['number_of_page_results']
		if listedSoFar < result['number_of_total_results']:
			oc.add(
				NextPageObject(
					key=Callback(Videos, cat_id=cat_id, query=query, offset=listedSoFar),
					title="Next Page"
				)
			)

	return oc

def ApiKey():
	if Prefs['apiKey']:
		key = Prefs['apiKey']
	else:
		key = API_KEY

	return key
