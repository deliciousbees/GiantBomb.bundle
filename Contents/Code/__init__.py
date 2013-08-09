API_PATH = 'http://api.giantbomb.com'
API_KEY = '70d735e54938286d6d9142727877107ced20e5ff'

ART = 'art-default.png'
ICON = 'icon-default.png'

def ValidatePrefs():
    link_code = Prefs['link_code'].upper()
    if link_code and len(link_code) == 6:
        response = JSON.ObjectFromURL(API_PATH + '/validate?link_code=' + link_code + '&format=json')
        if 'api_key' in response:
            Dict['api_key'] = response['api_key']
            Dict.Save()

@handler('/video/giantbomb', 'Giant Bomb')
def MainMenu():
    oc = ObjectContainer()

    # Live stream
    response = JSON.ObjectFromURL(API_PATH + '/chats/?api_key=' + ApiKey() + '&format=json')

    if response['status_code'] == 100:
        # Revert to the default key
        Dict.Reset()
        Dict.Save()

    chats = response['results']
    for chat in chats:
        url = 'http://www.justin.tv/widgets/live_embed_player.swf?channel=' + chat['channel_name'] + '&auto_play=true&start_volume=25'
        if chat['password']:
            url += '&publisherGuard=' + chat['password']
        try:
            thumb=chat['image']['super_url'],
        except:
            thumb = R(ICON)

        oc.add(
            VideoClipObject(
                key=WebVideoURL(url),
                title='LIVE: ' + chat['title'],
                summary=chat['deck'],
                source_title='Justin.tv',
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
            oc.add(
                DirectoryObject(
                    key='/video/giantbomb/erun',
                    title=cat['name'],
                    summary=cat['deck'],
                    thumb=R(ICON),
                    art=R(ART)
                )
            )
        else:
            oc.add(
                DirectoryObject(
                    key='/video/giantbomb/videos/?cat_id=' + str(cat['id']),
                    title=cat['name'],
                    summary=cat['deck'],
                    thumb=R(ICON),
                    art=R(ART)
                )
            )

    oc.add(
        SearchDirectoryObject(
            identifier="com.plexapp.plugins.giantbomb",
            title="Search",
            summary="Search Giant Bomb videos",
            prompt="Search for...",
            thumb=R(ICON),
            art=R(ART)
        )
    )

    oc.add(
        PrefsObject(
            title='Preferences',
            thumb=R(ICON),
            art=R(ART)
        )
    )

    return oc

@route('/video/giantbomb/erun')
def EnduranceRunMenu():
    oc = ObjectContainer(
        objects = [
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5-DP',
                title='Deadly Premonition',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5-P4',
                title='Persona 4',
                art=R(ART)
            ),
            DirectoryObject(
                key='/video/giantbomb/videos/?cat_id=5-MO',
                title='The Matrix Online: Not Like This',
                art=R(ART)
            )
        ]
    )

    return oc

@route('/video/giantbomb/videos')
def Videos(cat_id=None):
    oc = ObjectContainer()

    if cat_id == '5-DP':
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + ApiKey() + '&video_type=5&offset=161&format=json')['results']
    elif cat_id == '5-P4':
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + ApiKey() + '&video_type=5&format=json')['results']
        videos += JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + ApiKey + '&video_type=5&offset=100&limit=61&format=json')['results']
        videos = [video for video in videos if not video['name'].startswith('The Matrix Online')]
    elif cat_id == '5-MO':
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + ApiKey() + '&video_type=5&offset=105&limit=21&format=json')['results']
        videos = [video for video in videos if video['name'].startswith('The Matrix Online')]
    elif cat_id:
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + ApiKey() + '&video_type=' + cat_id + '&sort=-publish_date&format=json')['results']
    else:
        videos = JSON.ObjectFromURL(API_PATH + '/videos/?api_key=' + ApiKey() + '&sort=-publish_date&format=json')['results']

    for vid in videos:
        if 'wallpaper_image' not in vid or not vid['wallpaper_image']: # or whatever it gets called
            vid_art = R(ART)
        else:
            vid_art = vid['wallpaper_image']

        oc.add(
                VideoClipObject(
                    url=vid['site_detail_url'],
                    title=vid['name'],
                    summary=vid['deck'],
                    thumb=vid['image']['super_url'],
                    art=vid_art,
                    rating_key=vid['id']
                )
        )

    return oc

def ApiKey():
    if 'api_key' in Dict:
        return Dict['api_key']
    else:
        return API_KEY