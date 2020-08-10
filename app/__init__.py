"""

AUTOR: jarquinsandra


"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
#from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
url='mysql+pymysql://root:root@localhost:3306/Forest'

def create_app(settings_module):
    app = Flask(__name__)
    # Load the config file specified by the APP environment variable
    #app.config.from_object(settings_module)

    #Here you need to define the URI database, with the following data 'mysql+pymysql:user:password@host:port/database' you can change the data according to your needs
    app.config['SQLALCHEMY_DATABASE_URI']=url
    app.config['SECRET_KEY'] = '5e04a4955d8878191923e86fe6a0dfb24edb226c87d6c7787f35ba4698afc86e95cae409aebd47f7'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

    #Bootstrap(app)
    db.init_app(app)
    migrate.init_app(app, db)
     #Import Blueprints   
    from .search import search
    app.register_blueprint(search)

    from .landing import landing
    app.register_blueprint(landing)

    from .db_manager import db_manager
    app.register_blueprint(db_manager)

    #with app.app_context():

        # Create tables for our models
        #db.create_all()

        #return app
    register_error_handlers(app)

    return app

def register_error_handlers(app):

    @app.errorhandler(500)
    def base_error_handler(e):
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def error_404_handler(e):
        return render_template('404.html'), 404



