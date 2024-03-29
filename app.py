
import hashlib
from config import app, mysql, api
from flask_socketio import SocketIO, send, emit
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
import os
from dateutil.relativedelta import relativedelta
from restapi import Leasing_Documents
import util
import db
import contract

import api_endpoints

from notifications import generate_notifications






#--------------------------------------------------------------------------------
#Routings of the web server are configured and found here
#--------------------------------------------------------------------------------



# Find the specific string
@app.route('/pdffile')
def edit_word():
    response = contract.setContract()

    return response

@app.route('/pdf')
def generate_pdf():
    response = contract.generate_pdf()

    return response
#============================================================

@app.route('/')
def index():  
    if 'sessionID' in session:
            return redirect(url_for('dashboard'))
    

    title = "B-Lease | Login" 
    
    return render_template('index.html', title=title)   
   
@app.route('/lawyer')
def lawyerindex():  
    if 'sessionID' in session:
            return redirect(url_for('dashboard'))
    

    title = "B-Lease | Lawyer Login" 
    
    return render_template('lawyerindex.html', title=title)   
   
    
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
            session['admin_firstname'] = okey['admin_fname']
            session['admin_mname'] = okey['admin_mname']
            session['admin_lastname'] = okey['admin_lname']
            session['user_type'] = 'admin'
            message = "Login Successfully"
            return redirect(url_for('dashboard'))
        else:
            message = "Wrong credentials"  
            return render_template('index.html', message=message)
         
   
@app.route("/login_lawyer", methods=['POST'])
def login_lawyer():
    if 'sessionID' in session:
            return redirect(url_for('lawyerdashboard'))

    if request.method == 'POST' and 'lawyer_username' in request.form and 'lawyer_password' in request.form: 
        lawyer_username = request.form['lawyer_username']
        lawyer_password = request.form['lawyer_password']
        fields = ['lawyer_username','lawyer_password']
        data = [lawyer_username,lawyer_password]
        
        okey = db.get_specific_data('lawyer',fields,data)
        if okey is not None:
            session['sessionID'] = okey['lawyerID']  
            session['lawyer_firstname'] = okey['lawyer_fname']
            session['lawyer_mname'] = okey['lawyer_mname']
            session['lawyer_lastname'] = okey['lawyer_lname']
            session['user_type'] = 'lawyer'
            message = "Login Successfully"
            return redirect(url_for('lawyerdashboard'))
        else:
            message = "Invalid credentials"  
            return render_template('lawyerindex.html', message=message)
         
   
     

    
@app.route("/dashboard")
def dashboard():
    if 'sessionID' not in session:
            return redirect(url_for('index'))
    title = "B-Lease | Dashboard" 
    total_finished_contracts = db.countTotalFinishedContracts()
    total_ongoing_contracts = db.countTotalOngoingContracts()
    total_open_properties = db.countTotalOpenProperties()
    total_filed_complaints = db.countTotalFiledComplaints()
    total_resolved_complaints = db.countTotalResolvedComplaints()
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        return render_template('dashboard.html', okey=session['sessionID'], 
                               title=title, firstname=firstname,middlename=middlename,
                               lastname=lastname, total_finished_contracts =total_finished_contracts,
                                total_ongoing_contracts = total_ongoing_contracts,
                                 total_open_properties=total_open_properties,
                                  total_filed_complaints=total_filed_complaints,
                                   total_resolved_complaints=total_resolved_complaints )
    return redirect(url_for('index'))
@app.route("/lawyerdashboard")
def lawyerdashboard():
    if 'sessionID' not in session:
            return redirect(url_for('lawyerindex'))
    title = "B-Lease | Lawyer Dashboard" 

    total_approved_contracts = db.countTotalOngoingContracts()
    total_finished_contracts = db.countTotalFinishedContracts()
    total_declined_contracts = db.countTotalDeclinedContracts()

    if 'sessionID' in session:
        firstname = session['lawyer_firstname']
        middlename = session['lawyer_mname']
        lastname = session['lawyer_lastname']
        return render_template('lawyerdashboard.html', okey=session['sessionID'], 
                               title=title, firstname=firstname,middlename=middlename,
                               lastname=lastname, total_approved_contracts = total_approved_contracts,
                               total_finished_contracts = total_finished_contracts, total_declined_contracts = total_declined_contracts
                               
                               )
    return redirect(url_for('lawyerindex'))

@app.route('/logout')
def logout():
   user_type = session['user_type']
   session.clear()

   if user_type == 'admin':
        return redirect(url_for('index'))
       
   if user_type == 'lawyer':
        return redirect(url_for('lawyerindex'))
    

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
    logging = db.getLoggingReport()

    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']

    # session = db.get_all_data('session')
    # logoutTime = request.args.get('logoutTime')
    # logout = db.get_specific_data('session','logoutTime',logoutTime)

        # for each in logging:
        #     each['images'] = []
        #     for filename in os.listdir(f'static/users/{each["userID"]}/images/'):
        #         if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
        #             # data['images'].append(str(filename))
        #             each['images'].append(filename)

        return render_template("user_report.html",title=title,logging_data=logging,firstname=firstname,middlename=middlename,lastname=lastname)

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
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Admin Panel"   
        admin = db.get_all_data('admin')

        return render_template(
            "admin_panel.html",
            title = title,
            admin = admin,
            firstname=firstname,
            middlename=middlename,
            lastname=lastname
        )
    
@app.route("/lawyer_panel")
def lawyer_panel():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Admin Panel"   
        lawyers = db.get_all_data('lawyer')

        return render_template(
            "lawyer_panel.html",
            title = title,
            lawyers = lawyers,
            firstname=firstname,
            middlename=middlename,
            lastname=lastname
        )
@app.route("/add_admin")
def add_admin():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Add Admin User"
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']

    return render_template("add_admin.html", title=title,firstname=firstname,middlename=middlename,lastname=lastname)
@app.route("/add_lawyer")
def add_lawyer():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    title = "B-Lease | Add Lawyer User"
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']

    return render_template("add_lawyer.html", title=title,firstname=firstname,middlename=middlename,lastname=lastname)

@app.route("/addAdmin",methods=['POST'])
def addAdmin():
    if 'sessionID' not in session:
            return redirect(url_for('dashboard'))

    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']

        error = request.args.get('error')
        success = request.args.get('success')
        admin_fname = request.form['admin_fname'].upper()
        admin_mname = request.form['admin_mname'].upper()
        admin_lname = request.form['admin_lname'].upper()
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        adminID = util.generateUUID(f"{admin_fname},{admin_mname},{admin_lname},{admin_username},{admin_password}")

        existing_member = db.get_data('admin', 'adminID', adminID)
        if existing_member is None:

            md5_hash = hashlib.md5(admin_password.encode()).hexdigest()

            fields = ['adminID','admin_fname', 'admin_mname', 'admin_lname', 'admin_username', 'admin_password_hashed','admin_password']
            data = [adminID,admin_fname, admin_mname,admin_lname,admin_username,md5_hash,admin_password]

            db.insert_data('admin', fields, data)
            
            message = f"Successfully added { admin_lname }, {admin_fname} {admin_mname} as admin"
            message1 = 'ok'
            return redirect(url_for('admin_panel', message=message,firstname=firstname,middlename=middlename,lastname=lastname))

        elif adminID and admin_fname and admin_mname and admin_lname and admin_username and admin_password and  existing_member:
            message = f"Member { admin_lname}, {admin_fname} {admin_mname} is already a member"
            message1 = 'not ok'
            return redirect(url_for('add_admin',message=message,message1=message1,firstname=firstname,middlename=middlename,lastname=lastname))

@app.route("/addLawyer",methods=['POST'])
def addLawyer():
    if 'sessionID' not in session:
            return redirect(url_for('dashboard'))

    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        
        error = request.args.get('error')
        success = request.args.get('success')
        lawyer_fname = request.form['lawyer_fname'].upper()
        lawyer_mname = request.form['lawyer_mname'].upper()
        lawyer_lname = request.form['lawyer_lname'].upper()
        lawyer_username = request.form['lawyer_username']
        lawyer_password = request.form['lawyer_password']

        lawyerID = util.generateUUID(f"{lawyer_fname},{lawyer_mname},{lawyer_lname},{lawyer_username},{lawyer_password}")

        existing_member = db.get_data('lawyer', 'lawyerID', lawyerID)
        if existing_member is None:

            md5_hash = hashlib.md5(lawyer_password.encode()).hexdigest()

            fields = ['lawyerID','lawyer_fname', 'lawyer_mname', 'lawyer_lname', 'lawyer_username', 'lawyer_password_hashed','lawyer_password']
            data = [lawyerID,lawyer_fname, lawyer_mname,lawyer_lname,lawyer_username,md5_hash,lawyer_password]

            db.insert_data('lawyer', fields, data)
            
            message = f"Successfully added { lawyer_lname }, {lawyer_fname} {lawyer_mname} as lawyer"
            message1 = 'ok'
            return redirect(url_for('lawyer_panel', message=message,firstname=firstname,middlename=middlename,lastname=lastname))

        elif lawyerID and lawyer_fname and lawyer_mname and lawyer_lname and lawyer_username and lawyer_password and  existing_member:
            message = f"Member { lawyer_lname}, {lawyer_fname} {lawyer_mname} is already a member"
            message1 = 'not ok'
            return redirect(url_for('add_lawyer',message=message,message1=message1,firstname=firstname,middlename=middlename,lastname=lastname))

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
    
@app.route("/deletelawyeraccount", methods=['GET'])
def deletelawyeraccount():
    
    lawyerID = request.args.get('lawyerID')
    
    lawyer = db.get_specific_data('lawyer', ['lawyerID'], [lawyerID])
    
    if lawyer:
        okey = db.delete_data('lawyer', 'lawyerID', lawyerID)
        if okey:
            print ('Lawyer Successfully Deleted')
            return redirect(url_for('lawyer_panel'))
        else:
            print('Lawyer was not deleted')
            return redirect(url_for('lawyer_panel'))
    else:
        print('Account not found')
        return redirect(url_for('lawyer_panel'))
    

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
    
@app.route("/updatelawyer", methods=['POST'])
def updatelawyer():
    
    lawyerID = request.form['lawyerID']
    lawyer_fname = request.form['lawyer_fname']
    lawyer_mname = request.form['lawyer_mname']
    lawyer_lname = request.form['lawyer_lname']
    lawyer_username = request.form['lawyer_username']
    lawyer_password = request.form['lawyer_password']

    print(lawyerID)
    print(lawyer_fname)
    print(lawyer_mname)
    print(lawyer_lname)
    print(lawyer_username)
    print(lawyer_password)
    
    if lawyerID and lawyer_fname and lawyer_mname and lawyer_lname and lawyer_username and lawyer_password:
        db.update_data('lawyer', ['lawyerID', 'lawyer_fname', 'lawyer_mname', 'lawyer_lname', 'lawyer_username', 'lawyer_password'], [lawyerID,lawyer_fname.upper(),lawyer_mname.upper(),lawyer_lname.upper(),lawyer_username,lawyer_password])
        message = "Profile Info updated successfully"
        return redirect(url_for('lawyer_panel', success=message))
    else:
        message = "Error updating profile info"
        return redirect(url_for('lawyer_panel', error=message))

@app.route("/property_listings")
def property_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']

        title = "B-Lease | Verify Property Listings"  
        property = db.get_all_data('property')
        user = db.get_all_data('user')
        property_images = db.get_all_data('property_images')
        
        for each in property:
            each['images'] = []
            for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                        
                    each['images'].append(filename)

        return render_template("property_listings.html", title=title, property=property, user=user,property_images=property_images,firstname=firstname,middlename=middlename,lastname=lastname)

@app.route("/approved_listings")
def approved_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Approved Property Listings"  
        property = db.get_all_data('property')
        user = db.get_all_data('user')
        for each in property:
            each['images'] = []
            for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                        
                    each['images'].append(filename)
    
        return render_template("approved_listings.html", title=title, property=property, user=user,firstname=firstname,middlename=middlename,lastname=lastname)

@app.route("/pending_listings")
def pending_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Pending Property Listings"  
        property = db.get_all_data('property')
        user = db.get_all_data('user')
        for each in property:
            each['images'] = []
            for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):

                    each['images'].append(filename)
    
        return render_template("pending_listings.html", title=title, property=property, user=user,firstname=firstname,middlename=middlename,lastname=lastname)

@app.route("/declined_listings")
def declined_listings():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Declined Property Listings"  
        property = db.get_all_data('property')
        user = db.get_all_data('user')
        for each in property:
            each['images'] = []
            for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            
                    each['images'].append(filename)

        return render_template("declined_listings.html", title=title, property=property, user=user,firstname=firstname,middlename=middlename,lastname=lastname)



@app.route("/view_property", methods=['GET'])
def view_property():
    
     if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
     
     if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        propertyID = request.args.get('propertyID')
        userID = request.args.get('userID')
        user = db.get_all_data('user')
        title = "B-Lease | View Property Listings"  
        property = db.get_specific_data('property',['propertyID'],[propertyID])

        property['images'] = []
        
        for filename in os.listdir(f'static/property_listings/{property["propertyID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
          
                property['images'].append(filename)

        property['documents'] = []
        for filename in os.listdir(f'static/property_listings/{property["propertyID"]}/documents/'):
            if filename.endswith('.pdf') or filename.endswith('.doc') or filename.endswith('.docx'):

                property['documents'].append(filename)

        return render_template("view_property.html", title=title, property=property,user=user,firstname=firstname,middlename=middlename,lastname=lastname)

    
@app.route("/approveStatus", methods=['GET'])
def approveStatus():

    propertyID = request.args.get('propertyID')
    property_status = "open"
    userID = None
    propertyAddress = None
    message = None
    now = None
    read = None
    notificationID = None
    
    
    notification_desc = ''
    
    propertyInfo = db.get_data('property','propertyID',propertyID)
    if propertyInfo:
        userID = propertyInfo['userID']
        propertyAddress = propertyInfo['address']
        notification_desc = f'Your property at {propertyAddress} has been approved.'
        now = str(datetime.now())
        notification_categ = 'Property Listing Approval'

        read = "unread"

        image = util.getPropertyImageThumbnail(propertyInfo['propertyID'])
        
        data = {
            "propertyID":propertyInfo['propertyID'],
            "image":f"{image}",
        }
        status = 'approved'
        data = f"{propertyInfo['propertyID']},{image},{status}"
        if userID and propertyAddress and notification_desc and now and read:
            notificationID = util.generateUUID(f"{userID},{propertyAddress},{notification_categ},{notification_desc},{now},{read}")
        
    if notificationID:
        make_notif = db.insert_data('notifications',
                       ['notificationID','userID','notification_categ','notification_desc','notification_date','read','data'],
                       [notificationID,userID,notification_categ, notification_desc,now,read,data])
  

    db.update_data('property', ['propertyID', 'property_status'],[propertyID, property_status])
    message = "You have successfully approve the listing."

    return redirect(url_for('property_listings', success = message))



@app.route("/declinePropertyListing", methods=['GET'])
def declinePropertyListing():
    
     if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
     
     propertyID = request.args.get('propertyID')

   
     title = "B-Lease | Decline Property Listings"  
   
     return render_template("declineproperty.html", title=title, propertyID=propertyID)

@app.route("/declineStatus", methods=['POST'])
def declineStatus():

    propertyID = request.form['propertyID']
    remarks = request.form['remarks']
    property_status = "declined"
    userID = None
    propertyAddress = None
    message = None
    now = None
    read = None
    notificationID = None
    
    
    notification_desc = ''
    propertyInfo = db.get_data('property','propertyID',propertyID)
    if propertyInfo:
        userID = propertyInfo['userID']
        propertyAddress = propertyInfo['address']
        notification_desc = f'Your property at {propertyAddress} has been declined.'
        now = str(datetime.now())
        notification_categ = 'Property Listing Approval'

        read = "unread"
        image = []
     
        for filename in os.listdir(f'static/property_listings/{propertyInfo["propertyID"]}/images/'):
            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                image.append(filename)

        image = image[0]
        
        data = {
            "propertyID":propertyInfo['propertyID'],
            "image":f"{image}",
        }

        status = "rejected"

        data = f"{propertyInfo['propertyID']},{image},{status}"
        if userID and propertyAddress and notification_desc and now and read:
            notificationID = util.generateUUID(f"{userID},{propertyAddress},{notification_categ},{notification_desc},{now},{read}")
        
    if notificationID:
        make_notif = db.insert_data('notifications',
                       ['notificationID','userID','notification_categ','notification_desc','notification_date','read','data'],
                       [notificationID,userID,notification_categ, notification_desc,now,read,data])
  

    db.update_data('property', ['propertyID', 'property_status', 'remarks'],[propertyID, property_status,remarks])
    message = "Failed to approve the listing."
    return redirect(url_for('property_listings', success = message))

@app.route("/contracts")
def contracts():
    if 'sessionID' not in session:
        return redirect(url_for('lawyerindex'))
    
    if 'sessionID' in session:
        user_type = session['user_type']

        if user_type == 'admin':
            firstname = session['admin_firstname']
            middlename = session['admin_mname']
            lastname = session['admin_lastname']
        if user_type == 'lawyer':
            firstname = session['lawyer_firstname']
            middlename = session['lawyer_mname']
            lastname = session['lawyer_lastname']

        title = "B-Lease | List of Contracts"  

        leasing = db.get_all_data('leasing')
        
        user = db.get_all_data('user')
        
        return render_template("contracts.html", title=title, property=property, user=user,leasing=leasing,firstname=firstname,middlename=middlename,lastname=lastname,user_type=user_type)

@app.route("/decline", methods=['POST'])
def decline():

    leasingID = request.form['leasingID']
    leasing_remarks = request.form['leasing_remarks']
    leasing_status = "declined"
    lessorID = None
    lesseeID = None
    propertyAddress = None
    message = None
    now = None
    read = None
    notificationID = None
    
    
    # notification_desc = ''
    # leasingInfo = db.get_data('leasing','leasingID',leasingID)
    # if leasingInfo:
    #     lessorID = leasingInfo['lessorID']
    #     lesseeID = leasingInfo['lesseeID']
    #     # propertyAddress = leasingInfo['address']
    #     # notification_desc = f'Your contract at {propertyAddress} has been declined.'
    #     now = str(datetime.now())
    #     notification_categ = 'Contract Declined'

    #     read = "unread"
    #     image = []
     
    #     for filename in os.listdir(f'static/contracts/{leasingInfo["propertyID"]}/images/'):
    #         if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
    #             image.append(filename)

    #     image = image[0]
        
    #     data = {
    #         "leasingID":leasingInfo['leasingID'],
    #         "image":f"{image}",
    #     }

    #     status = "rejected"

    #     data = f"{leasingInfo['propertyID']},{image},{status}"
    #     if lessorID and propertyAddress and notification_desc and now and read:
    #         notificationID = util.generateUUID(f"{lessorID},{propertyAddress},{notification_categ},{notification_desc},{now},{read}")
        
    # if notificationID:
    #     make_notif = db.insert_data('notifications',
    #                    ['notificationID','lessorID','notification_categ','notification_desc','notification_date','read','data'],
    #                    [notificationID,lessorID,notification_categ, notification_desc,now,read,data])
  

    db.update_data('leasing', ['leasingID', 'leasing_status', 'leasing_remarks'],[leasingID, leasing_status,leasing_remarks])
    message = "Failed to approve the contract."
    return redirect(url_for('contracts', success = message))

@app.route("/view_contract", methods=['GET'])
def view_contract():
    if 'sessionID' not in session:
        return redirect(url_for('lawyerindex'))
    
    if 'sessionID' in session:
        user_type = session['user_type']

        if user_type == 'admin':
            firstname = session['admin_firstname']
            middlename = session['admin_mname']
            lastname = session['admin_lastname']
        if user_type == 'lawyer':
            firstname = session['lawyer_firstname']
            middlename = session['lawyer_mname']
            lastname = session['lawyer_lastname']

    leasingID = request.args.get('leasingID')
    user = db.get_all_data('user')
    title = "B-Lease | View Contracts" 
    leasing = db.get_all_data('leasing')
    payment = db.get_all_data('payment')

    leasing = db.get_specific_data('leasing',['leasingID'],[leasingID])
    
    

    leasing['documents'] = []
    for filename in os.listdir(f'static/contracts/{leasing["leasingID"]}'):
        if filename.endswith('for_review.pdf') or filename.endswith('for_review.doc') or filename.endswith('for_review.docx'):
            leasing['documents'].append(filename)



    return render_template("view_contract.html", title=title, leasing=leasing, user=user,payment=payment, user_type=user_type, firstname = firstname , middlename = middlename , lastname = lastname)


@app.route("/markasresolve")
def markasresolve():
    
    complaintID = request.args.get('complaintID')

    db.update_data('complaint', ['complaintID', 'complaint_status'],[complaintID, 'resolve'])
    message = "Approve"

    return redirect(url_for('manage_complaint', success = message))


@app.route('/updatethread',methods=['POST'])
def updatethread():
     
    complaintID = request.form['complaintID']
    thread_content = request.form['thread_content']
    created_at =str(datetime.now())
    message = ""
    if complaintID and thread_content:
        complaintthreadID = util.generateUUID(f"{complaintID},{thread_content},{created_at}")
        fields = ['complaintthreadID', 'complaintID', 'thread_content', 'created_at']
        data = [complaintthreadID, complaintID, thread_content, created_at]
        insert_thread = db.insert_data('complaint_thread', fields, data)
        if insert_thread:

    # fields = ['complaintID', 'complaint_threadID','complaint_subject','complaint_desc','complainerID','complaineeID','complaint_status','created_at']
    # data = [complaintID, complaint_threadID, complaint_subject, complaint_desc, complainerID, complaineeID, complaint_status, current_date]
    # db.insert_data('complaint',fields,data)

            complaintInfo = db.get_data('complaint','complaintID', complaintID)


            # Complainer Notification
            
            complainer_notification_desc = f"We have an update on your complaint"

            complainer_notification_data = {
                "userID":complaintInfo['complainerID'],
                "notification_categ":"Complaints",
                "notification_desc":complainer_notification_desc,
                "notification_data":complaintID
            }

            insert_complainer_notification = generate_notifications(complainer_notification_data)

            # Complainee Notification
            
            complainee_notification_desc = f"We have an update on the complaint filed against you"
            

            complainee_notification_data = {
                "userID":complaintInfo['complaineeID'],
                "notification_categ":"Complaints",
                "notification_desc":complainee_notification_desc,
                "notification_data":complaintID
            }

            insert_complainee_notification = generate_notifications(complainee_notification_data)

            message= "success"
        else:
            message = "error"

    return redirect(url_for('view_complaint',message=message, complaintID=complaintID))

@app.route("/approveContract")
def approveContract():

    leasingID = request.args.get('leasingID')

    leasing_payment_frequency = request.args.get('leasing_payment_frequency')
    pay_lessorID = request.args.get('lessorID')
    pay_lesseeID = request.args.get('lesseeID')
    pay_fee = request.args.get('leasing_total_fee')
    
    leasing_start_str = request.args.get('leasing_start')
    leasing_end_str = request.args.get('leasing_end')
    leasing_start = datetime.strptime(leasing_start_str, '%Y-%m-%d').date()
    leasing_end = datetime.strptime(leasing_end_str, '%Y-%m-%d').date()

    if leasing_payment_frequency == "1":
        paymentID = util.generateUUID(str(leasingID+ str(datetime.now())))
        leasing_start = (leasing_start).strftime("%Y-%m-%d")
        fields = ['paymentID', 'leasingID','pay_status','pay_lessorID','pay_lesseeID','pay_date','pay_fee']
        data = [paymentID, leasingID, 'pending', pay_lessorID, pay_lesseeID, leasing_start, pay_fee]
        db.insert_data('payment',fields,data)

    elif leasing_payment_frequency == "2":
        val = None
        ctr = 0
        fields = ['paymentID', 'leasingID','pay_status','pay_lessorID','pay_lesseeID','pay_date','pay_fee']
        ctr_date = leasing_start
        while ctr_date <= leasing_end:
            if ctr_date < leasing_start or ctr_date >= leasing_end:
                ctr_date += relativedelta(months=1)
                continue
            
            ctr+=1
            ctr_date += relativedelta(months=1)
        
        pay_fee = float(pay_fee)/ctr + 1
        current_date = leasing_start
        while current_date <= leasing_end:
            if current_date < leasing_start or current_date >= leasing_end:
                current_date += relativedelta(months=1)
                continue
            
            paymentID = util.generateUUID(str(leasingID+ str(datetime.now())))
            val = (current_date).strftime("%Y-%m-%d")
            data = [paymentID, leasingID, 'pending', pay_lessorID, pay_lesseeID, val, pay_fee]
            db.insert_data('payment',fields,data)
            
            current_date += relativedelta(months=1)

    elif leasing_payment_frequency == "3":
        val = None
        ctr = 0
        fields = ['paymentID', 'leasingID','pay_status','pay_lessorID','pay_lesseeID','pay_date','pay_fee']
        ctr_date = leasing_start
        while ctr_date <= leasing_end:
            if ctr_date < leasing_start or ctr_date >= leasing_end:
                ctr_date += relativedelta(months=3)
                continue
            
            ctr+=1
            ctr_date += relativedelta(months=3)
        
        pay_fee = float(pay_fee)/ctr + 1
        current_date = leasing_start
        while current_date <= leasing_end:
            if current_date < leasing_start or current_date >= leasing_end:
                current_date += relativedelta(months=3)
                continue
            
            paymentID = util.generateUUID(str(leasingID+ str(datetime.now())))
            val = (current_date).strftime("%Y-%m-%d")
            data = [paymentID, leasingID, 'pending', pay_lessorID, pay_lesseeID, val, pay_fee]
            db.insert_data('payment',fields,data)
            
            current_date += relativedelta(months=3)
    
    elif leasing_payment_frequency == "4":
        val = None
        ctr = 0
        fields = ['paymentID', 'leasingID','pay_status','pay_lessorID','pay_lesseeID','pay_date','pay_fee']
        ctr_date = leasing_start
        while ctr_date <= leasing_end:
            if ctr_date < leasing_start or ctr_date >= leasing_end:
                ctr_date += relativedelta(months=12)
                continue
            
            ctr+=1
            ctr_date += relativedelta(months=12)
        
        pay_fee = float(pay_fee)/ctr + 1
        current_date = leasing_start
        while current_date <= leasing_end:
            if current_date < leasing_start or current_date >= leasing_end:
                current_date += relativedelta(months=12)
                continue
            
            paymentID = util.generateUUID(str(leasingID+ str(datetime.now())))
            val = (current_date).strftime("%Y-%m-%d")
            data = [paymentID, leasingID, 'pending', pay_lessorID, pay_lesseeID, val, pay_fee]
            db.insert_data('payment',fields,data)
            
            current_date += relativedelta(months=12)

    getLeasingInfo = db.getLeasingInfo(leasingID)
    getLeasingInfo['propertyImage'] = util.getPropertyImageThumbnail(getLeasingInfo['propertyID'])

    lessor_notif_userID = getLeasingInfo['lessorID']
    notif_lessee = db.get_data('user', 'userID', getLeasingInfo['lesseeID'])
    notification_categ = "Leasing Contract"
    notif_read = "unread"
    notification_date = str(datetime.now())
    notif_data = f"{getLeasingInfo['leasingID']}*|*{getLeasingInfo['propertyID']}*|*{getLeasingInfo['address']}*|*{getLeasingInfo['leasing_status']}*|*{getLeasingInfo['propertyImage']}*|*{getLeasingInfo['lessorID']}*|*{getLeasingInfo['lesseeID']}"
    lessor_notification_desc = f"Your contract has been approved and is now ongoing"
    lessor_notificationID = util.generateUUID(f"{lessor_notif_userID},{notification_categ},{lessor_notification_desc},{notification_date},{notif_read},{notif_data}")
    lessor_notification_fields = ['notificationID', 'userID', 'notification_categ', 'notification_desc', 'notification_date', 'read', 'data']
    lessor_notification_data = [lessor_notificationID, lessor_notif_userID, notification_categ, lessor_notification_desc, notification_date, notif_read, notif_data]
    lessor_insert_notification = db.insert_data('notifications', lessor_notification_fields, lessor_notification_data)

    lessee_notif_userID = getLeasingInfo['lesseeID']
    lessee_notification_desc = f"Your contract has been approved and is now ongoing"
    lessee_notificationID = util.generateUUID(f"{lessee_notif_userID},{notification_categ},{lessee_notification_desc},{notification_date},{notif_read},{notif_data}")
    lessee_notification_fields = ['notificationID', 'userID', 'notification_categ', 'notification_desc', 'notification_date', 'read', 'data']
    lessee_notification_data = [lessee_notificationID, lessee_notif_userID, notification_categ, lessee_notification_desc, notification_date, notif_read, notif_data]
    lessee_insert_notification = db.insert_data('notifications', lessee_notification_fields, lessee_notification_data)


    db.update_data('leasing', ['leasingID', 'leasing_status'],[leasingID, 'ongoing'])

    for filename in os.listdir(f'static/contracts/{leasingID}'):
        if filename.endswith('for_review.pdf') or filename.endswith('for_review.doc') or filename.endswith('for_review.docx'):
            # Specify the current and new file paths
            current_file_path = f'static/contracts/{leasingID}/{filename}'
            new_file_path = f'static/contracts/{leasingID}/{util.generateUUID(str(datetime.now()))}_ongoing.pdf' 
            os.rename(current_file_path, new_file_path)

    message = "You have successfully approved the contract."
    return redirect(url_for('contracts', success = message))

@app.route("/declinecontracts")
def declinecontracts():
     
     if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
     
     leasingID = request.args.get('leasingID')

   
     title = "B-Lease | Decline Contract"  


   
     return render_template("declinecontracts.html", title=title, leasingID=leasingID)


@app.route("/ongoing_contracts")
def ongoing_contracts():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    if 'sessionID' in session:

        user_type = session['user_type']

        if user_type == 'admin':
            firstname = session['admin_firstname']
            middlename = session['admin_mname']
            lastname = session['admin_lastname']
        if user_type == 'lawyer':
            firstname = session['lawyer_firstname']
            middlename = session['lawyer_mname']
            lastname = session['lawyer_lastname']

        title = "B-Lease | Ongoing List of Contracts"  
        leasing = db.get_all_data('leasing')
    
        user = db.get_all_data('user')

        return render_template("ongoing_contracts.html", title=title, property=property, user=user,leasing=leasing,firstname=firstname,middlename=middlename,lastname=lastname, user_type=user_type)

@app.route("/finished_contracts")
def finished_contracts():
    if 'sessionID' not in session:
        return redirect(url_for('dashboard'))
    
    if 'sessionID' in session:
        user_type = session['user_type']

        if user_type == 'admin':
            firstname = session['admin_firstname']
            middlename = session['admin_mname']
            lastname = session['admin_lastname']
        if user_type == 'lawyer':
            firstname = session['lawyer_firstname']
            middlename = session['lawyer_mname']
            lastname = session['lawyer_lastname']

        title = "B-Lease | Finished List of Contracts"  
        leasing = db.get_all_data('leasing')
    
        user = db.get_all_data('user')

        return render_template("finished_contracts.html", title=title, property=property, user=user,leasing=leasing,firstname=firstname,middlename=middlename,lastname=lastname, user_type=user_type)

@app.route("/payment_reports")
def payment_reports():
    if 'sessionID' not in session:
            return redirect(url_for('index'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Payment Reports"   

        payment = db.get_all_data('payment')
        user = db.get_all_data('user')

        
        return render_template("payment_reports.html", title=title, payment=payment,user=user,firstname=firstname,middlename=middlename,lastname=lastname)


@app.route("/manage_complaint")
def manage_complaint():
    if 'sessionID' not in session:
            return redirect(url_for('index'))
    
    if 'sessionID' in session:
        firstname = session['admin_firstname']
        middlename = session['admin_mname']
        lastname = session['admin_lastname']
        title = "B-Lease | Manage Complaints"   

        complaint = db.get_all_data('complaint')
        user = db.get_all_data('user')

        return render_template("manage_complaint.html", title=title, complaint=complaint,user=user,firstname=firstname,middlename=middlename,lastname=lastname)

@app.route("/view_complaint")
def view_complaint():
    if 'sessionID' not in session:
            return redirect(url_for('index'))
    title = "B-Lease | View Complaint"   

    complaintID = request.args.get('complaintID')
   
    message = request.args.get('message')
    complaint = db.get_data('complaint', 'complaintID', complaintID)
    complaint_thread = db.get_thread(complaintID)

    return render_template("view_complaint.html", title=title, complaint=complaint, complaint_thread = complaint_thread, message=message)


# if __name__ == "__main__":
# #     # server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
# #     # server.serve_forever()
#     from geventwebsocket.handler import WebSocketHandler
#     from gevent.pywsgi import WSGIServer
    
#     http_server = WSGIServer(('0.0.0.0', 5000,), app, handler_class=WebSocketHandler)
#     http_server.serve_forever()
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
