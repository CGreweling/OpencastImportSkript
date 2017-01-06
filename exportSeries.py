import json,sys,requests,re,os,xml
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree
from xml.dom import minidom
import config

#Digest login source server
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)

#Source Engage Server data
searchrequest = config.engageserver + config.seriesSearchendpoint + sys.argv[1]

print searchrequest

# Get mediapackage from search service
searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)
mediapackagesearch = searchresult.json()['search-results']['result']
print searchresult
print mediapackagesearch
#print json.dumps(mediapackagesearch['mediapackage'])
for mediapackage in mediapackagesearch:

    print "Ingesting id: "+  mediapackage['id']
    command = 'python exportEpisode.py '+ mediapackage['id']
    print command
    os.system(command)
