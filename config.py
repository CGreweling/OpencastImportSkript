#Digest login source server
sourceuser = "matterhorn_system_account"
sourcepassword = "Password"
header = {"X-Requested-Auth": "Digest"}

#Source Engage Server data
engageserver = "http://testserver.de"
searchendpoint = "/search/episode.json?id="
seriesSearchendpoint = "/search/episode.json?cid="

#Source Admin/Archive Server
archiveserver = "http://testserver.de"
archiveendpoint = "/episode/episode.json?id="

#target admin/ingest server
targetserver = "http://testserver.de"
targetuser = "opencast_system_account"
targetpassword = "CHANGE_ME"

#TargetWorkflow
targetworkflow="import"

