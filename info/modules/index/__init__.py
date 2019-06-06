from flask import Blueprint


index_blu = Blueprint("index", __name__)

from .views import *


#
# @app.route('/')
# def index():
#     logging.debug("debug")
#     logging.error("error")
#     logging.warning(("warning"))
#     logging.info("info")
#     logging.fatal("fatal")
#
#     return 'Hello World'