from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '<52f2f7bbd0899acac4c4cc57bad53e4bc96af3abc9128ff2>'

# Uploaded file folder setting
# UPLOAD_FOLDER = 'blog/static/img/'
UPLOAD_FOLDER = 'aat/static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# suppress SQLAlchemy warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB Connection
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c22011528:Twente0508$@csmysql.cs.cf.ac.uk:3306' \
#                                         '/c22011528_aat'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c22075165:Js139437jsn36879!@csmysql.cs.cf.ac.uk:3306/c22075165_aat'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

from aat import models
from aat import routes

