from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from praw.models import MoreComments

from flask_cors import CORS
import praw

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob
from nltk import sent_tokenize

import re 
import datetime
import smtplib, ssl
import getpass
#import matplotlib.pyplot as plt

# from ipywidgets import interactive
# import numpy as np
# import plotly
# import plotly.graph_objs as go

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
import json
import plotly

import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)



@app.route("/")
#def hello():

#	return "App is running!"

def default_graphs(): 
    # rng = pd.date_range('1/1/2011', periods=7500, freq='H')
    #ts = pd.Series(np.random.randn(len(datetimes)), index=datetimes)
    global neg
    global neu
    global pos
    global st 
    graphs = [
        dict(
            data=[
                dict(
                    values = [pos, neu, neg],
                    labels = ["positive", "neutral", "negative"],
                    type='pie'
                ),
            ],
            layout=dict(
                title='Sentiment Analysis'
            )
        ), 

        dict(
            data=[
                dict(
                    values = [st, 1-st],
                    labels = ["subjectivity", "objectivity"],
                    type='pie'
                ),
            ],
            layout=dict(
                title='Subjectivity Analysis'
            )
        )
    ]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('layouts/index.html',
                           ids=ids,
                           graphJSON=graphJSON)



def index(datetimes, polarities):
    # rng = pd.date_range('1/1/2011', periods=7500, freq='H')
    ts = pd.Series(np.random.randn(len(datetimes)), index=datetimes)

    graphs = [
        # dict(
        #     data=[
        #         dict(
        #             x=[1, 2, 3],
        #             y=[10, 20, 30],
        #             type='scatter'
        #         ),
        #     ],
        #     layout=dict(
        #         title='first graph'
        #     )
        # ),

        # dict(
        #     data=[
        #         dict(
        #             x=[1, 3, 5],
        #             y=[10, 50, 30],
        #             type='bar'
        #         ),
        #     ],
        #     layout=dict(
        #         title='second graph'
        #     )
        # ),

        dict(
            data=[
                dict(
                    x=ts.index,  # Can use the pandas data structures directly
                    y=polarities
                )
            ]
        )

    ]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('layouts/index.html',
                           ids=ids,
                           graphJSON=graphJSON)
    #return str(rng) + " SPACED OUT " + str(ts)

@app.route("/graph/<string:input_param>/<string:subreddit>/<int:num_comments>/<int:num_posts>/<string:time_period>")
def graph_routine(input_param, subreddit, num_comments, num_posts, time_period):
    reddit = praw.Reddit(client_id='hdi4lt8k2KdlWg',
        client_secret='DoP1QLPV9BbcL5fjWmtK1gEap5w',
        user_agent='CS 410 Final')
    cur_comments = 0
    post_counter = 0
    max_comments = num_comments
    if(time_period == "all time"):
        submissions = reddit.subreddit(subreddit).top(limit=1000)
    else:
        submissions = reddit.subreddit(subreddit).top(limit=1000, time_filter=time_period)
    keyword = input_param
    polarities = []
    times = []
    for submission in submissions:
        if post_counter > num_posts:
            break
        if keyword.lower() in submission.title.lower():
            post_counter += 1

            pos = 0
            neg = 0
            neu = 0
            st = 0 
            count = 0
            for top_level_comment in submission.comments:

                if isinstance(top_level_comment, MoreComments):
                    continue
                scores = sentiment_analyzer_scores(top_level_comment.body)
                st += TextBlob(top_level_comment.body).sentiment.subjectivity
                if(scores['pos'] > scores['neg']):
                    pos += 1
                elif(scores['neg'] > scores['pos']):
                    neg += 1
                else: neu += 1

                count += 1


                cur_comments += 1
                if(count >= max_comments):
                    break
            temp = pos/cur_comments - neg/cur_comments
            polarities.append(temp)
            times.append(datetime.datetime.fromtimestamp(submission.created))
        print(cur_comments)
    print(polarities)
    print(times)
    if cur_comments == 0:
        return "No comments found with the specified criteria."
    list1, list2 = zip(*sorted(zip(times, polarities)))
    return index(pd.DatetimeIndex(list1), list2)

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
	global pos
	global neg
	global neu
	global st 

	pos = 0
	neg = 0
	neu = 0
	st = 0 

	for submission in reddit.subreddit(subreddit).top(limit=1000, time_filter='week'):
	    if keyword.lower() in submission.title.lower():
	        for top_level_comment in submission.comments:
	            if isinstance(top_level_comment, MoreComments):
	                continue
	            scores = sentiment_analyzer_scores(top_level_comment.body)
	            st += TextBlob(top_level_comment.body).sentiment.subjectivity
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
	print(st/cur_comments)
	st = st/cur_comments
	return "Negative: " + str(round((100 *neg)/cur_comments)) + "% Positive: " + str(round((100*pos)/cur_comments)) + "%" + " Subjectivity: " + str(round(st*100)) + "%"    


#print(s)
	# return str(s)


@app.route("/twitter/<string:keyword>/<int:max_comments>")
def twtter_call_api(keyword, max_comments):
	return twitter(keyword, max_comments) + " Keyword, max_comments: " + keyword + ", " + str(max_comments)



neg = 0
pos = 0
neu = 0
tweet_count = 0
post = 0
negt = 0
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
            #print(tweet)
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

                global neu
                neu = self.neutral
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
    global st
    st = st/tweet_count

    return "Negative: " + str(round((100 *neg)/tweet_count)) + "% Positive: " + str(round((100*pos)/tweet_count)) + "%" + " Subjectivity: " + str(round(st*100)) + "%"    




def sentiment_analyzer_scores(sentence):
	analyser = SentimentIntensityAnalyzer()
	score = analyser.polarity_scores(sentence)
	return score

@app.route("/site/<string:input_string>")
def csite_call_api(input_string):
	global neg 
	global pos 
	global neu 
	global st 

	neg = 0
	neu = 0
	pos = 0
	st = 0
	sentence_count = 0
	sentences = re.split('[?.!]', input_string)
	for sentence in sentences:
		st += TextBlob(sentence).sentiment.subjectivity
		if(len(sentence) == 0):
			continue
		scores = sentiment_analyzer_scores(sentence)
		if scores['pos'] > scores['neg']:
			pos += 1
		elif scores['pos'] < scores['neg']:
			neg += 1
		else: neu += 1
		sentence_count += 1
	if sentence_count == 0:
		return "No sentences found, be sure to select some text"
	st = st/sentence_count
	return "Negative: " + str(round((100 *neg)/sentence_count)) + "% Positive: " + str(round((100*pos)/sentence_count)) + "%" + " Subjectivity: " + str(round(st*100)) + "%"    


@app.route("/server/<string:data>")
def send_email(data):
    sender_email = "peterDiesInInfinityWar@gmail.com"
    receiver_email = "peterDiesInInfinityWar@gmail.com"
    server = str(request.headers["Referer"])
    server = server.replace(":", "")
    message = "\n" + "URL is "  + server + "\n" + data
    port = 465  # For SSL
    password = "1ron M@n" 
    #print("the requests are: ")
    #print(request.headers)
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("peterDiesInInfinityWar@gmail.com", password)
        server.sendmail(sender_email, receiver_email, message)

    return "ok"