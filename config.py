#Digest login source server
sourceuser = "matterhorn_system_account"
sourcepassword = "CHANGE_ME"
header = {"X-Requested-Auth": "Digest"}

#Source Engage Server data
engageserver = "http://your.server.com"
searchendpoint = "/search/episode.json?id="
seriesSearchendpoint = "/search/episode.json?q="

#Source Admin/Archive Server
archiveserver = "http://your.server.com"
archiveendpoint = "/episode/episode.json?id="

#target admin/ingest server
targetserver = "http://yourtargetserver.com"
targetuser = "opencast_system_account"
targetpassword = "yourpassword"

#target admin/ingest server
#targetserver = "http://localhost:8080"
#targetuser = "opencast_system_account"
#targetpassword = "CHANGE_ME"


#TargetWorkflow
targetworkflow="import"
