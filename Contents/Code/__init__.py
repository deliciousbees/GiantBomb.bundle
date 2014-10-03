API_PATH = 'http://www.giantbomb.com/api'
API_KEY = '70d735e54938286d6d9142727877107ced20e5ff'

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

@handler('/video/giantbomb', 'Giant Bomb')
def MainMenu():
    oc = ObjectContainer()

    # Live stream
    response = JSON.ObjectFromURL(API_PATH + '/chats/?api_key=' + ApiKey() + '&format=json')
    chats = response['results']

    for chat in chats:
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

    oc.add(
        DirectoryObject(
            key='/video/giantbomb/videos',
            title='Latest',
            summary='Watch the newest stuff.',
            thumb=R(ICON),
            art=R(ART)
        )
    )

    categories = JSON.ObjectFromURL(API_PATH + '/video_types/?api_key=' + ApiKey() + '&format=json')['results']

    for cat in categories:
        # Endurance Runs
        if cat['id'] == 5:
            route = '/video/giantbomb/erun'
        else:
            route = '/video/giantbomb/videos/?cat_id=' + str(cat['id'])

        oc.add(
            DirectoryObject(
                key=route,
                title=cat['name'],
                summary=cat['deck'],
                thumb=R(ICON),
                art=R(ART)
            )
        )

    # oc.add(
    #     SearchDirectoryObject(
    #         identifier="com.plexapp.plugins.giantbombtoo",
    #         title="Search",
    #         summary="Search Giant Bomb videos"
    #     )
    # )

    oc.add(
        PrefsObject(
            title = L('Preferences')
        )
    )

    return oc

@route('/video/giantbomb/erun')
def EnduranceRunMenu():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5&query=Chrono%20Trigger',
                title='Chrono Trigger',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5&query=Deadly%20Premonition',
                title='Deadly Premonition',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5&query=Persona%204',
                title='Persona 4',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5&query=Matrix%20Online',
                title='The Matrix Online: Not Like This',
                art=R(ART)
            )
        ]
    )

    return oc

@route('/video/giantbomb/videos')
def Videos(cat_id=None, query=None, offset=0):
    oc = ObjectContainer()

    if cat_id == '5' and query:
        result = JSON.ObjectFromURL('%s/videos/?api_key=%s&video_type=5&format=json&sort=publish_date:asc&filter=name:%s&offset=%s' % (API_PATH, ApiKey(), query, offset))
    elif cat_id:
        result = JSON.ObjectFromURL('%s/videos/?api_key=%s&video_type=%s&format=json&offset=%s' % (API_PATH, ApiKey(), cat_id, offset))
    else:
        result = JSON.ObjectFromURL('%s/videos/?api_key=%s&format=json&offset=%s' % (API_PATH, ApiKey(), offset))

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
        newOffset = listedSoFar + result['limit']
        oc.add(
            NextPageObject(
                key=Callback(Videos, cat_id=cat_id, query=query, offset=newOffset),
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
