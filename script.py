#Have to install BeautifulSoup, requests
#and maybe other external libraries
#See web resources to download for mac, windows or Linux
from requests import get
import requests
from bs4 import BeautifulSoup
import urllib.request
import json
from json import loads
import re
import time
​
#Get the content of the webpage
def getContentOfPage(url, session_requests):   
    result = session_requests.get(
        url,
        headers = dict(referer = url)
    )
    return BeautifulSoup(result.content, "html.parser")
​
#Get links from website
#internal specification for the different
#types of web structures
def getLinksFromSite(ParentContent, tag, SpecifiedAttrs, lessonsFetch, lessonFetch):
    result = {}
    Count = []
    if lessonsFetch != True:
        for section in ParentContent.findAll(tag, attrs=SpecifiedAttrs):
            links = section.findAll('a', href = re.compile('^/library/channels/list/[a-zA-Z]'))
            lessonCount = section.findAll('small')
            Count.append(lessonCount)
            result[links[0].text] = links[0]['href']
    else:
        if lessonFetch == False:
            lessonLinks = []
            for lesson in ParentContent.findAll(tag, attrs=SpecifiedAttrs):
                try:
                    url = lesson.get('href')
                    if url != None:
                        lessonLinks.append(url)
                except:
                    pass
            return lessonLinks 
        else:
            #Get's the actual resources - links to video and audio
            files = []
            if lessonFetch != 'Video':
                for file in ParentContent.findAll(tag, href=re.compile(SpecifiedAttrs)):
                    files.append([file.text.strip('\n').strip(),file['href']])
            else:
                for file in ParentContent.findAll(tag, attrs=SpecifiedAttrs):
                    videoLink = file.findAll('script', src=re.compile('link-to-resource'))[0]['src']
                    #converts jsonp file extension to json - more accesible
                    files.append(videoLink[:len(videoLink)-1])
            return files
​
    return [result, Count]
​
def program():
    #Head of POST request
    #should be replaced when entering another
    #website
    payload = {
        "email" : "SOMETHING",
        "password" : "SOMETHING",
        "csrfmiddlewaretoken" : "SOMETHING --> This token is called a csrf_token and can be found on webpages",
    }
    #Keeps me logged in
    session_requests = requests.Session()
    #Base urls
    login_url = "link"
    site_url = 'link'
    levels_url = 'link'
    result = session_requests.get(login_url)
    result = session_requests.post(
        login_url, 
        data = payload, 
        headers = dict(referer=login_url)
    )
    #Get levels page
    root = getContentOfPage(levels_url, session_requests)
    #Specifications
    levels = getLinksFromSite(root, 'div', {'class': 'course-stack'}, False, False)
    level = levels[0]
    count = levels[1]
    index = 0
​
    parameter = []
    #Message to the user for an overview
    for content in level:
        print(str(index) + ': ' + content)
        print(count[index][0].text + '\n')
        parameter.append([content, level[content]])
        index += 1
    #Download function
    def downloadSpecification(site_url, levels, session_requests):
        index = 0
        svar = input('Hvilken lesson har du lyst til å laste ned? \nAlt - press enter, én - tast inn nr, flere - tast inn nr med mellomrom: \n')
        if len(svar) > 1:
            index = svar.split(" ")
        elif len(svar) == 1:
            index = svar
        else:
            index =  [0,1,2,3,4,5,6]
        
        lessonCount = 0
        for i in index:
            levelName = levels[int(i)][0]
            saveInPATH = 'PATH'
            pageNumber = 1
            morePages = True
            saveInPATH += levelName
            while morePages == True:
                if pageNumber != 1:
                    #finds the next page of a website
                    page = site_url + levels[int(i)][1] + '/desc/?page=' + str(pageNumber)  
                else:
                    page = site_url + levels[int(i)][1]
                currentPage = getContentOfPage(page, session_requests)
                lessonLinks = getLinksFromSite(currentPage, 'a', {'class': 'parameter(s)'}, True, False)
                if len(lessonLinks) > 1:
                    try:
                        for lesson in range(len(lessonLinks)):
                            resources = getContentOfPage(site_url + lessonLinks[lesson], session_requests)
                            Audio = getLinksFromSite(resources, 'a', 'mp3', True, 'Audio')
                            audio = 0
                            for file in Audio:
                                #Downloads the audio file
                                urllib.request.urlretrieve(file[1], saveInPATH + '/Audio/'+file[0] + '/'+ levelName+'_'+ str(pageNumber)+'_'+str(lesson) +'_'+str(audio)+'_'+'.mp3')
                                print('saver ' + file[1] + ' in '+ saveInPATH + '/Audio/'+ file[0] +'/'+ levelName+'_'+ str(pageNumber)+'_'+str(lesson) +'_'+str(audio)+'_'+'.mp3')
                                audio += 1
                            try:
                                Video = getLinksFromSite(resources, 'div', {'class' : 'parameter'}, True, 'Video')
                                #Parses json
                                videoFile = json.load(urllib.request.urlopen(Video[0]))
                                videoURL = videoFile['media']['assets'][9]['url']
                                videoMP4 = videoURL[:len(videoURL)-3] + 'mp4'
                                #Downloads the video file
                                urllib.request.urlretrieve(videoMP4, saveInPATH + '/Video/' + levelName +'_'+str(pageNumber)+'_'+str(lesson)+'.mp4')
                                print('saver ' + videoMP4 + ' in '+ saveInPATH + '/Video/' + levelName+'_'+str(pageNumber)+'_'+str(lesson)+'.mp4')
                            except:
                                pass
                            lessonCount += 1
                        pageNumber += 1
                       
                    except:
                        lessonCount += 1
                        pageNumber += 1
                        pass
                else:
                    morePages = False
                    levelName = levels[int(i)][0]
        print('Ferdig! Lastet ned fra: ' + str(lessonCount))
​
    downloadSpecification(site_url, parameter, session_requests)
​
program()