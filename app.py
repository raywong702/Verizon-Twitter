# all the imports
import os
import datetime
from pytz import timezone
from flask import Flask
from flask import render_template
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import twitter
#import test

# create our little application :)
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

from models import *

def get_last_time():
    result = Result.query.order_by(desc(Result.time)).first()
    return result.time

def is_data_stale():
    time_back = 1
    eastern = timezone('US/Eastern')
    now = datetime.datetime.now()
    time_check = now - datetime.timedelta(minutes = time_back)
    time_check = eastern.localize(time_check)
    if get_last_time() > time_check:
        return False
    else:
        return True 

def convert_results():
    entries = []
    hashtags = []
    users = []

    results = Result.query.order_by(desc(Result.time)).limit(100).all()

    for result in results:
        hashtags = result.json.get('entities').get('hashtags')
        users = result.json.get('entities').get('user_mentions')
        text = result.text
        text = twitter.style_text(text, hashtags, users)

        entry = {"time":result.time.strftime("%Y-%m-%d %H:%M:%S EST"),
                 "screen_name":result.screen_name,
                 "place":result.place,
                 "text":text
                }
        entries.append(entry)
    return entries


@app.route('/')
def index():
    if is_data_stale():
        twitter.get_tweets()
        twitter.get_stream()
        
    return render_template('index.html', entries = convert_results())

if __name__  == '__main__':
    app.debug = True
    app.run()

