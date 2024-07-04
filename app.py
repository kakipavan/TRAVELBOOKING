from flask import Flask, render_template, request, redirect, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/travel_booking_db'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user:
            return 'That username already exists!'

        hashpass = generate_password_hash(request.form['password'])
        users.insert_one({'username': request.form['username'], 'password': hashpass})
        session['username'] = request.form['username']
        return redirect('/dashboard')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and check_password_hash(login_user['password'], request.form['password']):
            session['username'] = request.form['username']
            return redirect('/dashboard')
        else:
            return 'Invalid username/password combination'

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        bookings = mongo.db.bookings.find({'username': session['username']})
        return render_template('dashboard.html', bookings=bookings)
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_booking', methods=['POST'])
def add_booking():
    if 'username' in session:
        bookings = mongo.db.bookings
        airline_info = {
            'airline_name': request.form['airline_name'],
            'flights': [
                {
                    'source': request.form['flight_source'],
                    'destination': request.form['flight_destination']
                }
            ]
        }
        booking_data = {
            'username': session['username'],
            'airline': airline_info,
            'hotel_name': request.form['hotel_name'],
            'check_in_date': request.form['check_in_date'],
            'check_out_date': request.form['check_out_date']
        }
        bookings.insert_one(booking_data)
        return redirect('/dashboard')
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
