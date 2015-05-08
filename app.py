# all the imports
import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
#import twitter

# create our little application :)
app = Flask(__name__)
###app.config.from_object(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)


from models import *

@app.route('/')
def index():
###    print("hello world")
###    return render_template('index.html', entries = twitter.get_tweets())

#     twitter.get_tweets()
      return render_template('index.html', entries = Result.query.order_by(desc(Result.time)).limit(100).all())

if __name__  == '__main__':
    app.debug = True
    app.run()
