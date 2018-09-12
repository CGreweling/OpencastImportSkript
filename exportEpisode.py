import json,sys,requests,re,os,xml
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree
from xml.dom import minidom
import config
from subprocess import Popen, PIPE, STDOUT
import addTrack
import pycurl

searchrequest = config.engageserver + config.searchendpoint + sys.argv[1]

archiverequest = config.archiveserver + config.archiveendpoint + sys.argv[1]

sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

#The Files will be downloaded to the lokal Disk, if false Opencast will download from set url in the Mediapackage
downloadToDisk = True




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

def getMediapackageData():
    mediapackagearchive = dict()
    trackfromarchive = []
    attachmentsfromarchive = []
    # Get mediapackage from search service
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)

    mediapackagesearch = searchresult.json()['search-results']['result']['mediapackage']
    # Get mediapackage from episode/archive service
    archiveresult = requests.get(archiverequest, auth=sourceauth, headers=config.header)
    if (archiveresult.json()['search-results'].get('result')):
        mediapackagearchive = archiveresult.json()['search-results']['result']['mediapackage']
        #print json.dumps(mediapackagearchive)
        # get Tracks
        try:
          trackfromarchive = jsonMakeObjectToList(mediapackagearchive['media']['track'])
        except TypeError:
          print "No track"
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
    #mediapackagesearch['attachments']['attachment'] = attachmentsfromarchive + attachmentsfrommediapackage
    mediapackagesearch['attachments']['attachment'] = attachmentsfrommediapackage

    # merge both track lists
    #tracknew = trackfrommediapackage + trackfromarchivie
    tracknew = trackfrommediapackage

    # remove all streaming server entries
    trackwithoutrtmp = []
    for t in tracknew:
        url = str(t.get('url'))
        if not re.match("^rtmp", url):
            trackwithoutrtmp.append(t)

    # add new tracklist to mediapackage again
    mediapackagesearch['media']['track'] = trackwithoutrtmp

    return mediapackagesearch



def createMediapackeOnIngestNode(mediaPackageId):
  if len(mediaPackageId) < 35:
    print ("Wrong uid creating new one:")
    create_mediapackage_resp = requests.get(config.targetserver + "/ingest/createMediaPackage", headers=config.header, auth=targetauth, verify=False)

    #write new uuid to file
    xmlMediapackage = ElementTree.fromstring(create_mediapackage_resp)
    with open("changedUUID.txt", 'a') as file:
      file.writelines(sys.argv[1]+";"+xmlMediapackage.get('id')+"\n")
    return create_mediapackage_resp.text
  else:
    # create mediapackage with right ID
    create_mediapackage_resp = requests.put(config.targetserver + "/ingest/createMediaPackageWithID/"+sys.argv[1], headers=config.header, auth=targetauth, verify=False)
    return create_mediapackage_resp.text


#  parse Tags to String list seperated by ,
def parseTagsToString(tags):
     #fix json bug, one element=not list element
     if  type(tags) is list :
            #tags=t.get("tags")
            stringTags=','.join(str(x) for x in tags)
            return stringTags
     else:
            #tags= t.get("tags").get("tag")
            return str(tags)


# download catalogs with curl and upload them to the target opencast
def donwloadCatalogsAndUpload(mediapackageCatalogs,ingest_mp):
    # create correct json object
    mediapackageCatalogs=jsonMakeObjectToList(mediapackageCatalogs)
    print ("Catalogs"+str(mediapackageCatalogs))
    for c in mediapackageCatalogs:
        if (c.get('type') and c.get('url')):
            filename = str(c.get('url')).split("/")[-1]
            command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + c.get('url') + " -o " + filename
            os.system(command)
            files = {'file': open(filename, 'rb')}
            tags = parseTagsToString(c.get("tags").get("tag"))
            payload = {'flavor': str(c.get("type")), 'mediaPackage': str(ingest_mp), 'tags' : str(tags) }
            ingest_track_resp = requests.post(config.targetserver + "/ingest/addCatalog", headers=config.header, files=files, auth=targetauth, data=payload, verify=False)
            os.remove(filename)
            if ingest_track_resp.status_code == requests.codes.ok:
                ingest_mp=ingest_track_resp.text
    return ingest_mp


# download attachments with curl and upload them to the target opencast
def downloadAttachmentsAndUpload(mediapackageAttachments,ingest_mp):
    mediapackageAttachments=jsonMakeObjectToList(mediapackageAttachments)
    for a in mediapackageAttachments:
        if (a.get('type') and a.get('url')):
            filename = str(a.get('url')).split("/")[-1]
            command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + a.get('url') + " -o " + filename
            os.system(command)
            files = {'file': open(filename, 'rb')}
            if (a.get("tags") is not list):
              tags =""
            else:
              tags = parseTagsToString(a.get("tags").get("tag"))
            payload = {'flavor': a.get("type"), 'mediaPackage': ingest_mp, 'tags' : tags }
            ingest_track_resp = requests.post(config.targetserver + "/ingest/addAttachment", headers=config.header, files=files, auth=targetauth, data=payload, verify=False)
            if ingest_track_resp.status_code == requests.codes.ok:
                ingest_mp = ingest_track_resp.text
            os.remove(filename)
    return ingest_mp

# create correct json object
#mediapackagesearch['media']['track']=jsonMakeObjectToList(mediapackagesearch['media']['track'])
def downloadTracksAndUpload(mediapackageTracks,ingest_mp):
    mediapackageTracks=jsonMakeObjectToList(mediapackageTracks)
    for t in mediapackageTracks:
        if (t.get('type') and t.get('url')):
          if downloadToDisk:
            filename = str(t.get('url')).split("/")[-1]
            command = "curl --digest -u " + config.sourceuser +":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' " + t.get('url') + " -o " + filename
            os.system(command)
            if os.path.isfile(filename):

              tags = parseTagsToString(t.get("tags").get("tag"))
              if (archivePresentationTracks):
                tags += ','+ 'archive'
              track = filename.encode('ascii', 'ignore')
              flavor = str(t.get('type'))
              fields = [('mediaPackage',str(ingest_mp)), ('flavor',str(flavor)),('tags',str(tags)),
                      ('BODY', (pycurl.FORM_FILE, track))]
              ingest_mp = addTrack.http_request(config.targetserver + '/ingest/addTrack', fields)
              os.remove(track)
            else:
              print ("Track not found skipping:" + filename)
          else:
            #let opencast download the files
            if (isinstance(t.get("tags"), unicode)):
              tags =""
            else:
              tags = parseTagsToString(t.get("tags").get("tag"))
            if (archivePresentationTracks):
               tags += ','+ 'archive'
            flavor = str(t.get('type'))
            print ('adding Tack : '+str(t.get('url') ))
            payload = {'flavor': flavor, 'mediaPackage': str(ingest_mp), 'tags' : str(tags) , 'url': str(t.get('url')) }
            ingest_track_resp = requests.post(config.targetserver + "/ingest/addTrack", headers=config.header,auth=targetauth, data=payload, verify=False)
            ingest_mp = ingest_track_resp.text
    return ingest_mp

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



def ingestMediapackage(mediapackage):
    print (mediapackage)
    mediapackage=prettify(ElementTree.fromstring(mediapackage))
    f = open('mediapackage.xml', 'w')
    f.write(mediapackage)
    f.close()
    payload = {'mediaPackage': mediapackage}
    ingest_track_resp = requests.post(config.targetserver + "/ingest/ingest/"+config.targetworkflow, headers=config.header, auth=targetauth, data=payload, verify=False)
    print(ingest_track_resp.text)
    print ("Ingesting done")


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    mediapackagesearch = getMediapackageData()

    ingest_mp = createMediapackeOnIngestNode(sys.argv[1])
    ingest_mp = donwloadCatalogsAndUpload(mediapackagesearch['metadata']['catalog'],ingest_mp)
    ingest_mp = downloadAttachmentsAndUpload(mediapackagesearch['attachments']['attachment'],ingest_mp)
    ingest_mp = downloadTracksAndUpload(mediapackagesearch['media']['track'],ingest_mp)

    # print(prettify(ElementTree.fromstring(ingest_mp)))
    ingestMediapackage(ingest_mp)


if __name__ == "__main__":
    main()
