from flask import Flask, render_template
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/meeting')
def meeting():
    return render_template('meeting_room.html')

@app.route('/write')
def write():
    return render_template('write_page.html')

@app.route('/post')
def post():
    return render_template('post_page.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)