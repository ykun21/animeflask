from bs4 import BeautifulSoup
import requests
import ujson
from flask import request, render_template
from app import app


@app.route('/player/', methods=['GET'])
def video():
    url = request.args['url']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    start = str(soup.find_all('script')[7]).index('\"episode\"')
    end = str(soup.find_all('script')[7]).index('|| {}')
    script = str(soup.find_all('script')[7]).strip()[start:end]
    jsonFy = ujson.loads("{" + script)
    link = jsonFy["episode"]["link1"]
    if not link:
        return {"status code": 404}
    page = requests.get(str(link))
    soup = BeautifulSoup(page.content, 'html.parser')
    start = str(soup.find_all('script')[3]).index('[{\"name\"')
    end = str(soup.find_all('script')[3]).index(';')
    script = str(soup.find_all('script')[3]).strip()[start:end]
    return render_template("videos.html", content=script)


@app.route('/home/', methods=['GET'])
def home():
    page = requests.get("https://www1.kickassanime.rs/api/frontpage_video_list")
    js = ujson.loads(page.content)
    print(page.content)
    context = js["data"]["all"]
    return render_template("home.html", content=context)


@app.route('/search/', methods=['GET'])
def search():
    return render_template("search.html")
