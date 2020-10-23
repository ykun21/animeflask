from flask import Flask
from flask_caching import Cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)

# cache config
app.config.from_mapping(config)
cache = Cache(app)

from app import views
