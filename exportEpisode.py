import json, sys, requests, re, os, xml
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree
from xml.dom import minidom
import config
import pycurl

from subprocess import Popen, PIPE, STDOUT
import addTrack

searchrequest = config.engageserver + config.searchendpoint + sys.argv[1]

archiverequest = config.archiveserver + config.archiveendpoint + sys.argv[1]

sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

# The Files will be downloaded to the lokal Disk, if false Opencast will download from set url in the Mediapackage
downloadToDisk = True

archivePresentationTracks = True


# Opencast sends an Object if list cotains only one Item instead of list
def jsonMakeObjectToList(jsonobject):
    if (not isinstance(jsonobject, list)):
        tmpObject = jsonobject
        jsonobject = []
        jsonobject.append(tmpObject)
        return jsonobject
    else:
        return jsonobject


def getMediapackageDataFromSearch():
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header).text
    return searchresult['search-results']['result']['mediapackage']


def getMediapackageDataFromArchive():

    return requests.get(archiverequest, auth=sourceauth, headers=config.header).text


def getMediapackageData():

    # Get mediapackage from episode/archive service
    archiveresult = getMediapackageDataFromArchive()

    return archiveresult


def createMediapackeOnIngestNode(mediaPackageId):
        # create mediapackage with right ID
        create_mediapackage_resp = requests.put(config.targetserver + "/ingest/createMediaPackageWithID/" + sys.argv[1],
                                                headers=config.header, auth=targetauth, verify=False)
        return create_mediapackage_resp.text


#  parse Tags to String list seperated by ,
def parseTagsToString(tags):
    # fix json bug, one element=not list element
    if type(tags) is list:
        # tags=t.get("tags")
        stringTags = ','.join(str(x) for x in tags)
        return stringTags
    else:
        # tags= t.get("tags").get("tag")
        return str(tags)

def getSignedURL(fileID,mediapacakgeID,xmlchild):
    url=''
    getURL= config.adminui+'/admin-ng/event/'+ mediapacakgeID +'/asset/'+xmlchild+'/'+fileID+'.json'
    print(getURL)
    trackJson = requests.get(getURL, headers=config.header,
                                      auth=sourceauth, verify=False).json()
    url = trackJson['url']
    print(url)

    return url


# download catalogs with curl and upload them to the target opencast
def donwloadCatalogsAndUpload(mediapackageSearch, ingest_mp):

    for catalog in mediapackageSearch.findall('{http://mediapackage.opencastproject.org}metadata/{http://mediapackage.opencastproject.org}catalog'):
        tags = []
        print(catalog.get('id'))
        print(catalog.get('url'))
        for tag in catalog.findall('{http://mediapackage.opencastproject.org}tags/{http://mediapackage.opencastproject.org}tag'):
            tags.append(tag.text)
        tags = ",".join(tags)

        urlFromMp = catalog.find('{http://mediapackage.opencastproject.org}url').text
        filename = str(urlFromMp.split("/")[-1])

        #DownloadFile
        command = "curl --digest -u " + config.sourceuser + ":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' '" + urlFromMp + "' -o " + filename
        print(command)
        os.system(command)
        files = {'file': open(filename, 'rb')}

        payload = {'flavor': str(catalog.get("type")), 'mediaPackage': str(ingest_mp), 'tags': str(tags)}
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addCatalog", headers=config.header,
                                          files=files, auth=targetauth, data=payload, verify=False)
        if ingest_track_resp.status_code == requests.codes.ok:
            ingest_mp = ingest_track_resp.text
        print(ingest_track_resp.text)
        payload = {'flavor': 'dublincore/episode', 'mediaPackage': str(ingest_track_resp), 'tags': str(tags)}
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addCatalog", headers=config.header,
                                          files=files, auth=targetauth, data=payload, verify=False)

        if ingest_track_resp.status_code == requests.codes.ok:
            ingest_mp = ingest_track_resp.text
        print(ingest_track_resp.text)
        os.remove(filename)
    return ingest_mp


# download attachments with curl and upload them to the target opencast
def downloadAttachmentsAndUpload(mediapackageSearch, ingest_mp):

     for attechment in mediapackageSearch.findall('{http://mediapackage.opencastproject.org}attachments/{http://mediapackage.opencastproject.org}attachment'):
        tags = []
        print(attechment.get('id'))
        for tag in attechment.findall('{http://mediapackage.opencastproject.org}tags/{http://mediapackage.opencastproject.org}tag'):
            tags.append(tag.text)
        tags = ",".join(tags)

        urlFromMp = attechment.find('{http://mediapackage.opencastproject.org}url').text
        filename = str(urlFromMp.split("/")[-1])

        #DownloadFile
        command = "curl --digest -u " + config.sourceuser + ":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' '" + urlFromMp + "' -o " + filename
        print(command)
        os.system(command)
        files = {'file': open(filename, 'rb')}


        payload = {'flavor': attechment.get("type"), 'mediaPackage': ingest_mp, 'tags': tags}
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addAttachment", headers=config.header,
                                          files=files, auth=targetauth, data=payload, verify=False)
        if ingest_track_resp.status_code == requests.codes.ok:
          ingest_mp = ingest_track_resp.text
        os.remove(filename)
     return ingest_mp


# create correct json object

def downloadTracksAndUpload(mediapackageSearch, ingest_mp):

    for track in mediapackageSearch.findall('{http://mediapackage.opencastproject.org}media/{http://mediapackage.opencastproject.org}track'):
        tags = []

        for tag in track.findall('{http://mediapackage.opencastproject.org}tags/{http://mediapackage.opencastproject.org}tag'):
            tags.append(tag.text)
        tags = ",".join(tags)

        urlFromMp = track.find('{http://mediapackage.opencastproject.org}url').text
        filename = str(urlFromMp.split("/")[-1])

        #DownloadFile
        command = "curl --digest -u " + config.sourceuser + ":" + config.sourcepassword + " -H 'X-Requested-Auth: Digest' '" + urlFromMp + "' -o " + filename
        print(command)
        os.system(command)
        files = {'file': open(filename, 'rb')}

        payload = {'flavor': track.get("type"), 'mediaPackage': ingest_mp, 'tags': tags}
        ingest_track_resp = requests.post(config.targetserver + "/ingest/addTrack", headers=config.header,
                                          files=files, auth=targetauth, data=payload, verify=False)
        if ingest_track_resp.status_code == requests.codes.ok:
            ingest_mp = ingest_track_resp.text
        os.remove(filename)
    return ingest_mp


def prettifyxml(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def ingestMediapackage(mediapackage):
    #print(mediapackage)
    mediapackage = prettifyxml(ElementTree.fromstring(mediapackage))
    f = open('mediapackage.xml', 'w')
    f.write(mediapackage)
    f.close()
    payload = {'mediaPackage': mediapackage}
    ingest_track_resp = requests.post(config.targetserver + "/ingest/ingest/" + config.targetworkflow,
                                      headers=config.header, auth=targetauth, data=payload, verify=False)
    print(ingest_track_resp.text)
    print("Ingesting done")


def main():
   # reload(sys)
    #sys.setdefaultencoding('utf-8')

    mediapackagesearch = getMediapackageData()
    print(mediapackagesearch)
    mediapackagexmltree = ElementTree.fromstring(mediapackagesearch)

    #print(prettifyxml(mediapackagexmltree))

    ingest_mp = createMediapackeOnIngestNode(sys.argv[1])
    ingest_mp = donwloadCatalogsAndUpload(mediapackagexmltree, ingest_mp)
    ingest_mp = downloadAttachmentsAndUpload(mediapackagexmltree, ingest_mp)
    ingest_mp = downloadTracksAndUpload(mediapackagexmltree, ingest_mp)

    print(prettifyxml(ElementTree.fromstring(ingest_mp)))
    ingestMediapackage(ingest_mp)


if __name__ == "__main__":
    main()
