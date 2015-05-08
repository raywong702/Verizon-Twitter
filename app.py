# all the imports
import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import twitter

# create our little application :)
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)


from models import *

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
    twitter.get_tweets()
    return render_template('index.html', entries = convert_results())

if __name__  == '__main__':
    app.debug = True
    app.run()
