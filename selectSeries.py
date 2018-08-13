#!/bin/python
import requests,re,os
from requests.auth import HTTPDigestAuth
import Tkinter as tk
from Tkinter import *
import config

#Digest login source server
sourceauth = HTTPDigestAuth(config.sourceuser, config.sourcepassword)

seriesDiconary = dict()

#get Series count
archiveSeriesCount =  "/series/count"
archiveSeriesCountrequest = config.archiveserver + archiveSeriesCount
seriesCount= requests.get(archiveSeriesCountrequest, auth=sourceauth, headers=config.header)
print archiveSeriesCountrequest
print seriesCount.text + " Series found"

finalSeriesString=''

def getStartTimeFromEpisodeforSeries(seriesId):
    try:
      searchrequest = config.engageserver + config.seriesSearchendpoint + seriesId

      searchresult = requests.get(searchrequest, auth=sourceauth, headers=config.header)

      mediapackagesearch = searchresult.json()['search-results']['result'][0]
      #mediapackagesearch=jsonMakeObjectToList(mediapackagesearch)
    
      return mediapackagesearch['dcCreated']
    except: 
      return ''

#python reqeusts can not handle as much data as e.g. firefox so... paging
page=0
#result per request
resultsize=1
seriesCount = int(seriesCount.text)
#get the number of pages
pages = seriesCount/resultsize
while page < pages:
      archiveenpoint = "/series/series.json?count="+str(resultsize)+"&startPage="+str(page)
      archiverequest = config.archiveserver + archiveenpoint
      archiveresult = requests.get(archiverequest, auth=sourceauth, headers=config.header).json()
      if  archiveresult['catalogs']:
              if archiveresult['catalogs'][0]['http://purl.org/dc/terms/']['identifier'][0]['value'] not in finalSeriesString:
                  title=archiveresult['catalogs'][0]['http://purl.org/dc/terms/']['title'][0]['value']

                  seriesId=archiveresult['catalogs'][0]['http://purl.org/dc/terms/']['identifier'][0]['value']
                  print (archiveresult['catalogs'][0]['http://purl.org/dc/terms/'])
                  finalSeriesString=finalSeriesString+title+ " ; "+seriesId+" ; "+getStartTimeFromEpisodeforSeries(seriesId)+'\n'
                  #safe id+title in an dictonary
                  seriesDiconary.update({seriesId:title})

      page=page+1



#save all Series to File seperated by ';'
f = open('All_Series_List.txt', 'w')
f.write(finalSeriesString.encode('UTF-8'))
f.close()

selectedSeries = dict()

def delteDuplicates(dictWithDuplicates):
    result = {}
    for key,value in dictWithDuplicates.items():
        if value not in result.values():
            result[key] = value
    return result

def writeSelectedSeriestoFile():
    selectedSeriesForFile=delteDuplicates(selectedSeries)
    selectedSeriesFile = ''
    for key, value in selectedSeriesForFile.iteritems():
        if value.get() == '1':
           selectedSeriesFile=selectedSeriesFile + key+' ; ' + seriesDiconary.get(key) + '\n'
    f = open("Selecet_Series_File.txt",'w')
    f.write(selectedSeriesFile.encode('UTF-8'))
    f.close()
    print ("Selecet_Series_File.txt Created!")

def ingest():
    selectedSeriesForIngest=delteDuplicates(selectedSeries)
    for key, value in selectedSeriesForIngest.iteritems():
        if value.get()=='1':
            print key
            command="python exportSeries.py "+ key
            os.system(command)


#create ui to select Series for ingest
root = tk.Tk()
vsb = tk.Scrollbar(root, orient="vertical")
text = tk.Text(root, width=40, height=20,
                            yscrollcommand=vsb.set)
vsb.config(command=text.yview)
vsb.pack(side="right", fill="y")
text.pack(side="left", fill="both", expand=True)



for key, value in seriesDiconary.iteritems():
      selectedSeries[key]=Variable()
      checkButton = tk.Checkbutton(root, text = value+" : "+key, variable = selectedSeries[key])
      text.window_create("end", window=checkButton)
      text.insert("end", "\n") # to force one checkbox per line

button = Button(root,text='Ingest Selected Series',command=ingest)
button.pack()
button = Button (root, text="Create Selected Series File",command=writeSelectedSeriestoFile)
button.pack()
button = Button (root, text="Quit!",fg='red', command=root.destroy)
button.pack()

root.mainloop()
