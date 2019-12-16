#Digest login source server
sourceuser = "matterhorn_system_account"
sourcepassword = "Password"
header = {"X-Requested-Auth": "Digest"}

#Source Engage Server data
engageserver = "https://engage-mh.YOURDOMAIN"
searchendpoint = "/search/episode.json?id="
seriesSearchendpoint = "/search/episode.json?sid="

#Source Admin/Archive Server
archiveserver = "https://admin-mh.YOURDOMAIN"
archiveendpoint = "/episode/episode.json?id="

#target admin/ingest server
targetserver = "http://localhost:8080"
targetuser = "opencast_system_account"
targetpassword = "CHANGE_ME"

#TargetWorkflow
targetworkflow="import"

