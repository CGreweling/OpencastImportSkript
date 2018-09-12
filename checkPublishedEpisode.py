import json,sys,requests
import config
from requests.auth import HTTPDigestAuth

targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)


episodeId= sys.argv[1]



def publishedEpisode(episodeId):
    print("checking for published Episode: "+episodeId)
    searchrequest ='http://yourenagenode.com' + '/search/episode.json?id='+ episodeId
    searchresult = requests.get(searchrequest, auth=targetauth, headers=config.header, verify=False)
    print searchresult
    total = int(searchresult.json()['search-results']['total'])
    print total

    if total>=1:
        return True
    else:
        return False



if publishedEpisode(episodeId):
    print ("Epsode already published -- next!")
else:
    print ('doing something')
