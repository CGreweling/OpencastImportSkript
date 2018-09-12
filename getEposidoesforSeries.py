#!/bin/python
import config,requests
import sys
from requests.auth import HTTPDigestAuth




#Opencast sends an Object if list cotains only one Item instead of list
def jsonMakeObjectToList(jsonobject):
    if (not isinstance(jsonobject, list)):
        tmpObject = jsonobject
        jsonobject = []
        jsonobject.append(tmpObject)
        return jsonobject
    else:
     return jsonobject

def getEpisodesForSeries(seriesId):
    episodeIds=[]
    searchrequest = config.engageserver + config.seriesSearchendpoint + seriesId
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header, verify=False)
    if (searchresult.json()['search-results']['total']!='0'):
      mediapackagesearch = searchresult.json()['search-results']['result']
      mediapackagesearch=jsonMakeObjectToList(mediapackagesearch)
      for mediapackage in mediapackagesearch:
        episodeIds.append(mediapackage['id'])
      return episodeIds
    else:
      return 'nothing'

def getSeriesIdsFromFile(filename):
    with open(filename, 'r') as f:
      SeriesIds = f.readlines()
    return SeriesIds


#Main
#Digest login for targer server
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

#Digest login source server
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)


for seriesId in getSeriesIdsFromFile(sys.argv[1]):
  with open('episodesToDelete.txt', 'a') as file:
     for episodeIds in  getEpisodesForSeries(seriesId):
       file.writelines(episodeIds + "\n")


