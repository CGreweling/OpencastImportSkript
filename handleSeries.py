import sys,requests
import config
from requests.auth import HTTPDigestAuth


def handleSeries(seriesId):
  if not (existsSeries(seriesId)):
      createSeries(getSeriesXml(seriesId),getseriesACl(seriesId))
      print ("Series created")
  else:
      print ("Series allready exists")


def existsSeries(seriesId):
    searchrequest = config.targetserver + '/series/'+ seriesId +'.xml'
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)
    if (searchresult.status_code==200):
        return True
    else:
        return False


def createSeries(seriesXml,seriesACL):
    payload = {'series': seriesXml, 'acl': seriesACL}
    createSeries_resp = requests.post(config.targetserver + "/series/", headers=config.header,
                                      auth=targetauth, data=payload)
    print(createSeries_resp.text)

def getSeriesXml(seriesId):
    searchrequest = config.archiveserver + '/series/' + seriesId + '.xml'
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)
    return searchresult.text


def getseriesACl(seriesId):
    searchrequest = config.archiveserver + '/series/' + seriesId + '/acl.xml'
    searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)
    return searchresult.text


sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)
targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)


seriesId=''




