import json
import re
import time

import requests
import ujson
from bs4 import BeautifulSoup
from flask import request, render_template

from app import app
from app import cache

session = requests.Session()


@app.route('/', methods=['GET'])
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
    try:
        page = session.get("https://www1.kickassanime.rs/api/frontpage_video_list")
        context = ujson.loads(page.content)
        return context
    except ConnectionError:
        time.sleep(3)
        frontPage()


@app.route('/anime_list/', methods=['GET'])
def animeList():
    context = fetchAnimeList()
    return render_template("animelist.html", content=context)


@cache.cached(timeout=14400, key_prefix="anime_list")
def fetchAnimeList():
    try:
        page = session.get("https://www2.kickassanime.rs/anime-list")
        soup = BeautifulSoup(page.content, 'html.parser')
        start = str(soup.find_all('script')[5]).index('\"animes\":')
        end = str(soup.find_all('script')[5]).index(',\"filters\"')
        script = str(soup.find_all('script')[5]).strip()[start:end].replace('\"animes\":', "")
        getContext = json.loads(script)
        return getContext
    except ConnectionError:
        time.sleep(3)
        fetchAnimeList()


@app.route('/genres/', methods=['GET'])
def genre():
    with open('app/static/genres.json') as f:
        context = json.load(f)
    return render_template("genres.html", content=context)


@cache.cached(timeout=3000)
@app.route('/player/', methods=['GET'])
def video():
    try:
        url = request.args['url']
        page = session.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        start = str(soup.find_all('script')[6]).index('\"episode\"')
        end = str(soup.find_all('script')[6]).index('|| {}')
        script = str(soup.find_all('script')[6]).strip()[start:end]
        jsonFy = ujson.loads("{" + script)
        link = jsonFy["episode"]["link1"]
        if not link:
            return {"status code": "Error no link found"}
        script = scrapPlayers(link)
        return render_template("videos.html", content=script)
    except ConnectionError:
        time.sleep(3)
        video()


def scrapPlayers(link):
    try:
        print(link)
        page = session.get(str(link))
        soup = BeautifulSoup(page.content, 'html.parser')
        print(page.content)
        try:
            start = str(soup.find_all('script')[3]).index('[{\"name\"')
            end = str(soup.find_all('script')[3]).index(';')
            script = str(soup.find_all('script')[3]).strip()[start:end]
            print(script)
            return script
        except ValueError:
            no_servers = [{
                "name": "Default",
                "src": link
            }]
            context = ujson.dumps(no_servers)
            return context
    except ConnectionError:
        time.sleep(3)
        frontPage()


@app.route('/search/')
def search():
    return render_template("search.html")


@app.route('/search/', methods=['POST'])
def search_post():
    query = request.form['query']
    try:
        if request.method == "POST":
            if len(query) <= 2:
                return "Please write atleast 3 characters"
            page = session.get("https://www2.kickassanime.rs/search?q=" + str(query))
            soup = BeautifulSoup(page.content, 'html.parser')
            start = str(soup.find_all('script')[5]).index('\"animes\":')
            end = str(soup.find_all('script')[5]).index(',\"query\"')
            context = str(soup.find_all('script')[5]).strip()[start:end].replace('\"animes\":', "")
            return render_template("search.html", content=context)
    except ConnectionError :
        time.sleep(3)
        search_post()


@cache.cached(timeout=400)
@app.route('/detail/')
def detail():
    url = request.args['url']
    removeEp = re.sub(r"|/episode-.*", "", url, flags=re.IGNORECASE)
    print(removeEp)
    try:
        page = session.get(removeEp, headers={"Referer": str(removeEp),
                                              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                                                            "rv:81.0) Gecko/20100101 Firefox/81.0"})
        soup = BeautifulSoup(page.content, 'html.parser')
        start = str(soup.find_all('script')[5]).index('\"anime\":')
        end = str(soup.find_all('script')[5]).index(',\"aid\"')
        script = str(soup.find_all('script')[5]).strip()[start:end].replace('\"anime\":', "")
        print("[" + script +"}]")
        context = ujson.loads("[" + str(script) + "}]")
        print(context)
        return render_template("detail.html", content=context)
    except ConnectionError:
        time.sleep(3)
        frontPage()


@app.route('/by_genre/', methods=['GET'])
def by_genre():
    by_genre = request.args['query']
    try:
        print("https://www2.kickassanime.rs" + str(by_genre))
        page = session.get("https://www2.kickassanime.rs" + str(by_genre))
        soup = BeautifulSoup(page.content, 'html.parser')
        start = str(soup.find_all('script')[5]).index('\"animes\":')
        end = str(soup.find_all('script')[5]).index(',\"ax\"')
        context = str(soup.find_all('script')[5]).strip()[start:end].replace('\"animes\":', "")
        return render_template("by_genre.html", content=context)
    except ConnectionError:
        time.sleep(3)
        by_genre()

