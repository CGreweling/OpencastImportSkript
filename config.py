#Digest login source server
sourceuser = "matterhorn_system_account"
sourcepassword = "soutriv6511"
header = {"X-Requested-Auth": "Digest","X-Opencast-Matterhorn-Authorization": "True"}

#Source Engage Server data
engageserver = "http://video3.virtuos.uos.de"
searchendpoint = "/search/episode.json?id="
seriesSearchendpoint = "/search/episode.json?sid="

#Source Admin/Archive Server
archiveserver = "http://mh-admin.virtuos.uos.de"
archiveendpoint = "/episode/episode.json?id="

#target admin/ingest server
targetserver = "http://oc-admin.virtuos.uos.de:8080"
targetuser = "opencast_system_account"
targetpassword = "soutriv6511_digest"


#target engage Server
targetengageserver = "https://video4.virtuos.uos.de"

#TargetWorkflow
targetworkflow="ng-import"
