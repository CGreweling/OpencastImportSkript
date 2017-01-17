import json,sys,requests,re,os,xml
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree
from xml.dom import minidom
import config
import handleSeries




searchrequest = config.engageserver + config.searchendpoint + sys.argv[1]

archiverequest = config.archiveserver + config.archiveendpoint + sys.argv[1]

sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

# Get mediapackage from search service
searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)

mediapackagesearch = searchresult.json()['search-results']['result']['mediapackage']


trackfromarchive=[]
attachmentsfromarchive=[]
mediapackagearchive= dict()
archivePresentationTracks=False

#Opencast sends an Object if list cotains only one Item instead of list
def jsonMakeObjectToList(jsonobject):
    if (not isinstance(jsonobject, list)):
        tmpObject = jsonobject
        jsonobject = []
        jsonobject.append(tmpObject)
        return jsonobject
    else:
     return jsonobject


# Get mediapackage from episode/archive service
archiveresult = requests.get(archiverequest, auth=sourceauth, headers=config.header)
if (archiveresult.json()['search-results'].get('result')):
    mediapackagearchive = archiveresult.json()['search-results']['result']['mediapackage']
    # get Tracks
    trackfromarchive = jsonMakeObjectToList(mediapackagearchive['media']['track'])
    attachmentsfromarchive = jsonMakeObjectToList(mediapackagearchive['attachments']['attachment'])
else:
    archivePresentationTracks=True
    print ("Hint: This Episode was not Archived + Archive for Presentation Tracks")



# get all tracks from search
track = mediapackagesearch['media']['track']

# make sure that tracks are lists not only objects
if (isinstance(track, list)) :
    trackfrommediapackage = track
else:
    trackfrommediapackage = []
    trackfrommediapackage.append(track)




# get attachment lists from both services
attachments = mediapackagesearch['attachments']['attachment']
attachmentsfrommediapackage = []
# make sure that tracks are lists not only objects
if (isinstance(attachments, list)) :
    attachmentsfrommediapackage = attachments
else:
    attachmentsfrommediapackage.append(attachments)


# replace old attachments list
mediapackagesearch['attachments']['attachment'] = attachmentsfromarchive + attachmentsfrommediapackage

# merge both track lists
tracknew = trackfrommediapackage + trackfromarchive

# remove all streaming server entries
trackwithoutrtmp = []
for t in tracknew:
    url = str(t.get('url'))
    if not re.match("^rtmp", url):
        trackwithoutrtmp.append(t)

# add new tracklist to mediapackage again
mediapackagesearch['media']['track'] = trackwithoutrtmp


finalmediapackage = {}
finalmediapackage['mediapackage'] = mediapackagesearch

reload(sys)
sys.setdefaultencoding('utf-8')

# write to json file with current ID
#with open(sys.argv[1]+'.json', 'w') as f:
#  json.dump(finalmediapackage, f, ensure_ascii=False)

#################### start ingesting


# empty mediapackage with the right ID
#ingest_mp = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><mediapackage xmlns="http://mediapackage.opencastproject.org" id="' + sys.argv[1]  + '" start="2016-08-01T12:44:03Z"><media/><metadata/><attachments/><publications/></mediapackage>'

# create mediapackage with right ID
ingest_track_resp = requests.put(config.targetserver + "/ingest/createMediaPackageWithID/"+sys.argv[1], headers=config.header, auth=targetauth)
ingest_mp = ingest_track_resp.text


# parse Tags to String list seperated by ,
def parseTagsToString(tags):
     #fix json bug, on element=not list element
     if  type(tags) is list :
            #tags=t.get("tags")
            tags=','.join(tags)
            return tags
     else:
            #tags= t.get("tags").get("tag")
            return tags


#create correct json object
mediapackagesearch['metadata']['catalog'] = jsonMakeObjectToList(mediapackagesearch['metadata']['catalog'])

# download catalogs with curl and upload them to the target opencast (no checking for errors yet)
for c in mediapackagesearch['metadata']['catalog']:
    if (c.get('type') and c.get('url')):
        filename = str(c.get('url')).split("/")[-1]
        command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + c.get('url') + " -o " + filename
        os.system(command)
        files = {'file': open(filename, 'rb')}
        tags = parseTagsToString(c.get("tags").get("tag"))
        payload = {'flavor': c.get("type"), 'mediaPackage': ingest_mp, 'tags' : tags }
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addCatalog", headers=config.header, files=files, auth=targetauth, data=payload)
        ingest_mp = ingest_track_resp.text
        os.remove(filename)

# create correct json object
mediapackagesearch['attachments']['attachment']=jsonMakeObjectToList(mediapackagesearch['attachments']['attachment'])
# download attachments with curl and upload them to the target opencast (no checking for errors yet)
for a in mediapackagesearch['attachments']['attachment']:
    if (c.get('type') and c.get('url')):
        filename = str(a.get('url')).split("/")[-1]
        command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + a.get('url') + " -o " + filename
        os.system(command)
        files = {'file': open(filename, 'rb')}
        tags = parseTagsToString(a.get("tags").get("tag"))
        payload = {'flavor': a.get("type"), 'mediaPackage': ingest_mp, 'tags' : tags }
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addAttachment", headers=config.header, files=files, auth=targetauth, data=payload)
        ingest_mp = ingest_track_resp.text
        os.remove(filename)


# create correct json object
#mediapackagesearch['media']['track']=jsonMakeObjectToList(mediapackagesearch['media']['track'])
# download tracks with curl and upload them to the target opencast (no checking for errors yet)
for t in mediapackagesearch['media']['track']:
    if (c.get('type') and c.get('url')):
        filename = str(t.get('url')).split("/")[-1]
        command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + t.get('url') + " -o " + filename
        os.system(command)
        files = {'file': open(filename, 'rb')}
        tags = parseTagsToString(t.get("tags").get("tag"))
        if (archivePresentationTracks):
            tags += ','+ 'archive'
        payload = {'flavor': t.get("type"), 'mediaPackage': ingest_mp, 'tags' : tags }
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addTrack", headers=config.header, files=files, auth=targetauth, data=payload)
        ingest_mp = ingest_track_resp.text
        os.remove(filename)



def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

#print(prettify(ElementTree.fromstring(ingest_mp)))

def ingestMediapackage(mediapackage):
    mediapackage=prettify(ElementTree.fromstring(ingest_mp))
    f = open('mediapackage.xml', 'w')
    f.write(mediapackage)
    f.close()
    payload = {'mediaPackage': mediapackage}
    ingest_track_resp = requests.post(config.targetserver + "/ingest/ingest/"+config.targetworkflow, headers=config.header, auth=targetauth, data=payload)
    print(ingest_track_resp.text)
    print ("Ingesting done")

ingestMediapackage(ingest_mp)
