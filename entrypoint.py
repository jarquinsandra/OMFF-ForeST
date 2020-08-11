"""

AUTOR: jarquinsandra


"""
import os
from app import create_app
from flask import render_template
from waitress import serve


#These are used for config files in case it needs to be deployed to internet
#settings_module = os.getenv('APP_SETTINGS_MODULE')
#app = create_app(settings_module)
app=create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    #Configuration for waitress just with Windows otherwise use the information above
    serve(app, host='0.0.0.0', port=5000)
