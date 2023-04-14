from datetime import datetime
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from flask_mysqldb import MySQL
from flask_restful import Api,Resource
import db
import restapi
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit

import requests
import flask
import socketmessage
import pdf

app = Flask(__name__)
app.secret_key = "b-lease2022"
#=====================================================
api = Api(app)
CORS(app)

#
#----------------------------------------------------

import os
import flask
import mysql.connector
from dateutil.relativedelta import relativedelta
import util


api.add_resource(restapi.user,"/user")
api.add_resource(restapi.delete_user,"/delete_user")
api.add_resource(restapi.changepassword,"/changepassword")
api.add_resource(restapi.session,"/session")
api.add_resource(restapi.complaint,"/complaint")
api.add_resource(restapi.user_payment_method,"/user_payment_method")
api.add_resource(restapi.register,"/register")
api.add_resource(restapi.login,"/login")

api.add_resource(restapi.Leasing,"/leasing")
api.add_resource(restapi.LeasingContracts,"/leasingcontracts")
api.add_resource(restapi.Leasing_Documents,"/leasingdocs")
api.add_resource(restapi.Message,"/messages")
api.add_resource(restapi.property,"/property")
api.add_resource(restapi.properties,"/properties")

api.add_resource(restapi.propertyimages,"/propertyimages/<string:propertyID>/<string:image>")
api.add_resource(restapi.propertydocuments,"/propertydocuments/<string:propertyID>/<string:docName>")
api.add_resource(restapi.leasingdocuments,"/leasingdocuments/<string:leasingID>/<string:contractDocument>")
api.add_resource(restapi.leasingdocs,"/leasingdocs/<string:leasingID>/<string:file>")



#-----------------------------------------------------

#Database Connection Setup 
#-----------------------------------------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3308
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'project2023!'
app.config['MYSQL_PASSWORD'] = 'Kyla2001!!'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_DB'] = 'b_lease'
mysql = MySQL(app)
#-----------------------------------------------------

#=============================================================
# Find the specific string
@app.route('/pdffile')
def edit_word():
    response = pdf.createPDF()

    return response

@app.route('/pdf')
def generate_pdf():
    response = pdf.generate_pdf()

    return response
#============================================================

@app.route('/')
def index():  
    if 'sessionID' in session:
            return redirect(url_for('dashboard'))
    

    title = "B-Lease | Login" 
    
    return render_template('index.html', title=title)   
   
    
@app.route("/login_user", methods=['POST'])
def login_user():
    if 'sessionID' in session:
            return redirect(url_for('dashboard'))

    if request.method == 'POST' and 'admin_username' in request.form and 'admin_password' in request.form: 
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']
        fields = ['admin_username','admin_password']
        data = [admin_username,admin_password]
        
        okey = db.get_specific_data('admin',fields,data)
        if okey is not None:
            session['sessionID'] = okey['adminID']  
            message = "Login Successfully"

        else:
            message = "Wrong credentials"
    

            return render_template('index.html', message=message)   
   
     

    
@app.route("/dashboard")
def dashboard():
    if 'sessionID' not in session:
            return redirect(url_for('index'))
    title = "B-Lease | Dashboard" 

    if 'sessionID' in session:
        return render_template('dashboard.html', okey=session['sessionID'], title=title)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('index'))


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return response

@app.route("/user_report")
def user_report():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | User Report"
    user = db.get_all_data('user')

    for each in user:
        each['images'] = []
        for filename in os.listdir(f'static/users/{each["userID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                # data['images'].append(str(filename))
                    
                each['images'].append(filename)
    return render_template(
        "user_report.html",
        title=title,
        user = user,
    )

@app.route("/view_user")
def view_user():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | User Info"   
    userID = request.args.get('userID')
    
    user = db.get_specific_data('user', ['userID'], [userID])
    error = request.args.get('error')
    success = request.args.get('success')


    user['images'] = []
    for filename in os.listdir(f'static/users/{user["userID"]}/images/'):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            # data['images'].append(str(filename))
                
            user['images'].append(filename)
                    
                
    return render_template(
        "view_user.html",
        title=title,
        user = user,
        success=success,
        error=error,
    )

@app.route("/admin_panel")
def admin_panel():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Admin Panel"   
    admin = db.get_all_data('admin')

    return render_template(
        "admin_panel.html",
        title = title,
        admin = admin,
    )
@app.route("/add_admin")
def add_admin():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Add Admin User"
    
    return render_template("add_admin.html", title=title)

@app.route("/addAdmin",methods=['POST'])
def addAdmin():
    if 'sessionID' not in session:
            return redirect(url_for('dashboard'))

    error = request.args.get('error')
    success = request.args.get('success')
    adminID = request.form['adminID']
    admin_fname = request.form['admin_fname'].upper()
    admin_mname = request.form['admin_mname'].upper()
    admin_lname = request.form['admin_lname'].upper()
    admin_username = request.form['admin_username']
    admin_password = request.form['admin_password']

    existing_member = db.get_data('admin', 'adminID', adminID)
    if existing_member is None:
   
        now = datetime.now()
        date_now = now.strftime("%Y-%m-%d %H:%M:%S")
        print('\n\n')
        print("----------------------------------------")
        print(f"New admin added | {date_now}")
        print("AdminID: " + adminID)
        print("Name:" + admin_fname+ " "+ admin_mname + " " + admin_lname)
        print("Username: " + admin_username)
        print("Password: " + admin_password)
        print("----------------------------------------")
        print("\n\n")

        md5_hash = hashlib.md5(admin_password.encode()).hexdigest()

        fields = ['adminID','admin_fname', 'admin_mname', 'admin_lname', 'admin_username', 'admin_password_hashed','admin_password', 'created_at']
        data = [adminID,admin_fname, admin_mname,admin_lname,admin_username,md5_hash,admin_password,date_now]

        db.insert_data('admin', fields, data)
        
        message = f"Successfully added { admin_lname }, {admin_fname} {admin_mname} as admin"
        return redirect(url_for('add_admin', message=message))

    elif adminID and admin_fname and admin_mname and admin_lname and admin_username and admin_password and  existing_member:
        message = f"Member { admin_lname}, {admin_fname} {admin_mname} is already a member"
        return redirect(url_for('add_admin',message=message,))

@app.route("/deleteaccount", methods=['GET'])
def deleteaccount():
    
    adminID = request.args.get('adminID')
    
    admin = db.get_specific_data('admin', ['adminID'], [adminID])
    
    if admin:
        okey = db.delete_data('admin', 'adminID', adminID)
        if okey:
            print ('Admin Successfully Deleted')
            return redirect(url_for('admin_panel'))
        else:
            print('Admin was not deleted')
            return redirect(url_for('admin_panel'))
    else:
        print('Account not found')
        return redirect(url_for('admin_panel'))

@app.route("/deleteuseraccount", methods=['GET'])
def deleteuseraccount():
    
    userID = request.args.get('userID')
    
    user = db.get_specific_data('user', ['userID'], [userID])
    
    if user:
        okey = db.delete_data('user', 'userID', userID)
        if okey:
            print ('User Successfully Deleted')
            return redirect(url_for('user_report'))
        else:
            print('User was not deleted')
            return redirect(url_for('user_report'))
    else:
        print('Account not found')
        return redirect(url_for('user_report'))


@app.route("/viewuseraccount", methods=['GET'])
def viewuseraccount():
    
    userID = request.args.get('userID')
    
    user = db.get_specific_data('user', ['userID'], [userID])
    
    if user:
        print ('User Successfully Found')
        return redirect(url_for('user_report'))
    else:
        print('Account not found')
        return redirect(url_for('user_report'))
    
@app.route("/viewadminaccount", methods=['GET'])
def viewadminaccount():
    
    adminID = request.args.get('userID')
    
    admin = db.get_specific_data('admin', ['adminID'], [adminID])
    
    if admin:
        print ('Admin Successfully Found')
        return redirect(url_for('admin_panel'))
    else:
        print('Account not found')
        return redirect(url_for('admin_panel'))
    
@app.route("/updateadmin", methods=['POST'])
def updateadmin():

    adminID = request.form['adminID']
    admin_fname = request.form['admin_fname']
    admin_mname = request.form['admin_mname']
    admin_lname = request.form['admin_lname']
    admin_username = request.form['admin_username']
    admin_password = request.form['admin_password']

    print(adminID)
    print(admin_fname)
    print(admin_mname)
    print(admin_lname)
    print(admin_username)
    print(admin_password)
    
    if adminID and admin_fname and admin_mname and admin_lname and admin_username and admin_password:
        db.update_data('admin', ['adminID', 'admin_fname', 'admin_mname', 'admin_lname', 'admin_username', 'admin_password'], [adminID,admin_fname.upper(),admin_mname.upper(),admin_lname.upper(),admin_username,admin_password])
        message = "Profile Info updated successfully"
        return redirect(url_for('admin_panel', success=message))
    else:
        message = "Error updating profile info"
        return redirect(url_for('admin_panel', error=message))

@app.route("/property_listings")
def property_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Verify Property Listings"  
    property = db.get_all_data('property')
    user = db.get_all_data('user')
    property_images = db.get_all_data('property_images')
    
    for each in property:
        each['images'] = []
        for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                # data['images'].append(str(filename))
                    
                each['images'].append(filename)

    
    # im = Image.open(property_images)
    return render_template("property_listings.html", title=title, property=property, user=user,property_images=property_images)

@app.route("/approved_listings")
def approved_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Verify Property Listings"  
    property = db.get_all_data('property')
    user = db.get_all_data('user')
    for each in property:
        each['images'] = []
        for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                # data['images'].append(str(filename))
                    
                each['images'].append(filename)
   
    return render_template("approved_listings.html", title=title, property=property, user=user)

@app.route("/pending_listings")
def pending_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Verify Property Listings"  
    property = db.get_all_data('property')
    user = db.get_all_data('user')
    for each in property:
        each['images'] = []
        for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                # data['images'].append(str(filename))
                    
                each['images'].append(filename)
  
    return render_template("pending_listings.html", title=title, property=property, user=user)

@app.route("/declined_listings")
def declined_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Verify Property Listings"  
    property = db.get_all_data('property')
    user = db.get_all_data('user')
    for each in property:
        each['images'] = []
        for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                # data['images'].append(str(filename))
                    
                each['images'].append(filename)

    return render_template("declined_listings.html", title=title, property=property, user=user)



@app.route("/view_property", methods=['GET'])
def view_property():
    
     if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
     propertyID = request.args.get('propertyID')
     userID = request.args.get('userID')
     user = db.get_all_data('user')
     title = "B-Lease | View Property Listings"  
     property = db.get_specific_data('property',['propertyID'],[propertyID])

     property['images'] = []
     
     for filename in os.listdir(f'static/property_listings/{property["propertyID"]}/images/'):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            # data['images'].append(str(filename))
                
            property['images'].append(filename)
     property['documents'] = []
     for filename in os.listdir(f'static/property_listings/{property["propertyID"]}/documents/'):
        if filename.endswith('.pdf') or filename.endswith('.doc') or filename.endswith('.docx'):
            # data['images'].append(str(filename))

            property['documents'].append(filename)

     return render_template("view_property.html", title=title, property=property,user=user)

    
@app.route("/approveStatus")
def approveStatus():

    propertyID = request.args.get('propertyID')
    property_status = "open"

    db.update_data('property', ['propertyID', 'property_status'],[propertyID, property_status])
    message = "You have successfully approve the listing."
    return redirect(url_for('property_listings', success = message))

@app.route("/declineStatus")
def declineStatus():

    propertyID = request.args.get('propertyID')
    property_status = "declined"

    db.update_data('property', ['propertyID', 'property_status'],[propertyID, property_status])
    message = "Failed to approve the listing."
    return redirect(url_for('property_listings', success = message))

@app.route("/contracts")
def contracts():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | List of Contracts"  

    leasing = db.get_all_data('leasing')
    
    user = db.get_all_data('user')

    # im = Image.open(property_images)
    return render_template("contracts.html", title=title, property=property, user=user,leasing=leasing)

@app.route("/view_contract", methods=['GET'])
def view_contract():
    
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    leasingID = request.args.get('leasingID')
    user = db.get_all_data('user')
    title = "B-Lease | View Contracts" 
    leasing = db.get_all_data('leasing')
    payment = db.get_all_data('payment')

    leasing = db.get_specific_data('leasing',['leasingID'],[leasingID])
     

    leasing['documents'] = []
    for filename in os.listdir(f'static/leasing/{leasing["leasingID"]}/documents/'):
        if filename.endswith('.pdf') or filename.endswith('.doc') or filename.endswith('.docx'):
            # data['images'].append(str(filename))

            leasing['documents'].append(filename)

    return render_template("view_contract.html", title=title, leasing=leasing, user=user,payment=payment)


@app.route("/approveContract")
def approveContract():

    leasingID = request.args.get('leasingID')
    leasing_status = "ongoing"
    leasing = db.get_all_data('leasing')
    
    # day = datetime.strptime('leasing_start', '%Y-%m-%d').strftime('%d')

    # print(str(day))
    # define your leasing start and end dates
    leasingID = request.args.get('leasingID')
    leasing_payment_frequency = request.args.get('leasing_payment_frequency')
    pay_lessorID = request.args.get('lessorID')
    pay_lesseeID = request.args.get('lesseeID')
    pay_fee = request.args.get('leasing_total_fee')

    # define your leasing start and end dates
    leasing_start_str = request.args.get('leasing_start')
    leasing_end_str = request.args.get('leasing_end')
    leasing_start = datetime.strptime(leasing_start_str, '%Y-%m-%d').date()
    leasing_end = datetime.strptime(leasing_end_str, '%Y-%m-%d').date()

    val = None
    

    fields = ['paymentID', 'leasingID','pay_status','pay_lessorID','pay_lesseeID','pay_date','pay_fee']
    # loop over the range of dates and insert records
    current_date = leasing_start
    while current_date <= leasing_end:
        # check if the current date occurs within the leasing period
        if current_date < leasing_start or current_date >= leasing_end:
            current_date += relativedelta(months=1)
            continue
        
        paymentID = util.generateUUID(str(leasingID+ str(datetime.now())))
        val = (current_date).strftime("%Y-%m-%d")
        data = [paymentID, leasingID, 'pending', pay_lessorID, pay_lesseeID, val, pay_fee]
        db.insert_data('payment',fields,data)
        
        # increment the current date by one month
        current_date += relativedelta(months=1)
    db.update_data('leasing', ['leasingID', 'leasing_status'],[leasingID, leasing_status])
    message = "You have successfully approve the contract."
    return redirect(url_for('contracts', success = message))

@app.route("/declineContract")
def declineContract():

    leasingID = request.args.get('leasingID')
    leasing_status = "for review"

    db.update_data('leasing', ['leasingID', 'leasing_status'],[leasingID, leasing_status])
    message = "Failed to approve the contract."
    return redirect(url_for('contracts', success = message))


@app.route("/ongoing_contracts")
def ongoing_contracts():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | List of Contracts"  
    leasing = db.get_all_data('leasing')
   
    user = db.get_all_data('user')

    # im = Image.open(property_images)
    return render_template("ongoing_contracts.html", title=title, property=property, user=user,leasing=leasing)

@app.route("/finished_contracts")
def finished_contracts():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | List of Contracts"  
    leasing = db.get_all_data('leasing')
   
    user = db.get_all_data('user')

    # im = Image.open(property_images)
    return render_template("finished_contracts.html", title=title, property=property, user=user,leasing=leasing)

@app.route("/payment_reports")
def payment_reports():
    if 'sessionID' not in session:
            return redirect(url_for('index'))
    title = "B-Lease | Payment Reports"   

    payment = db.get_all_data('payment')
    user = db.get_all_data('user')

    return render_template("payment_reports.html", title=title, payment=payment,user=user)

@app.route("/deletepaymentaccount", methods=['GET'])
def deletepaymentaccount():
    
    paymentID = request.args.get('paymentID')
    
    payment = db.get_specific_data('payment', ['paymentID'], [paymentID])
    
    if payment:
        okey = db.delete_data('payment', 'paymentID', paymentID)
        if okey:
            print ('Payment Successfully Deleted')
            return redirect(url_for('payment_reports'))
        else:
            print('Payment was not deleted')
            return redirect(url_for('payment_reports'))
    else:
        print('Payment not found')
        return redirect(url_for('payment_reports'))



# if __name__ == "__main__":
# #     # server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
# #     # server.serve_forever()
#     from geventwebsocket.handler import WebSocketHandler
#     from gevent.pywsgi import WSGIServer
    
#     http_server = WSGIServer(('0.0.0.0', 5000,), app, handler_class=WebSocketHandler)
#     http_server.serve_forever()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")







