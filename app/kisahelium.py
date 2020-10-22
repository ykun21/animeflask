from bs4 import BeautifulSoup
import requests
import ujson
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


if __name__ == '__main__':
    app.run()
