from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from praw.models import MoreComments

from flask_cors import CORS
import praw
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
def sentiment_analyzer_scores(sentence):
	analyser = SentimentIntensityAnalyzer()
	score = analyser.polarity_scores(sentence)
	return score



            