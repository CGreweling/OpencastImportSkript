import json, sys, requests, re, os, xml, time
from requests.auth import HTTPDigestAuth

import config

maxRunningWorkflows = 2 
ListofEpisodesFilename = 'All_Episodes_List.txt'

targetauth = HTTPDigestAuth(config.targetuser, config.targetpassword)

def getRunningWorkflows():
    RunningWorkflowsUrl = config.targetserver+'/admin-ng/event/events.json?filter=status:EVENTS.EVENTS.STATUS.PROCESSING&limit=20'
    result = requests.get(RunningWorkflowsUrl, auth=targetauth, headers=config.header).json()
    countWorkflows = result['count']
    print("Running Workflows: " + str(countWorkflows))
    return countWorkflows

def exportEpisodesforAllLinesIn(filename):
    runningWorkflows = getRunningWorkflows()
    f= open(filename)
    for line in f:
        while runningWorkflows > maxRunningWorkflows:
            time.sleep(240)
            runningWorkflows = getRunningWorkflows()
        else:
            print(str(line))
            command = "python exportEpisode.py "+ str(line)
            os.system(command)
            print(command)

def main():
    exportEpisodesforAllLinesIn(ListofEpisodesFilename)

if __name__ == "__main__":
    main()
