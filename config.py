#Digest login source server
sourceuser = "sourceuser"
sourcepassword = "sourcepassword"
header = {"X-Requested-Auth": "Digest"}

#Source Engage Server data
engageserver = "https://entwine.com"
searchendpoint = "/search/episode.json?id="
seriesSearchendpoint = "/search/episode.json?cid="
searchendpoint = "/search/episode.xml?id="
seriesSearchendpoint = "/search/episode.xml?sid="

#Source Admin/Archive Server
archiveserver = "https://entine-archive.com"
archiveendpoint = "/assets/episode/"
archiveendpoint = "/episode/episode.xml?id="

#target admin/ingest server
targetserver = "https://develop.opencast.org"
targetuser = "opencast_system_account"
targetpassword = "password"

#TargetWorkflow
targetworkflow="import"

