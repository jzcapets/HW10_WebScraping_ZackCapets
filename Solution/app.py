from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import mars_scraper

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

# Or set inline
# mongo = PyMongo(app, uri="mongodb://localhost:27017/craigslist_app")


@app.route("/")
def index():
    mars = mongo.db.marsdisplay.find_one()
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def scraper():
    mars = mongo.db.marsdisplay
    marsdata = mars_scraper.scrape()
    print(marsdata)
    mars.update({}, marsdata, upsert=True)
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)
