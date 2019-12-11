import sys, requests, re, os

from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth

import config, handleSeries

# Digest login source server
sourceauth = HTTPBasicAuth("greweling", "opencast!2019")


# get Events from for series from api
searchrequest = config.archiveserver + "/api/v1/events?filter=is_part_of:" + sys.argv[1]

print(searchrequest)

# check if Series exists, else create
handleSeries.handleSeries(sys.argv[1])


# Opencast sends an Object if list cotains only one Item instead of list
def jsonMakeObjectToList(jsonobject):
    if (not isinstance(jsonobject, list)):
        tmpObject = jsonobject
        jsonobject = []
        jsonobject.append(tmpObject)
        return jsonobject
    else:
        return jsonobject


# Get mediapackage from search service
searchresult = requests.get(searchrequest, auth=sourceauth).json()

#mediapackagesearch = searchresult
#mediapackagesearch = jsonMakeObjectToList(mediapackagesearch)

# ingest each Episode
for event in searchresult:
     print("Ingesting id: " + event['event']['eventId'] + "\n")
     command = 'python exportEpisode.py ' + event['event']['eventId']
     print(command + "\n")
     os.system(command)
