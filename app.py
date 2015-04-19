# all the imports
from flask import Flask
from flask import render_template
from flask import url_for
import twitter

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('index.html', entries = twitter.get_tweets())

if __name__  == '__main__':
    app.debug = True
    app.run()