from flask import Flask, render_template, request
from datetime import datetime
from flask_mysqldb import MySQL

def before_home_page():
    return render_template("before_home.html")


def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)

def caravans_page():
    return render_template("caravans.html")

def register_page():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        surname = request.form['surname']
        licenceID = request.form['drivinglicence']
        email = request.form['email']
        phonenum = request.form['phone']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO customer (firstName, lastName, drivingLicenceNumber, email, phoneNumber, customerPassword) VALUES (%s %s %s %s %s %s)", (name, surname, licenceID, email, phonenum, password))
        mysql.connection.commit()
        cur.close()
        msg = 'Registered succesfully!'
        return render_template("register.html", msg=msg)

def login_page():
    return render_template("login.html")