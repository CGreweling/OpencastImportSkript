import sys,requests,re,os
from requests.auth import HTTPDigestAuth

import config, handleSeries

#Digest login source server
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)

#Source Engage Server data
searchrequest = config.engageserver + config.seriesSearchendpoint + sys.argv[1] + '&limit=100'

print searchrequest

# check if Series exists, else create
handleSeries.handleSeries(sys.argv[1])


#Opencast sends an Object if list cotains only one Item instead of list
def jsonMakeObjectToList(jsonobject):
    if (not isinstance(jsonobject, list)):
        tmpObject = jsonobject
        jsonobject = []
        jsonobject.append(tmpObject)
        return jsonobject
    else:
     return jsonobject


# Get mediapackage from search service
searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)
mediapackagesearch = searchresult.json()['search-results']['result']
mediapackagesearch=jsonMakeObjectToList(mediapackagesearch)

counter=0
#control for user
for mediapackage in mediapackagesearch:
    print "Ingesting id: "+  mediapackage['mediapackage']['id'] + mediapackage['mediapackage']['title']
    print "Series - " + mediapackage['mediapackage']['seriestitle']
    counter+=1
goOn = raw_input("Ingest Episodes -"+str(counter)+"- ? (y/n)").lower()

if(goOn=='y'):
 #ingest each Episode
 for mediapackage in mediapackagesearch:
    command = 'python exportEpisode.py '+ mediapackage['id']
    print command +"\n"
    os.system(command)

else:
    print ('Not ingesting')
