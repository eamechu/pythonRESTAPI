from flask import Flask
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL

app = Flask(__name__)
api = Api(app)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'dbpyapi'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

# Initialize Database connection
conn = mysql.connect()

# create database cursor
cursor = conn.cursor()


# User creation class
class CreateUser(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Email address to create user')
            parser.add_argument('password', type=str, help='Password to create user')
            args = parser.parse_args()

            _userEmail = args['email']
            _userPassword = args['password']

            cursor.callproc('spCreateUser', (_userEmail, _userPassword))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return {'StatusCode': '200', 'Message': 'User creation success'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0])}

        except Exception as e:
            return {'error': str(e)}


api.add_resource(CreateUser, '/CreateUser')


# Authentication Class
class AuthenticateUser(Resource):
    def post(self):
        try:
            # Parse the arguments

            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Email address for Authentication')
            parser.add_argument('password', type=str, help='Password for Authentication')
            args = parser.parse_args()

            _userEmail = args['email']
            _userPassword = args['password']

            cursor.callproc('sp_AuthenticateUser', (_userEmail,))
            data = cursor.fetchall()

            if len(data) > 0:
                if str(data[0][2]) == _userPassword:
                    return {'status': 200, 'UserId': str(data[0][0])}
                else:
                    return {'status': 100, 'message': 'Authentication failure'}

        except Exception as e:
            return {'error': str(e)}


api.add_resource(AuthenticateUser, '/AuthenticateUser')


# Add Items Class
class AddItem(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=str)
            parser.add_argument('item', type=str)
            args = parser.parse_args()

            _userId = args['id']
            _item = args['item']

            cursor.callproc('sp_AddItems',(_userId,_item))
            data = cursor.fetchall()

            conn.commit()
            return {'StatusCode': '200', 'Message': 'Success'}

        except Exception as e:
            return {'error': str(e)}


# GetAll Items
class GetAllItems(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=str)
            args = parser.parse_args()

            _userId = args['id']

            cursor.callproc('sp_GetAllItems',(_userId,))
            data = cursor.fetchall()

            items_list=[];
            for item in data:
                i = {
                    'Id':item[0],
                    'Item':item[1]
                }
                items_list.append(i)

            return {'StatusCode':'200','Items':items_list}

        except Exception as e:
            return {'error': str(e)}


if __name__ == '__main__':
    app.run(debug=True)


