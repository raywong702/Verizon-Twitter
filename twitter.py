import os
import datetime
import re
import json
from pytz import timezone
import tweepy
from app import db
import models


# Consumer keys and access tokens, used for OAuth
consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']
 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

# Setting limits
max_tweets = 100

# Limit to US
#places = api.geo_search(query = "USA", granularity = "country")
#place_id = places[0].id
#us = " place:{}".format(place_id)

# Setting timezones
eastern = timezone('US/Eastern')
utc = timezone('UTC')

# Ellipses from retweets
ellipses = u"\u2026"
#ellipses = ellipses.encode('utf-8')

def get_tweets():
    hashtags = []
    users = []

    # Calculating the current date and using it as a query limit
    now = datetime.datetime.now()
    year= now.year
    month = now.month
    day = now.day
    date = ("{}-{}-{}".format(year, month, day))
    since = " since:{}".format(date)

    # Build query
    query = "verizon vzw #verizon #vzw"
    query = query.split()
    query = " OR ".join(query)
#    query += us
    query += since

    # Query Twitter API
    results = api.search(q = query, lang = "en", result_type = "recent", count = max_tweets)

    # Parse Twitter Results
    for tweet in results:
        # Convert time from UTC to Eastern
        created_at = tweet.created_at
        utc_created_at = utc.localize(created_at)
        est_created_at = utc_created_at.astimezone(eastern)
        est_created_at = est_created_at.replace(tzinfo = None)
        time = est_created_at.strftime("%Y-%m-%d %H:%M:%S EST")

        place = tweet.place
        if place is not None:
            place = place.full_name
#            print(place)
        else:
            place = ""

        text = tweet.text
        user = tweet.user.screen_name
        hashtags = tweet.entities.get('hashtags')
        users = tweet.entities.get('user_mentions')

        # json debugging
        #print(json.dumps(tweet._json, indent=4, sort_keys=True))
        #if "@" in text:
            #print(json.dumps(tweet._json, indent=4, sort_keys=True))
            #break

        # Filling in ellipses which were broken up retweets
        #if ellipses in text.encode('utf-8'):
        if ellipses in text:
            try:
                if tweet.retweeted_status:
                    retweet = tweet.retweeted_status.text
#                    left_text = text.encode('utf-8')
                    left_text = text
#                    print(left_text)
                    left_text = left_text[:left_text.rindex(ellipses)]
#                    print(left_text)
#                    print(retweet)
                    if " " in left_text:
                        last_word = left_text[left_text.rindex(" "):]
                        missing = retweet[retweet.rindex(last_word) + len(last_word):]
                        left_text += missing
                    else:
                        missing = retweet[retween.rindex(text) + len(text):]
                        left_text += missing
                    text = left_text
                    print(text)
                    print("")
            except:
                pass


        print("{} ::: {} ::: {} ::: {}".format(time, user, place, text))
        print("")

        # Build DB
        row = models.Result(est_created_at, user, place, text, tweet._json)
        try:
            db.session.add(row)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()



# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)
        #print(json.dumps(tweet, indent=4, sort_keys=True))


        #Convert time from UTC to Eastern
        created_at = tweet['created_at']
        created_at = created_at.replace(" +0000", "")
        created_at = datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S %Y")
        utc_created_at = utc.localize(created_at)
        est_created_at = utc_created_at.astimezone(eastern)
        est_created_at = est_created_at.replace(tzinfo = None)
        time = est_created_at.strftime("%Y-%m-%d %H:%M:%S EST")

        place = tweet['place']
        if place is not None:
            place = place['full_name']
        else:
            place = ""

        text = tweet['text']
#        text = text.encode('utf-8')

        user = tweet['user'].get('screen_name')


        # Filling in ellipses which were broken up retweets
        if ellipses in text:
            try:
                if tweet['retweeted_status']:
                    #print(text)
                    #print("***********")
                    retweet = tweet['retweeted_status']['text']
                    text = text[:text.rindex(ellipses)]
                    if " " in text:
                        last_word = text[text.rindex(" "):]
                        missing = retweet[retweet.rindex(last_word) + len(last_word):]
                        text += missing
                    else:
                        missing = retweet[retween.rindex(text) + len(text):]
                        text += missing
            except:
                pass


        print("{} ::: {} ::: {} ::: {}".format(time, user, place, text))
        print("")
        

        # Build DB
        row = models.Result(est_created_at, user, place, text, tweet)
        try:
            db.session.add(row)
            db.session.commit()
        except:
            db.session.rollback()

        return True

    def on_error(self, status):
        print(status)







def get_stream():
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = tweepy.Stream(auth, l)
    stream.filter(track=['verizon', 'vzw'], languages=['en'], async = True)




# Format text for html
def style_text(value, hashtags, users):
    # Transform URLs to html links
    text = replace_url_to_link(value)

    # User styling
    for user in users:
        text = replace_user(text, user.get('screen_name'))

    # Hashtag styling
    for hashtag in hashtags:
        text = replace_hashtag(text, hashtag.get('text'))
    
    return text



# Replace users with span
def replace_user(value, user):
    screen_name = "@" + user
    href = ("<a href='https://twitter.com/" + 
            user + 
            "' class='screen_name' target='_blank'>" +
            screen_name + 
            "</a>")
    return value.replace(screen_name, href, 1)

# Replace hashtag with span
def replace_hashtag(value, tag):
    hashtag = "#" + tag
    href = ("<a href='https://twitter.com/hashtag/" + 
            tag + 
            "?src=hash' class='hashtag' target='_blank'>" + 
            hashtag + 
            "</a>")
    return value.replace(hashtag, href, 1)
    
# Replace url to link
def replace_url_to_link(value):
    urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", 
                      re.MULTILINE|re.UNICODE)
    value = urls.sub(r'<a href="\1" target="_blank">\1</a>', value)
    return value



if __name__ == '__main__':
    get_tweets()
    get_stream()

