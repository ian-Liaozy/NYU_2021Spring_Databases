from flask import Flask, session, request, render_template, redirect
from mysql_tool import MySQLTool
from config import *
from hashlib import md5
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

mt = MySQLTool()


@app.route('/register/customer/', methods=['POST', 'GET'])
def register_customer():
    if request.method == 'GET':
        return 'register_customer_get'
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        building_number = request.form.get('building_number')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        phone_number = request.form.get('phone_number')
        passport_number = request.form.get('passport_number')
        passport_expiration = request.form.get('passport_expiration')
        passport_country = request.form.get('passport_country')
        dob = request.form.get('date_of_birth')

        if mt.root_check_duplicates(table='customer', attribute='email', value=email, user='root'):
            # duplicate
            # TODO
            return 'duplicate user'

        else:
            md5_pass = md5(password.encode('utf-8')).hexdigest()
            mt.root_insert(user='root', table='customer', value=[email, name, md5_pass, building_number,
                                                                 street, city, state, phone_number, passport_number,
                                                                 passport_expiration, passport_country, dob])
            # inform user
            # TODO
            session['user'] = email + ":C"
            return redirect('/home/', code=302, Response=None)


@app.route('/register/agent/', methods=['POST', 'GET'])
def register_agent():
    if request.method == 'GET':
        return render_template('register_agent.html')

    else:
        email = request.form.get('email')
        password = request.form.get('password')

        # check duplicate
        if mt.root_check_duplicates(table='booking_agent', attribute='email', value=email, user='root'):
            # duplicate
            # TODO
            return 'duplicate user'

        else:
            md5_pass = md5(password.encode('utf-8')).hexdigest()
            agent_id = mt.root_get_new_agent_id(user='root')
            mt.root_insert(user='root', table='booking_agent', value=[email, md5_pass, agent_id])

            # inform user
            # TODO
            session['user'] = email + ":B"
            return redirect('/home/', code=302, Response=None)


@app.route('/register/staff/', methods=['POST', 'GET'])
def register_staff():
    if request.method == 'GET':
        airlines = mt.root_sql_query(user='root', stmt=MySQLTool.STMT_GET_ALL_AIRLINES)
        return 'register_staff_get'
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('date_of_birth')
        airline_name = request.form.get('airline_name')

        # check duplicate
        if mt.root_check_duplicates(table='airline_stuff', attribute='username', value=username, user='root'):
            # duplicate
            # TODO
            return 'duplicate user'
        else:
            md5_pass = md5(password.encode('utf-8')).hexdigest()
            mt.root_insert(user='root', table='airline_stuff', value=[username, md5_pass, first_name, last_name, dob,
                                                                      airline_name])
            # TODO
            session['user'] = username + ":A"
            return redirect('/home/', code=302, Response=None)


@app.route('/login/customer/', methods=['POST', 'GET'])
def login_customer():
    if 'user' in session.keys():
        return redirect('/home/', code=302, Response=None)

    if request.method == 'GET':
        return render_template('login_customer.html')
    else:
        email = request.form.get('email')
        md5_pass = md5(request.form.get('password').encode('utf8')).hexdigest()
        if mt.root_check_exists(user='root', table='customer', attribute=['email', 'password'],
                                value=[email, md5_pass]):
            # login success
            session['user'] = email + ':C'
            return 'login success as Customer'
        else:
            # login unsuccessful
            return 'login failed'
            pass


@app.route('/login/agent/', methods=['POST', 'GET'])
def login_agent():
    if 'user' in session.keys():
        return redirect('/home/', code=302, Response=None)

    if request.method == 'GET':
        return render_template('login_agent.html')
    else:
        email = request.form.get('email')
        md5_pass = md5(request.form.get('password').encode('utf8')).hexdigest()
        if mt.root_check_exists(user='root', table='booking_agent', attribute=['email', 'password'],
                                value=[email, md5_pass]):
            # login success
            session['user'] = email + ':B'
            return 'login success as booking agent'
        else:
            # login unsuccessful
            return 'login failed'
            pass


@app.route('/login/staff/', methods=['POST', 'GET'])
def login_staff():
    if 'user' in session.keys():
        return redirect('/home/', code=302, Response=None)

    if request.method == 'GET':
        return render_template('login_staff.html')
    else:
        username = request.form.get('username')
        md5_pass = md5(request.form.get('password').encode('utf8')).hexdigest()
        if mt.root_check_exists(user='root', table='airline_staff', attribute=['username', 'password'],
                                value=[username, md5_pass]):
            # login success
            session['user'] = username + ':A'
            return 'login success as Airline Staff'
        else:
            # login unsuccessful
            return 'login failed'
            pass


@app.route('/logout', methods=['POST', 'GET'])
def log_out():
    session.clear()
    return redirect('/home/', 302, Response=None)


@app.route('/home/', methods=['POST', 'GET'])
def home():
    if 'user' in session.keys():
        return 'Home of ' + session['user']
    else:
        return 'Guest'


@app.errorhandler(404)
def error404(error):
    return 'Are you sure about this url?'


@app.errorhandler(403)
def error403(error):
    return 'You have encountered a 403 error'


@app.errorhandler(500)
def error500(error):
    return 'Ohno server crashed!'


@app.route('/super/', methods=['POST', 'GET'])
def super():
    if request.method == 'GET':
        return render_template('super.html')
    else:
        if request.form.get('password') != 'god':
            return 'Password Wrong'
        stmtq = request.form.get('SQLQ')
        if stmtq != "":
            result = str(mt.root_sql_query(user='root', stmt=stmtq))
            return result
        stmta = request.form.get('SQLA')
        mt.root_sql_query(user='root', stmt=stmta)
        return 'OK'


if __name__ == '__main__':

    if DEBUG:
        app.run(debug=DEBUG, host=HOST, port=PORT)
    else:
        print("LAN IP:", socket.gethostbyname(socket.gethostname()))
        app.run(debug=DEBUG, host='0.0.0.0', port=80)
