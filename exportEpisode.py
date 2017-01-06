import json,sys,requests,re,os,xml
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree
from xml.dom import minidom
import config




searchrequest = config.engageserver + config.searchendpoint + sys.argv[1]

archiverequest = config.archiveserver + config.archiveendpoint + sys.argv[1]

sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

# Get mediapackage from search service
searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)

mediapackagesearch = searchresult.json()['search-results']['result']['mediapackage']

# Get mediapackage from episode/archive service
archiveresult = requests.get(archiverequest, auth=sourceauth, headers=config.header)
mediapackagearchive = archiveresult.json()['search-results']['result']['mediapackage']

# get all tracks from search both services
track = mediapackagesearch['media']['track']
tracktmp = mediapackagearchive['media']['track']

# make sure that tracks are lists not only objects
if (isinstance(track, list)) :
    trackfrommediapackage = track
else:
    trackfrommediapackage = []
    trackfrommediapackage.append(track)

# make sure that tracks are lists not only objects
if (isinstance(tracktmp, list)) :
    trackfromarchive = tracktmp
else:
    trackfromarchive = []
    trackfromarchive.append(tracktmp)

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

# get attachment lists from both services
attachments = mediapackagesearch['attachments']['attachment']

# make sure that tracks are lists not only objects
if (isinstance(attachments, list)) :
    attachmentsfrommediapackage = attachments
else:
    attachmentsfrommediapackage = []
    attachmentsfrommediapackage.append(attachments)



if "attachment" in mediapackagearchive['attachments']:
    attachmentstmp = mediapackagearchive['attachments']['attachment']
    # make sure that tracks are lists not only objects
    if (isinstance(attachmentstmp, list)) :
     attachmentsfromarchive = attachmentstmp
     # merge attachment lists
     attachmentsnew = attachmentsfrommediapackage + attachmentsfromarchive
    else:
     attachmentsfromarchive= []
     attachmentsfromarchive.append(attachmentstmp)
     attachmentsnew = attachmentsfrommediapackage + attachmentsfromarchive

else:
     attachmentsnew = attachmentsfrommediapackage





# replace old attachments list
mediapackagesearch['attachments']['attachment'] = attachmentsnew

#finalmediapackage = dict()
finalmediapackage = {}
finalmediapackage['mediapackage'] = mediapackagesearch

reload(sys)
sys.setdefaultencoding('utf-8')

# write to json file with current ID
with open(sys.argv[1]+'.json', 'w') as f:
  json.dump(finalmediapackage, f, ensure_ascii=False)

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

# download catalogs with curl and upload them to the target opencast (no checking for errors yet)
for c in mediapackagesearch['metadata']['catalog']:
    if ('type' and 'url' in c):
        filename = str(c.get('url')).split("/")[-1]
        command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + c.get('url') + " -o " + filename
        os.system(command)
        files = {'file': open(filename, 'rb')}
        tags = parseTagsToString(c.get("tags").get("tag"))
        payload = {'flavor': c.get("type"), 'mediaPackage': ingest_mp, 'tags' : tags }
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addCatalog", headers=config.header, files=files, auth=targetauth, data=payload)
        ingest_mp = ingest_track_resp.text
        os.remove(filename)

# download attachments with curl and upload them to the target opencast (no checking for errors yet)
for a in mediapackagesearch['attachments']['attachment']:
    if (type and 'url' in a):
        filename = str(a.get('url')).split("/")[-1]
        command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + a.get('url') + " -o " + filename
        os.system(command)
        files = {'file': open(filename, 'rb')}
        tags = parseTagsToString(a.get("tags").get("tag"))
        payload = {'flavor': a.get("type"), 'mediaPackage': ingest_mp, 'tags' : tags }
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addAttachment", headers=config.header, files=files, auth=targetauth, data=payload)
        ingest_mp = ingest_track_resp.text
        os.remove(filename)


# download tracks with curl and upload them to the target opencast (no checking for errors yet)
for t in mediapackagesearch['media']['track']:
    print t.get('id')
    if (type and 'url' in t):
        filename = str(t.get('url')).split("/")[-1]
        command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + t.get('url') + " -o " + filename
        os.system(command)
        files = {'file': open(filename, 'rb')}

        tags = parseTagsToString(t.get("tags").get("tag"))
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

print(prettify(ElementTree.fromstring(ingest_mp)))

def ingestMediapackage(mediapackage):
    mediapackage=prettify(ElementTree.fromstring(ingest_mp))
    f = open('mediapackage.xml', 'w')
    f.write(mediapackage)
    f.close()
    payload = {'mediaPackage': mediapackage}
    ingest_track_resp = requests.post(config.targetserver + "/ingest/ingest/"+config.targetworkflow, headers=config.header, auth=targetauth, data=payload)
    print(ingest_track_resp)
    print(ingest_track_resp.text)

ingestMediapackage(ingest_mp)
