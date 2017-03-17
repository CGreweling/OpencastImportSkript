#Digest login source server
sourceuser = "matterhorn_system_account"
sourcepassword = "yourPassword"
header = {"X-Requested-Auth": "Digest","X-Opencast-Matterhorn-Authorization": "True"}

#Source Engage Server data
engageserver = "http://your.engage.de"
searchendpoint = "/search/episode.json?id="
seriesSearchendpoint = "/search/episode.json?sid="

#Source Admin/Archive Server
archiveserver = "http://your.admin.de"
archiveendpoint = "/episode/episode.json?id="

#target admin/ingest server
targetserver = "http://your.target.admin.de"
targetuser = "opencast_system_account"
targetpassword = "yourtargetpassword"

#TargetWorkflow
targetworkflow="ng-import"
