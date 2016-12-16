import tweepy
import sys
import os

os.chdir('c:\\Users\\seanm\\')

consumer_key = 'hKX1hNCAGdqnjlxMYNuwdc2Ii'
consumer_secret = 'eoZIHD4yO1KW17FuxkBS7FQ6OLcMoTNNzMv1N2IPu83CSNInGV'
access_token = '807660304930738176-faZoQrZ8aKBVlJFdtz5EcGcpCsqonvi'
access_token_secret = 'AsUrsMLceooTaDhOYtHdHcEPJE9BQo9EvzvlvzP3jsNII'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


class StdOutListener(tweepy.StreamListener):

    def on_status(self, status):
        f = open('immigration.txt', 'a')
        print('***Tweet Text***')
        print(status.text.encode("utf-8"))
        f.write(str(status.text.encode("utf-8")))
        f.write('\n')
        if status.retweeted == True:
            print('***Retweet***')
            f.write('Retweet = True \n')
        else:
            f.write('Retweet = False \n')
        f.close()

        #for hashtag in status.entries['hashtags']:
            #print(hashtag['text'])

        return True

    def on_error(self, status_code):
        print('Error: ' + str(status_code))
        return False

    def on_timeout(self):
        print('Timeout')
        return False

if __name__ == '__main__':
    listener = StdOutListener()

    stream = tweepy.Stream(auth, listener)
    stream.filter(track=['immigration'])
