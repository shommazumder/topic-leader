from urllib2 import *
from urllib import *
from json import *
from urlparse import urlparse
from sets import Set
from xml.etree import ElementTree as ET
from lxml import etree
import tweepy
import csv
from progressbar import *
import time
import sys
import codecs
import os
from slistener import SListener
import json

#ask user for the url of the story that they want to analyze
isDone = False
storyUrls = []
while (isDone==False):
    storyUrls.append(raw_input('Enter the story url: '))
    done = raw_input('Would you like to enter another url? (Y/n) ')
    if (done=='n'):
        isDone = True
    elif (len(storyUrls)>=10):
        isDone = True

#extracting the story ids from the urls
storyIds = []
for url in storyUrls:
    if url.split('/')[3]=='blogs':
        storyIds.append(url.split('/')[8])
    else:
        storyIds.append(url.split('/')[6])

#fetch xml data for each storyId in order to retrieve associated tags
nprXML = 'http://www.npr.org/xstory/'
tags = Set([])
for id in storyIds:
    xmlOpen = nprXML+id
    xmlResponse = (urlopen(xmlOpen).read()).strip()
    value = etree.fromstring(xmlResponse)
    parsed = value.xpath('parent[@parentTypeId=24 and @relTypeId=20]/title')
    for element in parsed:
        tags.add(element.text)

#initializing news org url data
nprCount = 0
yahooCount = 0
cnnCount = 0
huffpoCount = 0
foxCount = 0 
nytimesCount = 0
wapoCount = 0
bbcCount = 0
guardCount = 0
voxCount = 0
buzzCount = 0
googleCount = 0
youtubeCount = 0
wsjCount = 0
reutersCount = 0
abcCount = 0

news_orgs = {'NPR': {'url': 'npr', 'count': nprCount},
             'Yahoo! News': {'url': 'news.yahoo', 'count': yahooCount},
             'CNN': {'url': 'cnn', 'count': cnnCount},
             'HuffPo': {'url': 'huffingtonpost', 'count': huffpoCount},
             'Fox News': {'url': 'foxnews', 'count': foxCount},
             'New York Times': {'url': 'nytimes', 'count': nytimesCount},
             'WaPo': {'url': 'washingtonpost', 'count': wapoCount},
             'BBC News (World)': {'url': 'bbc', 'count': bbcCount},
             'The Guardian': {'url': 'theguardian', 'count': guardCount},
             'Vox': {'url': 'vox', 'count': voxCount},
             'Buzzfeed': {'url': 'buzzfeed', 'count': buzzCount},
             'Google News': {'url': 'google', 'count': googleCount},
             'YouTube': {'url': 'youtube', 'count': youtubeCount},
             'Wall Street Journal': {'url': 'wsj', 'count': wsjCount},
             'Reuters': {'url': 'reuters', 'count': reutersCount},
             'ABC News': {'url': 'abcnews', 'count': abcCount}
             }

#Twitter credentials
#you'll have to register with Twitter to get your OAuth Credentials 
consumer_key = 'CONSUMER KEY'
consumer_secret = 'CONSUMER SECRET'
access_token_key = 'ACCESS TOKEN KEY'
access_token_secret = 'ACCESS TOKEN SECRET'

#initialize twitter api
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

#generating twitter search query based on stories inputed
rawQuery=''
track = []
for tag in tags:
    track.append(tag)
    rawQuery+=(' '+tag+' OR')

#begin streaming tweets
print 'fetching tweets'

listen = SListener(api, 'tweetDataBusiness')
stream = tweepy.streaming.Stream(auth, listen)
print 'Streaming started...'

try:
    stream.filter(track=track)
except IOError as e:
    print e.strerror
except:
    print sys.exc_info()[0]
    print 'error!'
    stream.disconnect()

#this batch of code stores each tweet as a json file in your working directory
streamed_tweets = []
fileName = 'NAME FILE HERE'
with open(fileName+'.json') as json_file:
    for line in json_file:
        line = line.strip()
        try:
            streamed_tweets.append(json.loads(line))
        except:
            pass

#this batch of code resolves all urls
urls = []
print "searching through tweets"
pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()], maxval=len(streamed_tweets)+1)
pbar.start()
i = 0

tweetCount = 0
for tweet in streamed_tweets:
    try:
        if tweet['entities']['urls']:
            sock = urlopen(tweet['entities']['urls'][0]['expanded_url'].encode('utf-8'))
            urls.append(sock.url)
            sock.close()
            i+=1
            pbar.update(i+1)
            tweetCount+=1
    except:
        continue
pbar.finish()
print "finished going through all "+str(tweetCount)+" of tweets with urls. generating counts"

#parsing urls and counting number of shares
for url in urls:
    print url
    for org in news_orgs:
        newsSubstring = news_orgs[org]['url']
        if newsSubstring in urlparse(url).netloc:
            news_orgs[org]['count']+=1

#printing out url count
print "Keywords: "+'\n'
print tags
for org in news_orgs:
    print org+" has "+str(news_orgs[org]['count'])



