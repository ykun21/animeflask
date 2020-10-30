from flask import Flask
from flask_caching import Cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "filesystem",
    'CACHE_DIR': 'cache',
    "CACHE_DEFAULT_TIMEOUT": 3000
}

app = Flask(__name__)

# cache config
app.config.from_mapping(config)
cache = Cache(app)

from app import views
