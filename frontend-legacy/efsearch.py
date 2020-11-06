import os
from flask import Flask, send_from_directory
from peewee import PostgresqlDatabase

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "efs-db")

application = Flask(__name__)
#DEBUG#application.debug = True
db = PostgresqlDatabase('efsearch', user='efs_db_user', password='efs_db_user_pwd', host=POSTGRES_HOST)

#import logging
#logger = logging.getLogger('peewee')
#logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)

from page_search import PageSearch

@application.route("/", methods=['GET'])
def root():
    db.connect()
    page = PageSearch()
    html = page.getHTML()
    db.close()
    return html

@application.route('/res/<path:path>')
def send_file(path):
    return send_from_directory('res', path)

@application.route('/robots.txt')
def send_robots():
    return send_from_directory('.', "robots.txt")
