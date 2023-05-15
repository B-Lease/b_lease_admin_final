from flask import Flask
from flask_restful import Api
from flask_mysqldb import MySQL
from flask_cors import CORS


#--------------------------------------------------------------------------------
#Configurations of the Server Admin are found here
#--------------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "b-lease2022"
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3308
app.config['MYSQL_USER'] = 'root'

#app.config['MYSQL_PASSWORD'] = 'Kyla2001!!'
#app.config['MYSQL_PASSWORD'] = 'nathaniel'
app.config['MYSQL_PASSWORD'] = 'project2023!'

app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_DB'] = 'b_lease'


mysql = MySQL(app)
api = Api(app)
CORS(app)










