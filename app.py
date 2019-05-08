from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import praw
app = Flask(__name__)

@app.route("/")
def hello():
	return "App is running!"


@app.route("/api/<string:input>")
def api_call(input):
	print(input)
	return run_reddit() + " Input: " + input
def run_reddit(): 

	reddit = praw.Reddit(client_id='hdi4lt8k2KdlWg',
		client_secret='DoP1QLPV9BbcL5fjWmtK1gEap5w',
		user_agent='CS 410 Final')
	shaleen = reddit.redditor('ecelol')
	value = shaleen.link_karma
	s = sentiment_analyzer_scores(str(value))
#print(s)
	return str(s)
def sentiment_analyzer_scores(sentence):
	analyser = SentimentIntensityAnalyzer()
	score = analyser.polarity_scores(sentence)
	return score