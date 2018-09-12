import sys,requests,re,os
from requests.auth import HTTPDigestAuth

import config, handleSeries

#Digest login for targer server
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

#Digest login source server
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)

#Source Engage Server data
searchrequest = config.engageserver + config.seriesSearchendpoint + sys.argv[1]
print searchrequest

# check if Series exists, else create
handleSeries.handleSeries((sys.argv[1]).rstrip())


#Opencast sends an Object if list cotains only one Item instead of list
def jsonMakeObjectToList(jsonobject):
    if (not isinstance(jsonobject, list)):
        tmpObject = jsonobject
        jsonobject = []
        jsonobject.append(tmpObject)
        return jsonobject
    else:
     return jsonobject


def publishedEpisode(episodeId):
    restCall ='https://video4.virtuos.uos.de' + '/search/episode.json?id='+ episodeId
    result = requests.get(restCall, auth=targetauth, headers=config.header, verify=False)
    total = result.json()['search-results']['total']
    if total!="0":
        return True
    else:
        return False

# Get mediapackage from search service
searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header, verify=False)

try:
  searchresult.json()['search-results']['result']
  mediapackagesearch = searchresult.json()['search-results']['result']
  mediapackagesearch=jsonMakeObjectToList(mediapackagesearch)

#ingest each Episode
  for mediapackage in mediapackagesearch:
    if not publishedEpisode(mediapackage['mediapackage']['id']):
      print "Ingesting id: "+  mediapackage['mediapackage']['id'] + "\n"
      command = 'python exportEpisode.py '+ mediapackage['id']
      print command +"\n"
      os.system(command)
    else:
      print "Episode already published, skipping this one: " + mediapackage['id']

except:
 print "No Episodes in this Series"
