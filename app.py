from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from praw.models import MoreComments

from flask_cors import CORS
import praw

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
	return "App is running!"


@app.route("/reddit/<string:subreddit>/<int:max_comments>")
def api_call2(subreddit, max_comments):
	keyword = ""
	return run_reddit(keyword, subreddit, max_comments) + " Subreddit: " + subreddit


@app.route("/reddit/<string:keyword>/<string:subreddit>/<int:max_comments>")
def api_call(keyword, subreddit, max_comments):
	return run_reddit(keyword, subreddit, max_comments) + " Keyword, Subreddit: " + keyword + ", " + subreddit

def run_reddit(keyword, subreddit, max_comments): 

	reddit = praw.Reddit(client_id='hdi4lt8k2KdlWg',
		client_secret='DoP1QLPV9BbcL5fjWmtK1gEap5w',
		user_agent='CS 410 Final')

	# max_comments = 1000
	cur_comments = 0
	negative = 0
	positive = 0
	neutral = 0

	pos = 0
	neg = 0
	neu = 0

	for submission in reddit.subreddit(subreddit).top(limit=1000, time_filter='week'):
	    if keyword.lower() in submission.title.lower():
	        for top_level_comment in submission.comments:
	            if isinstance(top_level_comment, MoreComments):
	                continue
	            scores = sentiment_analyzer_scores(top_level_comment.body)
	            if(scores['pos'] > scores['neg']):
	                pos += 1
	            elif(scores['neg'] > scores['pos']):
	                neg += 1
	            else: neu += 1
	            negative += scores['neg']
	            positive += scores['pos']
	            neutral += scores['neu']
	            
	            
	            cur_comments += 1
	    print(cur_comments)
	    if cur_comments > max_comments:
	        break
	if cur_comments == 0:
		return "No comments found with the specified criteria."
	print(pos, neg, neu)
	print(neg/cur_comments)
	print(pos/cur_comments)
	return "Negative: " + str(round((100 *neg)/cur_comments)) + "% Positive: " + str(round((100*pos)/cur_comments)) + "%"


#print(s)
	return str(s)


@app.route("/twitter/<string:keyword>/<int:max_comments>")
def twtter_call_api(keyword, max_comments):
	return twitter(keyword, max_comments) + " Keyword, max_comments: " + keyword + ", " + str(max_comments)

neg = 0
pos = 0
neu = 0
tweet_count = 0
pt = 0
st = 0

def twitter(keyword, max_comments): 

    #consumer key, consumer secret, access token, access secret.
    ckey="bxh7iOBWAR5evT8dHOJH7RIDi"
    csecret="daPXgwanOTF4zxSqU2iNxMozDtUHBrP0IYw13pbDAnRl0xkhXb"
    atoken="981273264747089920-8l8CNBeZ2jitSnxc6Ve1PqVXRVHNhjA"
    asecret="Hvj1y3VjboNyEfHeWnaZrN8gMs4g3N7cjtbv40m2XsbPi"



    
    class listener(StreamListener):
        def __init__(self):
            super().__init__()
            self.counter = 0
            self.limit = max_comments
            self.positive = 0
            self.negative = 0
            self.neutral = 0
            self.pt = 0
            self.nt = 0
            self.polarity = 0
            self.subjectivity = 0
        
        def on_status(self, status):
            print("hi")
        def on_data(self, data):

            all_data = json.loads(data)

            tweet = all_data["text"]
            print(tweet)
            scores = sentiment_analyzer_scores(tweet)
            if(scores['pos'] > scores['neg']):
                self.positive += 1
            elif(scores['neg'] > scores['pos']):
                self.negative += 1
            else: self.neutral += 1
            scoresT = TextBlob(tweet).sentiment
            if scoresT.subjectivity > 0.3:
                if scoresT.polarity > 0:
                    self.pt += 1
                elif scoresT.polarity < 0:
                    self.nt += 1
            self.polarity += scoresT.polarity
            self.subjectivity += scoresT.subjectivity


            if(self.counter > self.limit):
                twitterStream.disconnect()
                global neg
                neg = self.negative
                global pos 
                pos = self.positive

                global tweet_count
                tweet_count = self.counter+1

                global post
                global negt
                post = self.pt
                negt = self.nt
                
                global pt
                global st
                pt = self.polarity
                st = self.subjectivity
                
            self.counter += 1

            return True

        def on_error(self, status):
            print(status)

    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)



    twitterStream = Stream(auth, listener())
    twitterStream.filter(track=[keyword])

    print(neg/tweet_count)
    print(pos/tweet_count)

    print(pt, st/tweet_count)

    return "Negative: " + str(round((100 *neg)/tweet_count)) + "% Positive: " + str(round((100*pos)/tweet_count)) + "%" + " Subjectivity: " + str(round((st*100)/tweet_count)) + "%"    




def sentiment_analyzer_scores(sentence):
	analyser = SentimentIntensityAnalyzer()
	score = analyser.polarity_scores(sentence)
	return score



            