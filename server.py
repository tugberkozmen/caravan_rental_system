from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime
import mysql.connector

app = Flask(__name__)

app.secret_key = '8b1d300039c4dfa8f3dbd87d'

db = mysql.connector.connect(host="eu-cdbr-west-03.cleardb.net", user="bec64b4c2937df", password="584be305", database="heroku_dcb8a7c7bafdb7a")

app.config.from_object("settings")

@app.route("/")
def before_home_page():
    return render_template("before_home.html")

@app.route("/home", methods = ['GET', 'POST'])
def home_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    cur = db.cursor()
    cur.execute("SELECT * FROM location")
    location = cur.fetchall()
    db.commit()
    if request.method == 'GET':
        return render_template("home.html", location=location)
    else:
        category_num = request.form['category']
        pickup = request.form['pickup']
        return_date = request.form['return']
        location = request.form['location']
        d1 = datetime.strptime(pickup, "%Y-%m-%d")
        d2 = datetime.strptime(return_date, "%Y-%m-%d")
        delta = d2 - d1

        session['category'] = category_num
        session['pickup'] = pickup
        session['return_date'] = return_date
        session['location'] = location
        session['days'] = delta.days
        return redirect(url_for('search_caravan_page'))        

@app.route("/caravans")
def caravans_page():
    return render_template("caravans.html")

@app.route("/register", methods = ['GET', 'POST'])
def register_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        surname = request.form['surname']
        licenceID = request.form['drivinglicence']
        email = request.form['email']
        phonenum = request.form['phone']
        password = request.form['password']

        cur = db.cursor()
        cur.execute("INSERT INTO customer (firstName, lastName, drivingLicenceNumber, email, phoneNumber, customerPassword) VALUES (%s, %s, %s, %s, %s, %s)", (name, surname, licenceID, email, phonenum, password))
        db.commit()
        cur.close()
        message1 = 'Registered succesfully!'
        return render_template("register.html", message=message1)

@app.route("/login", methods = ['GET', 'POST'])
def login_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    cur = db.cursor(dictionary=True)
    message2 = ""

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur.execute("SELECT * FROM customer WHERE email = %s AND customerPassword = %s", (email, password))
        customer_account = cur.fetchone()

        if customer_account:
            session['id'] = customer_account['customerID']
            session['name'] = customer_account['firstName']
            return redirect(url_for('home_page'))
        else:
            message2 = "Incorrect email or password"
    return render_template("login.html", msg=message2)

@app.route("/profile", methods = ['GET', 'POST'])
def profile_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM customer WHERE firstName = %s", [session['name']])
    customer_profile = cur.fetchone()
    session['customer_name'] = customer_profile['firstName']
    session['customer_lastname'] = customer_profile['lastName']
    session['licenceID'] = customer_profile['drivingLicenceNumber']
    session['email'] = customer_profile['email']
    session['phone'] = customer_profile['phoneNumber']
    cur.close()

    cur = db.cursor()
    cur.execute("SELECT customer.firstName, customer.lastName FROM reservation INNER JOIN customer ON reservation.customerID = customer.customerID")
    customer_info = cur.fetchall()
    db.commit()
    cur.execute("SELECT caravan.brand, caravan.model, caravan.modelyear, location.locationname, location.city, location.state, reservation.pickup_date, reservation.return_date, reservation.insurance, reservation.cost, reservation.reservationID FROM reservation INNER JOIN caravan ON reservation.selectedcaravan = caravan.caravanID INNER JOIN location ON reservation.locationID = location.locationID")
    reservation_info = cur.fetchall()
    db.commit()
    if request.method == 'POST':
        reservation = request.form['reservation']
        cur.execute("SELECT selectedcaravan FROM reservation WHERE reservationID = %s", (reservation,))
        caravan = cur.fetchone()
        db.commit()
        cur.execute("UPDATE caravan SET pickupDate = %s, returnDate = %s WHERE caravanID = %s", ('0000-00-00', '0000-00-00', caravan[0]))
        db.commit()
        cur.execute("DELETE FROM reservation WHERE reservationID = %s", (reservation,))
        db.commit()
        return redirect(url_for('profile_page'))
    cur.close()
    return render_template("profile.html", details=reservation_info)

@app.route("/register-company", methods = ['GET', 'POST'])
def register_company_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    if request.method == 'GET':
        return render_template("register_company.html")
    else:
        company_name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        cur = db.cursor()
        cur.execute("INSERT INTO company (name, phone, password) VALUES (%s, %s, %s)", (company_name, phone, password))
        db.commit()
        cur.close()
        message1 = 'Registered succesfully!'
        return render_template("register_company.html", message=message1)

@app.route("/login-company", methods = ['GET', 'POST'])
def login_company_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    cur = db.cursor(dictionary=True)
    message2 = ""

    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        company_name = request.form['name']
        password = request.form['password']
        cur.execute("SELECT * FROM company WHERE name = %s AND password = %s", (company_name, password))
        company_account = cur.fetchone()
        if company_account:
            session['company_id'] = company_account['companyID']
            session['cname'] = company_account['name']
            return redirect(url_for('company_home_page'))
        else:
            message2 = "Incorrect name or password"
    return render_template("login_company.html", msg=message2)

@app.route("/logout")
def logout():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    session.clear()
    return redirect(url_for('home_page'))

@app.route("/search-caravan", methods = ['GET', 'POST'])
def search_caravan_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    category_num = session.get('category')
    pickup = session.get('pickup')
    rdate = session.get('return_date')
    cur = db.cursor()
    cur.execute("SELECT * FROM caravan WHERE category = %s AND (pickupDate = '0000-00-00' OR returnDate < %s OR %s < pickupDate)", (category_num, pickup, rdate))
    caravan = cur.fetchall()
    db.commit()
    cur.close()
    if request.method == 'GET':
        return render_template("search_caravan.html", data=caravan)
    else:
        customer = session.get('id')
        location = session.get('location')
        caravan = request.form['caravan']
        how_many_days = session.get('days')
        pickup_date = session.get('pickup')
        return_date = session.get('return_date')
        cur = db.cursor()
        cur.execute("SELECT * FROM location WHERE locationname = %s", (location,))
        locationid = cur.fetchone()
        db.commit()
        cur.execute("SELECT caravan.costperday FROM caravan WHERE caravanID = %s", (caravan,))
        caravan_cost = cur.fetchone()
        db.commit()
        total_cost = caravan_cost[0] * how_many_days
        insurance = request.form['answer']
        if insurance == 'Yes':
            total_cost += 20 * how_many_days
        cur.execute("SELECT supplier FROM caravan WHERE caravanID = %s", (caravan,))
        company = cur.fetchone()
        db.commit()
        cur.execute("INSERT INTO reservation (customerID, locationID, selectedcaravan, company, pickup_date, return_date, insurance, cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (customer, locationid[0], caravan, company[0], pickup_date, return_date, insurance, total_cost))
        db.commit()
        cur.execute("UPDATE caravan SET pickupDate = %s, returnDate = %s WHERE caravanID = %s", (pickup_date, return_date, caravan))
        db.commit()
        return redirect(url_for('profile_page'))        

@app.route("/company-home", methods = ['GET', 'POST'])
def company_home_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    message = ""
    if request.method == 'GET':
        return render_template("company_home.html")
    else:
        categoryid = request.form['category']
        company = session.get('company_id')
        brand = request.form['brand']
        model = request.form['model']
        modelyear = request.form['modelyear']
        transmission = request.form['transmission']
        size = request.form['size']
        cost = request.form['cost']
        cur = db.cursor()
        cur.execute("INSERT INTO caravan (category, supplier, brand, model, modelyear, transmission, caravansize, costperday) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (categoryid, company, brand, model, modelyear, transmission, size, cost))
        db.commit()
        message = "Caravan added successfully!"
        return render_template("company_home.html", mesaj=message)

@app.route("/company-profile", methods = ['GET', 'POST'])
def company_profile_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM company WHERE name = %s", [session['cname']])
    company = cur.fetchone()
    session['company_name'] = company['name']
    session['company_phone'] = company['phone']
    cur.close()
    cur = db.cursor()
    cur.execute("SELECT customer.firstName, customer.lastName, customer.drivingLicenceNumber, customer.email, customer.phoneNumber, caravan.brand, caravan.model, reservation.pickup_date, reservation.return_date, reservation.insurance, reservation.cost, reservation.reservationID FROM reservation INNER JOIN customer ON reservation.customerID = customer.customerID INNER JOIN caravan ON reservation.selectedcaravan = caravan.caravanID")
    reservations = cur.fetchall()
    db.commit()
    if request.method == 'POST':
        reservation = request.form['reservation']
        cur.execute("SELECT selectedcaravan FROM reservation WHERE reservationID = %s", (reservation,))
        caravan = cur.fetchone()
        db.commit()
        cur.execute("UPDATE caravan SET pickupDate = %s, returnDate = %s WHERE caravanID = %s", ('0000-00-00', '0000-00-00', caravan[0]))
        db.commit()
        cur.execute("DELETE FROM reservation WHERE reservationID = %s", (reservation,))
        db.commit()
        return redirect(url_for('company_profile_page'))
    return render_template("company_profile.html", reservation=reservations)

@app.route("/delete-caravan", methods=['GET', 'POST'])
def delete_caravan_page():
    if not db.is_connected():
        while not db.is_connected():
            db.ping(reconnect=True, attempts=1, delay=0)
    company_id = session.get('company_id')
    cur = db.cursor()
    cur.execute("SELECT * FROM caravan WHERE supplier = %s", (company_id,))
    caravans = cur.fetchall()
    db.commit()
    message3 = ""
    if request.method == 'POST':
        deleted_caravan = request.form['caravan']
        cur.execute("SELECT * FROM reservation WHERE selectedcaravan = %s", (deleted_caravan,))
        any_caravan = cur.fetchone()
        db.commit()
        if any_caravan:
            message3 = "Caravan cannot be deleted. First cancel reservations for selected caravan"
        else:
            cur.execute("DELETE FROM caravan WHERE caravanID = %s", (deleted_caravan,))
            db.commit()
            message3 = "Caravan deleted succesfully"
            return redirect(url_for('delete_caravan_page'))
    return render_template("delete_caravan.html", caravans=caravans, msg=message3)

if __name__ == "__main__":
    app.run()