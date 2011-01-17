
# PMS plugin framework v2

####################################################################################################

VIDEO_PREFIX     = "/video/pbskids"
PBSKIDS_URL      = "http://www.pbskids.org/video/"
PBSKIDS_SHOWS    = "http://pbskids.org/everything.html"
PBS_JSON         = "http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&startIndex=1&endIndex=500&sortField=airdate&sortDescending=true&query=contentCustomBoolean|isClip|%s&field=airdate&field=author&field=bitrate&field=description&field=format&field=length&field=PID&field=thumbnailURL&field=title&field=URL&contentCustomField=isClip&param=affiliate|prekPlayer&field=categories&field=expirationDate&query=categories|%s"

CATEGORY_LIST    = "http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&query=CustomText|CategoryType|%s&query=HasReleases&field=title&field=thumbnailURL"
NAME = L('Title')


# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.jpg'
ICON          = 'icon-default.gif'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.art = R(ART)
  MediaContainer.title1 = NAME
  DirectoryItem.thumb=R(ICON)
  
####################################################################################################
def MainMenu():
    dir = MediaContainer(mediaType='video', viewGroup='List')
    dir.Append(Function(DirectoryItem(ShowsList, "Shows"), categoryType = "Show"))
    dir.Append(Function(DirectoryItem(ShowsList, "Topics"), categoryType = "Channel"))
    return dir
 
####################################################################################################
def ShowPage(sender, title, thumb):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='List')
    #title = title.replace(' ', '%20').replace('&', '%26')  ### FORMATTING FIX
    dir.Append(Function(DirectoryItem(VideoPage, "Full Episodes", thumb=thumb), clip='false', title=title))
    dir.Append(Function(DirectoryItem(VideoPage, "Clips", thumb=thumb), clip='true', title=title))
    return dir

####################################################################################################
def VideoPage(sender, clip, title):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    title = title.replace(' ', '%20').replace('&', '%26')  ### FORMATTING FIX
    content = JSON.ObjectFromURL(PBS_JSON % (clip, title), cacheTime=CACHE_1DAY)
    Log(content)
    for item in content['items']:
        thumb = item['thumbnailURL']
        Log(thumb)
        link = item['URL']
        Log(link)
        title = item['title']
        Log(title)
        summary = item['description']
        Log(summary)
        duration = item['length']
        Log(duration)
        dir.Append(Function(VideoItem(VideoPlayer, title=title, thumb=thumb, summary=summary, duration=duration), link=link))
    return dir

####################################################################################################
def VideoPlayer(sender, link):
    dir = MediaContainer(title2=sender.itemTitle)
    link = link + '&format=SMIL'
    videosmil = HTTP.Request(link).content
    clip = videosmil.split("ref src")
    player = clip[0]
    clip = clip[1].split('"')
    player = player.split("meta base")
    player = player[1].split('"')
    player = player[1]
    if ".mp4" in clip[1]:
        clip = clip[1].replace(".mp4", "")
        clip = "mp4:" + clip
    else:
        clip = clip[1].replace(".flv", "")
    return Redirect(RTMPVideoItem(player, clip))

####################################################################################################
def ShowsList(sender, categoryType):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='List')
    content = JSON.ObjectFromURL(CATEGORY_LIST % categoryType)
    for item in content['items']:
        title = item['title']
        Log(title)
        thumb = item['thumbnailURL']
        Log(thumb)
        if thumb != "":
            if "Channel Sample" not in title:
                if categoryType == "Show":
                    dir.Append(Function(DirectoryItem(ShowPage, title, thumb=thumb), title=title, thumb=thumb))
                else:
                    dir.Append(Function(DirectoryItem(VideoPage, title, thumb=thumb), clip='true', title=title))
    return dir

