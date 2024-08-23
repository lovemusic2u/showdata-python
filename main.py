from flask import Flask,render_template,send_from_directory
from showdata import *
from datetime import timedelta

app = Flask(__name__)

app.register_blueprint(showdata)
app.secret_key = ""
app.permanent_session_lifetime = timedelta(hours=1)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

