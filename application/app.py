from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
db_uri = <INSERT DATABASE URI HERE>
app.config['SQLALCHEMY_DATABASE_URI']  =db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    import routes.routing

if __name__ == '__main__':
    app.run(debug=True, port=5000, host=('0.0.0.0'))
