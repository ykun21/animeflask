import json

import requests
import ujson
from bs4 import BeautifulSoup
from flask import request, render_template

from app import app
from app import cache

session = requests.Session()


@app.route('/home/', methods=['GET'])
def home():
    getContext = frontPage()
    context = getContext["data"]["all"]
    return render_template("home.html", content=context)


@app.route("/recent_sub/")
def recentSub():
    getContext = frontPage()
    context = getContext["data"]["sub"]
    return render_template("recentsub.html", content=context)


@app.route("/recent_dub/")
def recentDub():
    getContext = frontPage()
    context = getContext["data"]["dub"]
    return render_template("recentdub.html", content=context)


@cache.cached(timeout=14400, key_prefix="frontpage")
def frontPage():
    page = session.get("https://www1.kickassanime.rs/api/frontpage_video_list")
    context = ujson.loads(page.content)
    return context


@app.route('/anime_list/', methods=['GET'])
def animeList():
    context = fetchAnimeList()
    return render_template("animelist.html", content=context)


@cache.cached(timeout=14400, key_prefix="anime_list")
def fetchAnimeList():
    page = session.get("https://www1.kickassanime.rs/anime-list")
    soup = BeautifulSoup(page.content, 'html.parser')
    start = str(soup.find_all('script')[6]).index('\"animes\":')
    end = str(soup.find_all('script')[6]).index(',\"filters\"')
    script = str(soup.find_all('script')[6]).strip()[start:end].replace('\"animes\":', "")
    getContext = json.loads(script)
    return getContext


@cache.cached(timeout=100)
@app.route('/player/', methods=['GET'])
def video():
    url = request.args['url']
    page = session.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    start = str(soup.find_all('script')[7]).index('\"episode\"')
    end = str(soup.find_all('script')[7]).index('|| {}')
    script = str(soup.find_all('script')[7]).strip()[start:end]
    jsonFy = ujson.loads("{" + script)
    link = jsonFy["episode"]["link1"]
    if not link:
        return {"status code": 404}
    script = scrapPlayers(link)
    return render_template("videos.html", content=script)


def scrapPlayers(link):
    page = session.get(str(link))
    soup = BeautifulSoup(page.content, 'html.parser')
    start = str(soup.find_all('script')[3]).index('[{\"name\"')
    end = str(soup.find_all('script')[3]).index(';')
    script = str(soup.find_all('script')[3]).strip()[start:end]
    print(script)
    return script


@app.route('/search/')
def search():
    return render_template("search.html")


@app.route('/search/', methods=['POST'])
def search_post():
    query = request.form['query']
    if request.method == "POST":
        if len(query) <= 2:
            return "Please write atleast 3 characters"
        page = session.get("https://www1.kickassanime.rs/search?q=" + str(query))
        soup = BeautifulSoup(page.content, 'html.parser')
        start = str(soup.find_all('script')[6]).index('\"animes\":')
        end = str(soup.find_all('script')[6]).index(',\"query\"')
        context = str(soup.find_all('script')[6]).strip()[start:end].replace('\"animes\":', "")
        return render_template("search.html", content=context)


@app.route('/detail/<url>/')
def detail(url):
    page = session.get(url)
    print(page.content)