#!/bin/python
import handleSeries
import sys
import config
import requests
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

def isEpisodepublished(episodeId):
    restCall =config.targetengageserver + '/search/episode.json?id='+ episodeId
    result = requests.get(restCall, auth=targetauth, headers=config.header, verify=False)
    total = str(result.json()['search-results']['total'])
    print str(total) +" Total Number"
    if total!='0':
        print ("Episode is published")
        return True
    else:
        print ("Episode not published")
        return False

def getEpisodesForSeries(seriesId):
    episodeIds=[]
    searchrequest = config.engageserver + config.seriesSearchendpoint + seriesId
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header, verify=False)

    mediapackagesearch = searchresult.json()['search-results']['result']
    mediapackagesearch=jsonMakeObjectToList(mediapackagesearch)
    for mediapackage in mediapackagesearch:
        episodeIds.append(mediapackage['id'])
    return episodeIds

def getSeriesIdsFromFile(filename):
    with open(filename, 'r') as f:
      SeriesIds = f.readlines()
    return SeriesIds

def addToCsv(text):
    with open(csvFile, 'a') as file:
      file.writelines(text+"\n")

def proofSeries(seriesId):
    if handleSeries.existsSeries(seriesId):
      addToCsv(seriesId+";;x;")
    else:
      addToCsv(seriesId+";;;x")

def proofEpisode(episodeId):
    if isEpisodepublished(episodeId):
        addToCsv(";"+episodeId+";x;")
    else:
        addToCsv(";"+episodeId+";;x")

#Main
#Digest login for targer server
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

#Digest login source server
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)

csvFile="CheckedMigration.csv"
csvHead="Series;Episode;Published;NotPublished"
addToCsv(csvHead)


for seriesId in getSeriesIdsFromFile(sys.argv[1]):
  proofSeries(seriesId.rstrip())
  for episodeId in getEpisodesForSeries(seriesId) :
      proofEpisode(episodeId)

print("Done")
