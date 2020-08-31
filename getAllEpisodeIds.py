import json, sys, requests, re, os, xml
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from xml.dom import minidom
import config


searchrequest = config.engageserver + "/search/episode.xml"
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)


def getMediapackageDataFromSearch():
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)
    print(searchrequest)
    searchresult = ElementTree.fromstring(searchresult.text)
    print(searchresult)
    return searchresult

def main():
  mediapackages = getMediapackageDataFromSearch()
  allIds=''
  for mediapackage in mediapackages.findall('{http://search.opencastproject.org}result'):
    id=str(mediapackage.get('id'))
    print(id)
    allIds+=str(id+"\n")

    f = open('All_Episodes_List.txt', 'w')
    f.write(allIds)
    f.close()

if __name__ == "__main__":
    main()
