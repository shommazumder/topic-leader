from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json, time, sys
import tweepy

class SListener(StreamListener):
    def __init__(self, api = None, fprefix = 'streamer'):
        self.api = api or API()
        self.counter = 0
        self.num_tweets = 0
        self.tweet_max = 10000
        self.fprefix = fprefix
        self.output = open('/Users/ShomMazumder/Desktop/DataMining/contentLeadership/streaming_data/'+fprefix+'.json','w+')
        self.delout = open('delete.txt', 'a')

    def on_data(self, data):
        #this function checks data for validity
        
        #turns off the stream once we hit tweet_max
        if self.counter >=self.tweet_max:
            return False
        if 'in_reply_to_status' in data:
            self.on_status(data)
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            print warning['message']
            return False

    def on_status(self,status):
        #this functions processes each individual tweet
        self.output.write(status+'\n')
        self.counter += 1
        if self.counter >= self.tweet_max:
            self.output.close()
            return False
        else:
            return True

    def on_delete(self, status_id, user_id):
        self.delout.write( str(status_id)+'\n')
        return

    def on_limit(self, track):
        sys.stderr.write(track+'\n')
        return

    def on_error(self, status_code):
        sys.stderr.write('Error: '+str(status_code)+'\n')
        return False

    def on_timeout(self):
        sys.stderr.write('Timeout, sleeping for 60 seconds...\n')
        time.sleep(60)
        return





