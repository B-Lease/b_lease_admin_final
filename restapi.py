from config import api, app
from flask_restful import Resource, reqparse
from flask import jsonify, request, abort, send_file, redirect, render_template, Response
from datetime import datetime, timedelta
from util import generateUUID, hashMD5, JSONEncoder, generate_otp
from emailverification import email_verification
from apscheduler.schedulers.background import BlockingScheduler
from flask_cors import CORS
import requests
import os
import db
import contract
import hmac
import hashlib
import time
import json
import util
from http.client import HTTPResponse




#--------------------------------------------------------------------------------
#RESTAPI resource classes are defined here
#RESTAPI endpoints are defined in the api_endpoints.py
#--------------------------------------------------------------------------------


PROPERTY_PATH = 'static/property_listings/'
# signup_put_args = reqparse.RequestParser()
# signup_put_args.add_argument("contact_number", type=str, help="Phone number of the user")
# class signup(Resource):
#     def get(self):
#         return {'data':'hello'}
#     def put(self,id):
#         args = signup_put_args.parse_args()
#         return { id:args}

class NextPay(Resource):
    def get(self):
        paymentID = request.args.get('paymentID')
        url = f'https://api-sandbox.nextpay.world/v2/paymentlinks/{paymentID}'
        #data = request.get_json()
        headers = request.headers
        headers = {
            "Content-Type": "application/json",
            "client-id": "ck_sandbox_g0rce9tf67r42g5ehygyhqy9"
        }
        response = requests.get(url, headers=headers)
        fin_response = response.json()
        return fin_response
    
    def post(self):
        payload = request.json
        client_secret = 'oz2lgjvuyhv6gpm03zopbf3y'
        body_string = json.dumps(payload, separators=(',', ':'))
        print(body_string)
        signature = hmac.new(client_secret.encode('utf-8'), body_string.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        print(signature)
        
        url = 'https://api-sandbox.nextpay.world/v2/paymentlinks/'
        #data = request.get_json()
        headers = {
            "Content-Type": "application/json",
            "client-id": "ck_sandbox_g0rce9tf67r42g5ehygyhqy9",
            "signature": str(signature)
        }
        response = requests.post(url, json=payload, headers=headers)
        fin_response = response.json()
        print(fin_response)
        return fin_response, 201

class Paymongo(Resource):
    def post(self):
        pass
    def get(self):
        url = "https://api.paymongo.com/v1/payment_intents/pi_ahmH3UGCNTP2S7cUvA7pFBTE"
        headers = {"accept": "application/json", "authorization": 'Basic c2tfdGVzdF9Sb2tNM0NkZ2pEYXEyclFtYWkzSERTSFA6'}
        response = requests.get(url, headers=headers)
        paymentIntent = response.json()
        attributes = paymentIntent['data']['attributes']['next_action']['redirect']['url']
        return paymentIntent, 201


class Payment(Resource):
    def get(self):
        userID = request.args.get('userID')
        paymentInfo = db.get_transactions(userID)
        if len(paymentInfo) != 0:
            payment_encoded = json.dumps(paymentInfo, default=str)
            return payment_encoded, 200
        else:
            return {'message': 'No transactions'}, 209
    
    def put(self):
        paymentID = request.args.get('paymentID')

        check_existing = db.check_existing_data(
            'payment', 'paymentID', paymentID)

        if check_existing:
            update_user = db.update_data('payment', ['paymentID', 'pay_status'], [paymentID, 'paid'])

            if update_user:
                return {
                    'message': f"Payment with paymentID: {paymentID} updated successfully"
                }, 200
            else:
                return {
                    'message': f"Error updating payment with paymentID:{paymentID}"
                }, 400
        else:
            return {'message': f'Payment with paymentID: {paymentID} does not exist'}, 400
        

# =======================================================================================
# REGISTER API CLASS
# =======================================================================================

register_args = reqparse.RequestParser()
register_args.add_argument(
    'email', type=str, help='Missing Email', required=True)
otp_dict = {}


class register(Resource):
    def get(self):
        email = str(request.args.get('email'))
        otp = str(request.args.get('otp'))
        isFound = False

        # print(otp_dict)
        for k, v in otp_dict.items():
            if k == email and v == otp:
                isFound = True

        if isFound:
            del otp_dict[email]
            # print(otp_dict)
            return {'message': 'OTP found'}, 200
        else:
            return {'message': 'OTP not found'}, 200

    def post(self):
        registerInfo = register_args.parse_args()

        email = request.json
        check_existing_user = db.check_existing_data('user','user_email', email['email'])

        if check_existing_user:
            return {'message': 'email already used'}, 200
        else:
            otp = generate_otp()
            send_email = email_verification(email['email'], otp)

            if send_email == True:
                otp_dict[email['email']] = otp
                # print(otp_dict)
                return {'message': 'success'}, 200
            else:
                return {'message': 'error'}, 200

    def put(self):
        pass

    def delete(self):
        email = request.args.get('email')

        if email:
            if email in otp_dict:
                otp = otp_dict[email]
                otp_dict.pop(email, None)
                # print(otp_dict)

                return {'message': f'OTP {otp} has expired '}, 200
            else:
                return abort(404, "OTP not found")
        else:
            return abort(404, "OTP not found")
        


# =======================================================================================
# USER API CLASS
# =======================================================================================

user_args = reqparse.RequestParser()
user_args.add_argument('phone_number', type=str,
                       help='Missing Phone number', required=True)
user_args.add_argument('user_password', type=str,
                       help='Missing User password', required=True)
user_args.add_argument('user_fname', type=str,
                       help='Missing User firstname', required=True)
user_args.add_argument('user_mname', type=str, help='Missing User middlename')
user_args.add_argument('user_lname', type=str,
                       help='Missing User lastname', required=True)
user_args.add_argument('user_birthdate', type=str,
                       help='Missing User birthdate', required=True)
user_args.add_argument('user_email', type=str,
                       help='Missing User email', required=True)


user_args_put = reqparse.RequestParser()
user_args_put.add_argument('userID', type=str, 
                           help='Missing User ID', required=True)
user_args_put.add_argument('user_fname', type=str,
                           help='Missing User firstname', required=True)
user_args_put.add_argument('user_mname', type=str,
                           help='Missing User middlename')
user_args_put.add_argument('user_lname', type=str,
                           help='Missing User lastname', required=True)
user_args_put.add_argument('user_birthdate', type=str,
                           help='Missing User birthdate', required=True)

user_args_put.add_argument('phone_number', type=str,
                           help='Missing Phone number', required=True)


user_args_patch = reqparse.RequestParser()
user_args_patch.add_argument(
    'sessionID', type=str, help='Missing Session ID', required=True)
user_args_patch.add_argument(
    'userID', type=str, help='Missing User ID', required=True)
user_args_patch.add_argument(
    'user_password', type=str, help='Missing User Password', required=True)

#=====================

class user(Resource):
    def get(self):
        userID = request.args.get('userID')
        if userID is None:
            userInfo = db.get_all_data('user')
            userInfo.remove('user_password')
            userInfo.remove('user_password_hashed')
            userInfo.remove('user_status')
            userInfo.remove('created_at')
            userJson = json.dumps(userInfo, indent=2, cls=JSONEncoder)
            return userJson, 200
        else:
            if userID is not None:
                userInfo = db.get_data('user', 'userID', userID)
                userInfo.pop('user_password')
                userInfo.pop('user_password_hashed')
                userInfo.pop('user_status')
                userInfo.pop('created_at')
                userJson = json.dumps(userInfo, default=str)

                return jsonify(userJson)

            else:
                return abort(400, 'User not found')

    def post(self):
        userInfo = user_args.parse_args()

        userJson = request.json
        userID = None
        fields = []
        data = []

        if 'userID' in userJson:
            userID = userJson.pop('userID')
        if 'imageUrl' in userJson:
            imageUrl = userJson.pop('imageUrl')

        for k, v in userJson.items():
            if v is not None:
                if k == 'phone_number':
                    fields.append('userID')
                    if userJson['auth_type'] == 'google':
                        userID = userID
                    else:
                         userID = generateUUID(json.dumps(userJson))
                    data.append(userID)
                if k == 'user_password':
                    fields.append('user_password_hashed')
                    data.append(hashMD5(v))
                if k == 'user_fname' or k == 'user_mname' or k == 'user_lname':
                    v = v.title()
                fields.append(k)
                data.append(v)

                if k == 'user_password':
                    fields.append('user_status')
                    data.append('active')
        if userJson['auth_type'] == 'google':
            fields.append('user_img')
            data.append(imageUrl)

        fields.append('created_at')
        data.append(str(datetime.now()))
        # print(fields)
        # print(data)
        check_existing = db.check_existing_data('user', 'userID', userID)
        if check_existing:
            return {'message': f'User with userID: {userID} already exist'}, 409
        else:
            insert_data_bool = db.insert_data('user', fields, data)
            if insert_data_bool:
                return {'message': 'Success user creation'}, 201
            else:
                return {'message': 'Error user creation'}, 400

    # def delete(self):
    #     sessionID = request.args.get('sessionID')
    #     userID = request.args.get('userID')

    #     check_session = db.get_specific_data('session', ['sessionID','userID','status'], [sessionID,userID,'valid'])

    #     if check_session:
    #         check_existing = db.check_existing_data('user', 'userID', userID)
    #         if check_existing:
    #             delete_user = db.delete_data('user', 'userID', userID)
    #             if delete_user:
    #                 return {
    #                     'message': f'deleted'
    #                 }, 200
    #             else:
    #                 return{
    #                     'message':f'Error deleting user with UserID:{userID}'
    #                 }, 400
    #         else:
    #             return abort(400,'Cannot delete. User not found')
    #     else:
    #         return abort(400, 'Session expired')

    def patch(self):
        userInfo = user_args_patch.parse_args()

        userJson = request.json

        fields = []
        data = []

        for k, v in userJson.items():
            if v is not None and k != 'user_password':
                fields.append(k)
                data.append(v)

        check_session = db.get_specific_data('session', ['sessionID', 'userID', 'status'], [
                                             userJson['sessionID'], userJson['userID'], 'valid'])

        if check_session:
            check_user_password = db.get_specific_data('user', ['userID', 'user_password_hashed', 'user_password'], [
                                                       userJson['userID'], hashMD5(userJson['user_password']), userJson['user_password']])
            if check_user_password:
                check_existing = db.check_existing_data(
                    'user', 'userID', userJson['userID'])
                if check_existing:
                    update_user = db.update_data('user', ['userID', 'user_status'], [
                                                 userJson['userID'], 'deactivated'])

                    if update_user:
                        return {
                            'message': f"deactivated"
                        }, 200
                    else:
                        return {
                            'message': f"error deactivating"
                        }, 200
                else:
                    return {
                        'message': f"user not found"
                    }, 200
            else:

                return {
                    'message': f"incorrect password"
                }, 200
        else:
            return abort(400, 'Session expired')

    def put(self):
        userInfo = user_args_put.parse_args()

        userJson = request.json

        fields = []
        data = []

        for k, v in userJson.items():
            if v is not None:
                fields.append(k)
                data.append(v)

        check_existing = db.check_existing_data(
            'user', 'userID', userJson['userID'])

        if check_existing:
            update_user = db.update_data('user', fields, data)

            if update_user:
                return {
                    'message': f"User with userID:{userJson['userID']} updated successfully"
                }, 200
            else:
                return {
                    'message': f"Error updating user with userID:{userJson['userID']}"
                }, 400
        else:
            return {'message': f'User with userID: {userJson["userID"]} does not exist'}, 400


# =======================================================================================
# DELETE USER API CLASS
# =======================================================================================

delete_user_args = reqparse.RequestParser()
delete_user_args.add_argument(
    'sessionID', type=str, help='Missing Session ID', required=True)
delete_user_args.add_argument(
    'userID', type=str, help='Missing User ID', required=True)
delete_user_args.add_argument(
    'user_password', type=str, help='Missing User Password', required=True)


class delete_user(Resource):
    def patch(self):
        userInfo = delete_user_args.parse_args()

        userJson = request.json

        fields = []
        data = []

        for k, v in userJson.items():
            if v is not None and k != 'user_password':
                fields.append(k)
                data.append(v)

        check_session = db.get_specific_data('session', ['sessionID', 'userID', 'status'], [
                                             userJson['sessionID'], userJson['userID'], 'valid'])

        if check_session:
            check_user_password = db.get_specific_data('user', ['userID', 'user_password_hashed', 'user_password'], [userJson['userID'], hashMD5(userJson['user_password']), userJson['user_password']])
            if check_user_password:
                check_existing = db.check_existing_data(
                    'user', 'userID', userJson['userID'])
                if check_existing:
                    delete_user = db.delete_data(
                        'user', 'userID', userJson['userID'])

                    if delete_user:
                        return {
                            'message': f"deleted"
                        }, 200
                    else:
                        return {
                            'message': f"error deleting"
                        }, 200
                else:
                    return {
                        'message': f"user not found"
                    }, 200
            else:

                return {
                    'message': f"incorrect password"
                }, 200
        else:
            return abort(400, 'Session expired')


# =======================================================================================
# CHANGE PASSWORD API CLASS
# =======================================================================================

changepassword_args = reqparse.RequestParser()
changepassword_args.add_argument(
    'sessionID', type=str, help='Missing Session ID', required=True)
changepassword_args.add_argument(
    'userID', type=str, help='Missing User ID', required=True)
changepassword_args.add_argument(
    'user_password', type=str, help='Missing Password', required=True)


class changepassword(Resource):
    def post(self):
        passwordInfo = changepassword_args.parse_args()

        passwordJson = request.json
        userID = None
        fields = []
        data = []
        for k, v in passwordJson.items():
            if v is not None:

                fields.append(k)
                data.append(v)
        check_session = db.get_specific_data('session', ['sessionID', 'userID', 'status'], [
                                             passwordJson['sessionID'], passwordJson['userID'], 'valid'])

        if check_session:
            check_existing = db.check_existing_data(
                'user', 'userID', passwordJson['userID'])
            if check_existing:
                update_user = db.update_data('user', ['userID', 'user_password', 'user_password_hashed'], [
                                             passwordJson['userID'], passwordJson['user_password'], hashMD5(passwordJson['user_password'])])

                if update_user:
                    return {
                        'message': f"passwordchanged"
                    }, 200
                else:
                    return {
                        'message': f"Error updating user with userID:{passwordJson['userID']}"
                    }, 400
            else:
                return abort(400, 'Cannot delete. User not found')
        else:
            return abort(400, 'Session expired')


# =======================================================================================
# LEASING API CLASS
# =======================================================================================



leasing_args_put = reqparse.RequestParser()
# for updating lease record
leasing_args_put.add_argument('leasingID', type=str, help='Missing LeasingID', required=True)
# the details that would be updated
leasing_args_put.add_argument('leasing_status', type=str, help='Missing Leasing Status', required=True)
leasing_args_put.add_argument('leasing_start', type=str, help='Missing Leasing Start', required=True)
leasing_args_put.add_argument('leasing_end', type=str, help='Missing Leasing End', required=True)
leasing_args_put.add_argument('leasing_payment_frequency', type=str, help='Missing Payment Frequency', required=True)
leasing_args_put.add_argument('leasing_total_fee', type=str, help='Missing Total Fee', required=True)
#leasing_args_put.add_argument('leasing_remarks', type=str, help='Missing Leasing Remarks', required=False)

leasing_contracts = reqparse.RequestParser()
# for creating lease contract
leasing_contracts.add_argument('lessor_name', type=str, help='Missing Lessor Name', required=True)
leasing_contracts.add_argument('lessee_name', type=str, help='Missing Lessee Name', required=True)
leasing_contracts.add_argument('address', type=str, help='Missing Address', required=True)
leasing_contracts.add_argument('land_description', type=str, help='Missing Land Description', required=True)
leasing_contracts.add_argument('purpose', type=str, help='Missing Purpose', required=True)
leasing_contracts.add_argument('security_deposit', type=bool, help='Missing Security Deposit', required=True)
leasing_contracts.add_argument('improvements', type=bool, help='Missing Improvements', required=True)
leasing_contracts.add_argument('erect_signage', type=bool, help='Missing Improvements', required=True)
leasing_contracts.add_argument('signature', type=str, help='Missing Signature', required=True)

class Leasing(Resource):
    def get(self):
        check_existing = request.args.get('check_existing')
        
        #FOR CHECKING EXISTING ONGOING LEASE RECORDS BEFORE CREATING A NEW LEASE RECORD
        if check_existing == 'yes':
            lesseeID = request.args.get('lesseeID')
            lessorID = request.args.get('lessorID')
            propertyID = request.args.get('propertyID')
            
            fields = ['lesseeID', 'lessorID', 'propertyID']
            values = [lesseeID, lessorID, propertyID]

            leasingInfo = db.get_all_specific_data('leasing', fields, values)
            #remove dictionaries in the list if it is equal to finished
            leasingInfoFiltered = [item for item in leasingInfo if item['leasing_status'] != 'finished']

            if len(leasingInfoFiltered) != 0:
                leasing_encoded = json.dumps(leasingInfoFiltered, default=str)
                return leasing_encoded, 200
            else:
                return {'message': 'No pending/ongoing leasing records'}, 209
        
        else:
            #USING LEASE RECORDS FOR LIST OF MESSAGES
            userID = request.args.get('userID')
            # as a lessee
            leasingInfo = db.join_tables(userID)
            
            if leasingInfo is not None:
                for each in leasingInfo:
                    each['images'] = []
                    for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                            # data['images'].append(str(filename))
                                
                            each['images'].append(filename)
                leasing_encoded = json.dumps(leasingInfo, default=str)
                return leasing_encoded, 200
            else:
                return abort(400, 'No conversations found')


    def post(self):
        lessorID = str(request.json['lessorID'])
        lesseeID = str(request.json['lesseeID'])
        propertyID = str(request.json['propertyID'])
        leasing_status = str(request.json['leasing_status'])


        param = str(lessorID + lesseeID + propertyID +
                    leasing_status + str(datetime.now()))
        leasingID = util.generateUUID(param)

        fields = ['leasingID', 'lessorID', 'lesseeID', 'propertyID', 'leasing_status']        
        data = [leasingID, lessorID, lesseeID, propertyID, leasing_status]



     
        # notificationID = None
        # userID = None
        # lessee = None
        # notification_categ = None
        # notification_desc = None
        # notification_date = None
        # read = None
        # data = None

        check_existing = db.check_existing_data('leasing', 'leasingID', leasingID)

        if check_existing:
            return {'message': f'User with userID: {leasingID} already exist'}, 409

        else:
            insert_data_bool = db.insert_data('leasing', fields, data)

            if insert_data_bool:
                notif_userID = lessorID
                notification_categ = "Property Inquiries"
                notif_lessee = db.get_data('user','userID', lesseeID)
                notif_lessor = db.get_data('user','userID', lessorID)
                notif_property = db.get_data('property','propertyID',propertyID)
                notification_desc = f"{notif_lessee['user_lname']}, {notif_lessee['user_fname']} has inquired about your property in {notif_property['address']}"
                notification_date = str(datetime.now())
                notif_read = "unread"

                notif_image = util.getPropertyImageThumbnail(notif_property['propertyID'])
                notif_data = f"{notif_userID}*|*{leasingID}*|*{notif_lessor['userID']}*|*{notif_lessor['user_fname']}*|*{notif_lessor['user_mname']}*|*{notif_lessor['user_lname']}*|*{notif_lessee['userID']}*|*{notif_lessee['user_fname']}*|*{notif_lessee['user_mname']}*|*{notif_lessee['user_lname']}*|*{notif_property['address']}*|*{notif_property['land_description']}*|*{notif_userID}*|*{notif_lessee['userID']}*|*{notif_lessee['user_fname']}*|*{notif_property['propertyID']}*|*{notif_image}"

                notificationID = util.generateUUID(f"{notif_userID},{notification_categ},{notification_desc},{notification_date},{notif_read},{data}")
                notification_fields = ['notificationID','userID','notification_categ','notification_desc','notification_date','read', 'data']
                notification_data = [notificationID, notif_userID, notification_categ, notification_desc, notification_date,notif_read,notif_data]
                insert_notification = db.insert_data('notifications', notification_fields, notification_data)
                
                return {'message': 'Successfully initiated lease request',
                        'leasingID': leasingID
                        }, 201

            else:
                return {'message': 'Unable to lease request'}, 400

    def put(self):
        leasingInfo = leasing_args_put.parse_args()
       
        fields = []
        data = []

        for k, v in leasingInfo.items():
            fields.append(k)
            data.append(v)
         

        check_existing = db.check_existing_data('leasing', 'leasingID', data[0])

        if check_existing:
            update_data_bool = db.update_data('leasing', fields, data)

            if update_data_bool:
                # after inserting important leasing data, create the pdf(contract) and
                # save the contract details to leasing_documents

                contractInfo = leasing_contracts.parse_args()
              
                insert_docs = contract.setContract(leasingInfo,contractInfo)

                # leasing_doc_name = str(leasing_docID + "_contract.pdf")
                # insert_docs = db.insert_data('leasing_documents', ['leasing_docID', 'leasingID', 'leasing_doc_name'], [
                #                              leasing_docID, leasingID, leasing_doc_name])
                if insert_docs:
              
                   

                    getLeasingInfo = db.getLeasingInfo(data[0])

                    notif_lessee = db.get_data('user','userID', getLeasingInfo['lesseeID'])
                    notif_lessor = db.get_data('user','userID',  getLeasingInfo['lessorID'])
                    getLeasingInfo['propertyImage'] = util.getPropertyImageThumbnail(getLeasingInfo['propertyID'])
            
                    #Lessee's Notification
                    lessee_notif_userID = notif_lessee['userID']
                    notification_categ = "Leasing Contract"
                    notif_read = "unread"
                    notification_date = str(datetime.now())
                    notif_data = f"{getLeasingInfo['leasingID']}*|*{getLeasingInfo['propertyID']}*|*{getLeasingInfo['address']}*|*{getLeasingInfo['leasing_status']}*|*{getLeasingInfo['propertyImage']}*|*{getLeasingInfo['lessorID']}*|*{getLeasingInfo['lesseeID']}"
                    
                    lessee_notification_desc = f"{notif_lessor['user_lname']},{notif_lessor['user_fname']} has set a leasing contract to the property you inquired."
                    lessee_notificationID = util.generateUUID(f"{lessee_notif_userID},{notification_categ},{lessee_notification_desc},{notification_date},{notif_read},{notif_data}")

                    lessee_notification_fields = ['notificationID','userID','notification_categ','notification_desc','notification_date','read', 'data']
                    lessee_notification_data = [lessee_notificationID, lessee_notif_userID, notification_categ, lessee_notification_desc, notification_date,notif_read,notif_data]
                    lessee_insert_notification = db.insert_data('notifications', lessee_notification_fields, lessee_notification_data)

                    return {'message': 'Successfully confirmed lease request'}, 204
                else:
                    db.delete_data('leasing', 'leasingID', data[0])

            else:
                return {'message': 'Unable to lease request'}, 400
        else:
            return abort(400, 'Leasing info not found')
        

    def delete(self):
        leasingID = request.args.get('leasingID')

        check_existing = db.check_existing_data(
            'leasing', 'leasingID', leasingID)
        if check_existing:
            delete_user = db.delete_data('leasing', 'leasingID', leasingID)
            if delete_user:
                return {
                    'message': f'Leasing ID:{leasingID} is deleted'
                }, 200
            else:
                return {
                    'message': f'Error deleting lease contract:{leasingID}'
                }, 400
        else:
            return abort(400, 'Cannot delete. Contract not found')


# =======================================================================================
# GET LEASING INFORMATION
# =======================================================================================

class GetLeasingInfo(Resource):
    def get(self):
        pass

# =======================================================================================
# LEASING CONTRACTS API CLASS
# =======================================================================================

class LeasingContracts(Resource):
    def get(self):
        # get specific data
        userID = request.args.get('userID')
        
        if userID:
            check_existing_user = db.check_existing_data('user','userID',userID)
            if check_existing_user:
                leasingInfo = db.get_leasing_contracts('leasing',['lessorID','lesseeID'],[userID,userID])
                if leasingInfo is not None:
                    for each in leasingInfo:
                        each['address'] = db.get_address_of_property(each['propertyID'])
                        if each['lessorID'] == userID:
                            lessee = db.get_name_of_user(each['lesseeID'])
                            each['name'] = f"{lessee['user_fname'].title()} {lessee['user_lname'].title()}"
                        if each['lesseeID'] == userID:
                            lessor = db.get_name_of_user(each['lessorID'])
                            each['name'] = f"{lessor['user_fname'].title()} {lessor['user_lname'].title()}"
                        each['images'] = []
                        for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                                # data['images'].append(str(filename))
                                    
                                each['images'].append(filename)
                    leasing_encoded = json.dumps(leasingInfo, default=str)
                    return leasing_encoded, 200
                else:
                    return {'message':'No contracts found'},200
            else:
                return abort(400,'User not found')
        else:
            return abort(400,'No userID present')

# =======================================================================================

class leasingdocs(Resource):
    def get(self, leasingID, file):
        filename = f'static/contracts/{leasingID}/{file}'

        if '.pdf' in filename:
            return send_file(filename, mimetype='application/pdf')
        if '.doc' or '.docx' in filename:
            return send_file(filename, mimetype='application/msword')   
    


# =======================================================================================
# LEASING DOCUMENTS API CLASS
# =======================================================================================

leasing_docs = reqparse.RequestParser()
leasing_docs.add_argument('leasingID', type=str,
                          help='Missing Leasing ID', required=True)


class Leasing_Documents(Resource):
    def get(self):
        leasingID = request.args.get('leasingID')
        contract = db.check_existing_data('leasing','leasingID',leasingID)
        if contract:
            pdfs=[]
            for filename in os.listdir(f'static/contracts/{leasingID}/'):
                if filename.endswith('_pending.docx'):
                    print(str(filename))
                    pdfs.append(filename)        
            if pdfs:
                file_path = f"static\contracts\{leasingID}\{pdfs[len(pdfs)-1]}"
                return send_file(file_path)
            else:
                return abort(400, 'No contract found')
        else:
            return abort(400, 'No leasing record found')

    def delete(self):
        return None
    
class Leasing_Status(Resource):
    def put(self):
        leasingID = request.json['leasingID']
        leasingID = request.args.get('leasingID')
        leasing_status = 'for review' if request.args.get('leasing_status') == '1' else 'declined'

        check_existing = db.check_existing_data(
            'leasing', 'leasingID', leasingID)
        
        fields = ['leasingID','leasing_status']
        data = [leasingID, leasing_status]
        if check_existing:
            update_data_bool = db.update_data('leasing', fields, data)
            if update_data_bool:
                #Lessor's Notification
                getLeasingInfo = db.getLeasingInfo(leasingID)
                getLeasingInfo['propertyImage'] = util.getPropertyImageThumbnail(getLeasingInfo['propertyID'])

                lessor_notif_userID = getLeasingInfo['lessorID']
                notif_lessee = db.get_data('user','userID', getLeasingInfo['lesseeID'])
                notification_categ = "Leasing Contract"
                notif_read = "unread"
                notification_date = str(datetime.now())
                notif_data = f"{getLeasingInfo['leasingID']}*|*{getLeasingInfo['propertyID']}*|*{getLeasingInfo['address']}*|*{getLeasingInfo['leasing_status']}*|*{getLeasingInfo['propertyImage']}*|*{getLeasingInfo['lessorID']}*|*{getLeasingInfo['lesseeID']}"
                
                lessor_notification_desc = f"{notif_lessee['user_lname']},{notif_lessee['user_fname']} has approved your leasing contract"
                lessor_notificationID = util.generateUUID(f"{lessor_notif_userID},{notification_categ},{lessor_notification_desc},{notification_date},{notif_read},{notif_data}")

                lessor_notification_fields = ['notificationID','userID','notification_categ','notification_desc','notification_date','read', 'data']
                lessor_notification_data = [lessor_notificationID, lessor_notif_userID, notification_categ, lessor_notification_desc, notification_date,notif_read,notif_data]
                lessor_insert_notification = db.insert_data('notifications', lessor_notification_fields, lessor_notification_data)

                return {'message': 'Contract status updated successfully'}, 201
            else:
                return {'message': 'Error approving contract'}, 400
        else:
            return {'message': f'Leasing record not found'}, 409



# =======================================================================================
# MESSAGE API CLASS
# =======================================================================================

class Message(Resource):
    def get(self):
        leasingID = request.args.get('leasingID')
        messages = db.get_items('message', 'leasingID', leasingID)
        sorted_messages = sorted(messages, key=lambda x: x['sent_at'])
        if messages is not None:
            messages_encoded = json.dumps(sorted_messages, default=str)
            print('messages_encoded')
            print(messages_encoded)
            return messages_encoded, 200
        else:
            return abort(400, 'No conversations found')


    def post(self):
        print(str('hello: '+request.json['leasingID']))
        leasingID = request.json['leasingID']
        msg_senderID = request.json['msg_senderID']
        msg_receiverID = request.json['msg_receiverID']
        msg_content = request.json['msg_content']
        sent_at = request.json['sent_at']
        
        fields = ['msgID', 'leasingID', 'msg_senderID',
                  'msg_receiverID', 'msg_content', 'sent_at']
        
        param = str(leasingID + msg_senderID + msg_receiverID + msg_content + sent_at)
        msgID = util.generateUUID(param)

        values = [msgID, leasingID, msg_senderID, msg_receiverID, msg_content, sent_at]

        message = db.insert_data('message', fields, values)
        #app.socketio.emit('add-message', msg_content, broadcast=True)
        return jsonify({'success': True})

class CountMessage(Resource):
    def get(self):
        leasingID = request.args.get('leasingID')
        if leasingID:
            count_message = db.countMessage(leasingID)

            if count_message:
                return {"totalMessages": count_message['countMessage']},200
        else:
            return abort("Missing Leasing ID", 404)
        
class CountUnreadNotifications(Resource):
    def get(self):
        userID = request.args.get("userID")

        if userID:
            count_unread = str(db.countUnreadNotifications(userID))

            if count_unread:
                return {"unreadNotifications":count_unread},200
        else:
            return abort("Missing user ID", 404)

class Message_Images(Resource):
    def get(self):
        return None

    def post(self):
        return None


# =======================================================================================
# LOGIN API CLASS
# =======================================================================================

login_args = reqparse.RequestParser()
login_args.add_argument('user_email', type=str,
                        help='Missing Email', required=True)
login_args.add_argument('user_ip', type=str,
                        help='Missing IP Address', required=True)

class login(Resource):

    def get(self):
        userID = request.args.get('userID')
        if userID is not None:
            userInfo = db.get_data('user', 'userID', userID)

            if userInfo:
                userJson = json.dumps(userInfo, default=str)
                
                return jsonify(userJson)
            else:
                return {'message':'User not found'}

        else:
            return {'message':'No userID'}
    def post(self):
        loginInfo = login_args.parse_args()

        loginJson = request.json
        sessionID = generateUUID(json.dumps(loginJson)+str(datetime.now()))
        userIP = None
        fields = []
        data = []
        accessToken = ''
        idToken = ''
        if 'accessToken' in loginJson:
            accessToken = loginJson.pop('accessToken')
        if 'idToken' in loginJson:
            idToken = loginJson.pop('idToken')
        if 'auth_type' in loginJson:
            auth_type = loginJson.pop('auth_type')

        for k, v in loginJson.items():
            if k == 'user_password':
                if auth_type != 'google':
                    fields.append('user_password_hashed')
                    data.append(hashMD5(v))
            if k != 'user_ip':
                fields.append(k)
                data.append(v)

            if k == 'user_ip':
                userIP = v

        # print(fields)
        # print(data)

        check_credential = db.get_specific_data('user', fields, data)

        if check_credential:
            session_fields = []
            session_data = []

            session_fields.append('sessionID')
            session_fields.append('userID')
            session_fields.append('accessToken')
            session_fields.append('idToken')
            session_fields.append('loginTime')
            session_fields.append('ipAddress')
            session_fields.append('status')

            session_data.append(sessionID)
            session_data.append(check_credential['userID'])
            session_data.append(accessToken)
            session_data.append(idToken)
            session_data.append(str(datetime.now()))
            session_data.append(userIP)
            session_data.append('valid')

            create_session = db.insert_data(
                'session', session_fields, session_data)

            if create_session:
                if check_credential['user_status'] == 'active':
                    return {'message': 'Login',
                            'sessionID': sessionID,
                            'userID': check_credential['userID'],
                            'accessToken':accessToken,
                            'idToken':idToken,
                            }, 200
                else:
                    update_data = db.update_data('user', ['userID', 'user_status'], [
                                                 check_credential['userID'], 'active'])

                    return {'message': 'User Deactivated. Login',
                            'sessionID': sessionID,
                            'userID': check_credential['userID'],
                            'accessToken':accessToken,
                            'idToken':idToken,
                            }, 200
            else:
                return abort(404, 'Error creating session')
        else:
            return {'message': 'Invalid Credentials'}, 404
        # if check_existing:
        #     return {'message':f'User with userID: {userID} already exist'},409
        # else:
        #     insert_data_bool = db.insert_data('user',fields,data)
        #     if insert_data_bool:
        #         return {'message':'Success user creation'},201
        #     else:
        #         return {'message':'Error user creation'},400


# =======================================================================================
# SESSION API CLASS
# =======================================================================================

session_args = reqparse.RequestParser()
session_args.add_argument('sessionID', type=str,
                          help='Missing Session ID', required=True)
session_args.add_argument(
    'userID', type=str, help='Missing User ID', required=True)


class session(Resource):
    # This is where session is checked if it is still valid or not
    def get(self):
        sessionID = request.args.get('sessionID')
        sessionInfo = db.get_specific_data(
            'session', ['sessionID', 'status'], [sessionID, 'valid'])
        if sessionInfo is not None:
            userJson = json.dumps(sessionInfo, default=str)
            # print(userJson)
            return {'message': 'Session valid'}, 200
        else:
            return {'message': 'Session expired'}, 200

    def post(self):
        sessionInfo = session_args.parse_args()

        sessionJson = request.json
        fields = []
        data = []
        for k, v in sessionJson.items():
            if v is not None:
                if k == 'userID':
                    fields.append('loginTime')
                    data.append(str(datetime.now()))
                fields.append(k)
                data.append(v)
        fields.append('status')
        data.append('open')

        check_existing = db.check_existing_data(
            'session', 'sessionID', sessionJson['sessionID'])
        if check_existing:
            return {'message': f'Session with sessionID: {sessionJson["sessionID"]} already exist'}, 409
        else:

            check_existing_user = db.check_existing_data(
                'user', 'userID', sessionJson['userID'])
            if check_existing_user:
                insert_data_bool = db.insert_data('session', fields, data)
                if insert_data_bool:
                    return {'message': 'Success session creation'}, 201
                else:
                    return {'message': 'Error session creation'}, 400
            else:
                return abort(400, 'User does not exist')

    # This is where logout occurs. Client sends a put request containing the sessionID. Server updates the data in the database by setting its status to 'expired'
    def put(self):
        sessionInfo = session_args.parse_args()

        sessionJson = request.json
        fields = []
        data = []
        for k, v in sessionJson.items():
            if v is not None:
                fields.append(k)
                data.append(v)

        fields.append('status')
        data.append('expired')
        fields.append('logoutTime')
        data.append(str(datetime.now()))

        check_existing = db.check_existing_data(
            'session', 'sessionID', sessionJson['sessionID'])
        if check_existing:
            check_existing_user = db.check_existing_data(
                'user', 'userID', sessionJson['userID'])
            if check_existing_user:
                update_data_bool = db.update_data('session', fields, data)
                if update_data_bool:
                    return {'message': 'Session expires'}, 201
                else:
                    return {'message': 'Error session expiration'}, 400
            else:
                return abort(400, 'User does not exist')
        else:
            return {'message': f'Session with sessionID: {sessionJson["sessionID"]} does not exist'}, 409


# =======================================================================================
# NOTIFICATION API CLASS | CRU

class notifications(Resource):
    def get(self):
        userID = request.args.get('userID')
        sessionID = request.args.get('sessionID')
        check_session = db.get_specific_data('session', ['sessionID','userID','status'], [sessionID,userID,'valid'])

        if check_session:
            notifications = db.get_items('notifications','userID',userID)
            if notifications:
                notificationJson = json.dumps(notifications, default=str)
                
                return jsonify(notificationJson )
            else:
                return {'message':'No notifications'},204

        else:
            return abort(401,'Authorization needed')
    def post(self):
        pass
    def put(self):
        pass
    def delete(self):
        pass

    def patch(self):
        userID = request.args.get('userID')
        notificationID = request.args.get('notificationID')
        sessionID = request.args.get('sessionID')
        check_session = db.get_specific_data('session', ['sessionID','userID','status'], [sessionID,userID,'valid'])

        if check_session:
            exist = db.get_data('notifications','notificationID',notificationID)
            if exist:
                notif_update = db.update_data('notifications',['notificationID','read'],[notificationID,'read'])
                
                return {"message":"Notification read"},202
            else:
                return {'message':'No notifications'},204

        else:
            return abort(401,'Authorization needed')

# =======================================================================================
# PAYMENT API CLASS | CRU

# =======================================================================================
# USER PAYMENT METHOD API CLASS | CRUD

upm_args = reqparse.RequestParser()
upm_args.add_argument('userID', type=str, help='Missing UserID', required=True)
upm_args.add_argument('userPay_accName', type=str,
                      help='Missing Account Name', required=True)
upm_args.add_argument('userPay_accNum', type=str,
                      help='Missing Account Number', required=True)


class user_payment_method(Resource):

    def get(self):
        pass

    def post(self):
        upmInfo = upm_args.parse_args()
        upmJson = request.json

        fields = []
        data = []
        paymethodID = json.dumps(upmJson)
        paymethodID = generateUUID(paymethodID)

        fields.append('paymethodID')
        data.append(paymethodID)
        for k, v in upmJson.items():
            if v is not None:
                fields.append(k)
                data.append(v)
                if k == 'userPay_accName':
                    fields.append('userPay_dateAdded')
                    data.append(str(datetime.now()))
        # print(fields)
        # print(data)

    def put(self):
        pass

    def delete(self):
        pass


# =======================================================================================
# COMPLAINT API CLASS | CR
complaint_args = reqparse.RequestParser()
complaint_args.add_argument(
    'complaintID', type=str, help='Missing Complaint ID', required=True)
complaint_args.add_argument(
    'complaint_subject', type=str, help='Missing Complaint Category', required=True)
complaint_args.add_argument(
    'complaint_desc', type=str, help='Missing Complaint Description', required=True)
complaint_args.add_argument(
    'complainerID', type=str, help='Missing ComplainerID', required=True)
complaint_args.add_argument(
    'complaineeID', type=str, help='Missing ComplaineeID', required=True)
complaint_args.add_argument(
    'complaint_status', type=str, help='Missing Complaint Status', required=True)
complaint_args.add_argument(
    'created_at', type=str, help='Missing Created At', required=True)



class complaint(Resource):
    def get(self):
        complaintID = request.args.get('leasingID')
        if complaintID is None:
            return abort(400, 'Missing leasing ID')
        else:
            complaints = db.get_items('complaint', 'complaintID', complaintID)
            if complaints:
                userJson = json.dumps(complaints, indent=2, cls=JSONEncoder)
                return userJson, 200
            else:
                return {'message': 'No complaints found'}

    def post(self):
        complaintInfo = complaint_args.parse_args()

        fields = []
        data = []

        for k, v in complaintInfo.items():
            fields.append(k)
            data.append(v)

        check_existing = db.check_existing_data('complaint', 'complaintID', data[0])

        if not check_existing:
            insert_data_bool = db.insert_data('complaint', fields, data)

            if insert_data_bool:
                
                return {'message': 'Successfully filed a complaint'}, 204

            else:
                return {'message': 'Unable to file'}, 400
        else:
            return abort(400, 'Complaint info not found')

class complaintThread(Resource):
    def get(self):
        complaintID = request.args.get('leasingID')
        if complaintID is None:
            return abort(400, 'Missing leasing ID')
        else:
            complaints = db.get_items('complaint_thread', 'complaintID', complaintID)
            if complaints:
                userJson = json.dumps(complaints, indent=2, cls=JSONEncoder)
                return userJson, 200
            else:
                return {'message': 'No complaints found'}

# =======================================================================================
# ADMIN API CLASS | CRUD

# =======================================================================================


# =======================================================================================
#    API CLASS | CRUD

# =======================================================================================

property_args_put = reqparse.RequestParser()
#  'userID': this.userID,
#           'sessionID':this.sessionID,
#           'propertyID':this.propertyID,
#           'price':price,
#           'property_type':property_type,
#           'moreDetails':moreDetails

property_args_put.add_argument('propertyID', type=str,
                           help='Missing Property ID')
property_args_put.add_argument('price', type=str,
                           help='Missing Property Price', required=True)
property_args_put.add_argument('property_type', type=str,
                           help='Missing Property Type', required=True)

property_args_put.add_argument('property_description', type=str,
                           help='Missing Property Details', required=True)


class property(Resource):
    def get(self):
        userID = request.args.get('userID')
        sessionID = request.args.get('sessionID')
        propertyID = request.args.get('propertyID')
        if userID and sessionID:
            check_user = db.check_existing_data('user', 'userID', userID)
            check_session = db.check_existing_data(
                'session', 'sessionID', sessionID)

            if check_user and check_session:
                if propertyID:
                    data = db.getIndividualPropertyListing(propertyID)

                    data['images'] = []
                  
                    for filename in os.listdir(f'static/property_listings/{data["propertyID"]}/images/'):
                        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                            # data['images'].append(str(filename))

                            data['images'].append(filename)
                    data['rating'] = db.averagePropertyRating(data['propertyID'])['average_rating']
                    print("RATINGG : ", data['rating'])
                    # print(data)

                else:
                    data = db.get_items('property', 'userID', userID)
                    # print(data)
                    for each in data:
                        each['images'] = []
                 
                        for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                            if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                                # data['images'].append(str(filename))

                                each['images'].append(filename)
                        each['rating'] = db.averagePropertyRating(each['propertyID'])['average_rating']
                        # print(each)
                        print("RATINGG : ", each['rating'])

                response = jsonify(data)
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response

        if not userID and sessionID:
            data = db.get_items('property', 'property_status', 'open')
            # print(data)
            for each in data:
                each['images'] = []
      
                for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                    if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                        # data['images'].append(str(filename))

                        each['images'].append(filename)
                # print(each)
                each['rating'] = db.averagePropertyRating(each['propertyID'])['average_rating']
                print("RATINGG : ", each['rating'])

            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            return abort(404, "Incomplete request data")

    def post(self):

        address = request.form['address']
        propertyLandSize = request.form['propertyLandSize']
        propertyLandSizeUnit = request.form['propertyLandSizeUnit']
        legalLandDescription = request.form['legalLandDescription']
        price = request.form['price']
        propertyType = request.form['propertyType']
        moreDetails = request.form['moreDetails']
        document = request.files.getlist('document')
        images = request.files.getlist('images')
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        sessionID = request.form['sessionID']
        userID = request.form['userID']
        property_status = 'pending'
        created_at = str(datetime.now())

        fields = []
        data = []
        print('LATITUDE: ', latitude)
        print('LONGITUDE: ', longitude)

        fields.append('propertyID')
        fields.append('userID')
        fields.append('property_status')
        fields.append('address')
        fields.append('latitude')
        fields.append('longitude')
        fields.append('property_description')
        fields.append('land_description')
        fields.append('size')
        fields.append('unit_type')
        fields.append('price')
        fields.append('property_type')
        fields.append('created_at')
        propertyID = generateUUID(
            str(userID) + "," + property_status + "," + address + "," + str(latitude) + "," + str(longitude) + "," +
            moreDetails + "," + legalLandDescription + "," + str(propertyLandSize) + "," + propertyLandSizeUnit + "," +
            str(price) + "," + propertyType + "," + created_at)

        data.append(propertyID)
        data.append(userID)
        data.append(property_status)
        data.append(address)
        data.append(latitude)
        data.append(longitude)
        data.append(moreDetails)
        data.append(legalLandDescription)
        data.append(propertyLandSize)
        data.append(propertyLandSizeUnit)
        data.append(price)
        data.append(propertyType)
        data.append(created_at)

   
        check_existing_property = db.check_existing_data(
            'property', 'propertyID', propertyID)

        if check_existing_property:
            return {'message': f'Property with propertyID: {propertyID} already exist'}, 409
        else:

         
            insert_property = db.insert_data('property', fields, data)

            # Create a directory for the property listings if it doesn't exist
            if not os.path.exists(PROPERTY_PATH):
                os.makedirs(PROPERTY_PATH)

            # Checks the directory of property listing with propertyID. If not present, will create one.
            if not os.path.exists(PROPERTY_PATH+"/"+propertyID):
                os.makedirs(PROPERTY_PATH+"/"+propertyID)

            # Checks the directory of property listing images with propertyID. If not present, will create one.
            if not os.path.exists(PROPERTY_PATH+"/"+propertyID+"/"+"images"):
                os.makedirs(PROPERTY_PATH+"/"+propertyID+"/"+"images")

            # Checks the directory of property listing documents with propertyID. If not present, will create one.
            if not os.path.exists(PROPERTY_PATH+"/"+propertyID+"/"+"documents"):
                os.makedirs(PROPERTY_PATH+"/"+propertyID+"/"+"documents")

            for image in images:
                image.save(os.path.join(PROPERTY_PATH+"/" +
                           propertyID+"/"+"images", image.filename))
            for doc in document:
                doc.save(os.path.join(PROPERTY_PATH+"/" +
                         propertyID+"/"+"documents", doc.filename))

            return {'message': 'success'}, 200

    def put(self):
        propertyInfo = property_args_put.parse_args()

        propertyJson = request.json
        userID = request.args.get('userID')
        sessionID = request.args.get('sessionID')
        

        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)


        if not check_session:
            return abort(404,"Session unauthorized")
        if not check_user:
            return abort(404,"User not found")
        


        fields = []
        data = []

        for k, v in propertyJson.items():
            if v is not None:
                fields.append(k)
                data.append(v)

        check_existing = db.check_existing_data(
            'property', 'propertyID', propertyJson['propertyID'])

        if check_existing:
            update_property = db.update_data('property', fields, data)

            if update_property:
                return {
                    'message': f"Property with propertyID:{propertyJson['propertyID']} updated successfully"
                }, 200
            else:
                return {
                    'message': f"Error updating property with property:{propertyJson['propertyID']}"
                }, 400
        else:
            return {'message': f'User with userID: {propertyJson["propertyID"]} does not exist'}, 400

    def delete(self):
        userID = request.args.get('userID')
        sessionID = request.args.get('sessionID')
        propertyID = request.args.get('propertyID')

        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)
        check_property = db.get_data('property', 'propertyID', propertyID)

        if not check_user:
            return abort(404, "User not found")
        if not check_session:
            return abort(404, "Session invalid")
        if not check_property:
            return abort(404,"Property not found")  
        

  
        check_leasing = db.checkOngoingLeasing(propertyID)

        if check_leasing:
            print("Cannot delete")
            return {"message":"Cannot delete leasing is ongoing"},403
        else:
            print("Clearing")
            empty_leasing = db.delete_data('leasing','propertyID', propertyID)
        print("Deleting")        
        delete_property = db.delete_data('property','propertyID',propertyID)

        if delete_property:
            delete_files = util.deleteFolder('property_listings',propertyID)
            
            if delete_files:
                print("Files deleted")
                print("Success deleting")
                return {"message":"Property deleted successfully"},200
            else:
                return abort(404,f"Property {propertyID} not deleted")

class SearchProperty(Resource):
    def get(self):
        sessionID = request.args.get("sessionID")

        query = request.args.get("query")
        check_session = util.checkSession(sessionID)


        if not check_session:
            return abort(404,"Session unauthorized")
        data = db.getSearchProperties(query)
        
        # print(data)
        if data:
            for each in data:
                each['images'] = []

                for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                    if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                        # data['images'].append(str(filename))

                        each['images'].append(filename)
                # print(each)
                each['rating'] = db.averagePropertyRating(each['propertyID'])['average_rating']
                print("RATINGG : ", each['rating'])

            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            return {"message":"No search results"},200
            
            

class propertyimages(Resource):
    def get(self, propertyID, image):
        filename = f'static/property_listings/{propertyID}/images/{image}'
        return send_file(filename, mimetype='image/jpeg')
    
class propertydocuments(Resource):
    def get(self,propertyID,docName):
        filename = f'static/property_listings/{propertyID}/documents/{docName}'

        if '.pdf' in filename:
            return send_file(filename, mimetype='application/pdf')
        if '.doc' or '.docx' in filename:
            return send_file(filename, mimetype='application/msword')

class leasingdocuments(Resource):
    def get(self,leasingID,contractDocument):
        filename = f'static/contracts/{leasingID}/{contractDocument}'

        if '.pdf' in filename:
            return send_file(filename, mimetype='application/pdf')
        if '.doc' or '.docx' in filename:
            return send_file(filename, mimetype='application/msword')        


# =======================================================================================
# PROPERTY LISTINGS API CLASS | CRUD

class properties(Resource):
    def get(self):

        sessionID = request.args.get('sessionID')

        check_existing_session = db.get_specific_data(
            'session', ['sessionID', 'status'], [sessionID, 'valid'])
        if check_existing_session:
            data = db.get_items('property', 'property_status', 'open')
            # print(data)
            for each in data:
                each['images'] = []
             
                for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                    if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                        each['images'].append(filename)
                # print(each)
                each['rating'] = db.averagePropertyRating(each['propertyID'])['average_rating']
            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:

            return abort(404, "Incomplete request data")

# =======================================================================================
# USER FEEDBACK API

feedback_args_post = reqparse.RequestParser()

# userID
# propertyID
# feedback_rating
# feedback_content
# created_at

feedback_args_post.add_argument('userID', type=str,
                           help='Missing User ID')

feedback_args_post.add_argument('propertyID', type=str,
                           help='Missing Property ID', required=True)

feedback_args_post.add_argument('feedback_rating', type=int,
                           help='Missing Feedback Rating', required=True)

feedback_args_post.add_argument('feedback_content', type=str,
                           help='Missing Feedback Content', required=True)

feedback_args_post.add_argument('sessionID', type=str,
                           help='Missing Session ID', required=True)


class feedback(Resource):
    def get(self):
        propertyID = request.args.get('propertyID')
        sessionID = request.args.get('sessionID')
        check_property = db.get_data('property','propertyID',propertyID)

        check_session = db.get_specific_data('session', ['sessionID','status'], [sessionID,'valid'])


        if not check_property:
            return abort(404,"Property not found")
        if not check_session:
            return abort(404,"Unauthorized access")
        
        if check_session:
            feedbacks = db.getPropertyFeedback(propertyID)
            if feedbacks:
                feedbacksJson = json.dumps(feedbacks, default=str)
                
                return jsonify(feedbacksJson )
            else:
                return {'message':'No feedbacks'},204

        else:
            return abort(401,'Authorization needed')
    def post(self):
        feedbackInfo = feedback_args_post.parse_args()

        feedbackJson = request.json
        userID = feedbackJson['userID']
        sessionID = feedbackJson.pop('sessionID')
        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)


        if not check_session:
            return abort(404,"Session unauthorized")
        if not check_user:
            return abort(404,"User not found")
        


        fields = []
        data = []
        fields.append('feedbackID')
        data.append(generateUUID(
            f"{feedbackJson['userID']},{feedbackJson['propertyID']},{feedbackJson['feedback_rating']},{feedbackJson['feedback_content']}"
        ))
        for k, v in feedbackJson.items():
            if v is not None:
                fields.append(k)
                data.append(v)
        fields.append('created_at')
        data.append(str(datetime.now()))
        check_existing = db.check_existing_data(
            'property', 'propertyID', feedbackJson['propertyID'])

        if check_existing:
            insert_feedback = db.insert_data('user_feedback', fields, data)

            if insert_feedback:
                return {
                    'message': f"Feedback with propertyID:{feedbackJson['propertyID']} submitted successfully"
                }, 200
            else:
                return {
                    'message': f"Error creating property feedback with property:{feedbackJson['propertyID']}"
                }, 400
        else:
            return {'message': f'User with userID: {feedbackJson["propertyID"]} does not exist'}, 400


class countfeedback(Resource):
    def get(self):
        propertyID = request.args.get('propertyID')
        sessionID = request.args.get('sessionID')

        check_property = db.get_data('property', 'propertyID',propertyID)
        check_session = util.checkSession(sessionID)\
        
        if not check_property:
            return abort(404, "Property not found")
        if not check_session:
            return abort(403,"Unauthorized access")
        
        countFeedback = db.totalPropertyFeedback(propertyID)

        if not countFeedback:
            return  {"message":"No feedback"},201
        if countFeedback:
            return jsonify(countFeedback )
        
class countrating(Resource):
    def get(self):
        propertyID = request.args.get('propertyID')
        sessionID = request.args.get('sessionID')

        check_property = db.get_data('property', 'propertyID',propertyID)
        check_session = util.checkSession(sessionID)\
        
        if not check_property:
            return abort(404, "Property not found")
        if not check_session:
            return abort(403,"Unauthorized access")
        
        countRating = db.averagePropertyRating(propertyID)

        if not countRating:
            return  {"message":"No feedback yet"},201
        if countRating:
            return jsonify(countRating)



# Favorites EndPoint
# =======================================================================================

favorites_args_post = reqparse.RequestParser()
favorites_args_post.add_argument('sessionID', type=str, help='Missing Session ID', required=True)
favorites_args_post.add_argument('userID', type=str, help='Missing User ID', required=True)
favorites_args_post.add_argument('propertyID', type=str, help='Missing Property ID', required=True)

class Favorites(Resource):
    def post(self):
        favoritesInfo = favorites_args_post.parse_args()
        favoritesJson = request.json
        userID = favoritesJson['userID']
        sessionID = favoritesJson.pop('sessionID')
        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)


        if not check_session:
            return abort(404,"Session unauthorized")
        if not check_user:
            return abort(404,"User not found")
        
        fields = ['property_favoritesID', 'userID', 'propertyID']
        data = [generateUUID(f"{favoritesJson['propertyID']}, {favoritesJson['userID']}"),favoritesJson['userID'],favoritesJson['propertyID']]

        insert_favorites = db.insert_data('property_favorites', fields, data)
        if insert_favorites:
            return {
                'message': f"Favorites added"
            }, 200
        else:
            return {
                'message': f"Error adding favorites"
            }, 400

    def get(self):
        userID = request.args.get('userID')
        sessionID = request.args.get('sessionID')

        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)

        if not check_session:
            return abort(404, "Session unauthorized")
        
        if not check_user:
            return abort(404, "User ID not found")
        
        property_favorites = db.getMyPropertyFavorites(userID)

        if property_favorites:
            for each in property_favorites:
                            each['images'] = []
                    
                            for filename in os.listdir(f'static/property_listings/{each["propertyID"]}/images/'):
                                if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                                    # data['images'].append(str(filename))

                                    each['images'].append(filename)
        
            return jsonify(property_favorites)
        else:
            return {"message": "No property favorites"},200

    def delete(self):
        userID = request.args.get("userID")
        sessionID = request.args.get("sessionID")
        propertyID = request.args.get("propertyID")

        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)
        check_property = db.get_data('property', 'propertyID', propertyID)

        if not check_session:
            return abort(404, "Session unauthorized")
        if not check_user:
            return abort(404,"User ID not found")
        if not check_property:
            return abort(404, "Property ID not found")
    
        fields = ['userID', 'propertyID']
        data = [userID, propertyID]

        delete_favorites = db.delete_data_where('property_favorites', fields, data)

        if delete_favorites:
            return {"message":"Property removed from favorites"},200
        else:
            return abort(404,"Error deleting property from favorites")



class PropertyFavorites(Resource):
    def get(self):
        userID = request.args.get('userID')
        sessionID = request.args.get('sessionID')

        check_session = util.checkSession(sessionID)
        check_user = db.get_data('user','userID',userID)

        if not check_session:
            return abort(404,"Session unauthorized")
        if not check_user:
            return abort(404,"User not found")
        
        property_favorites = db.getMyPropertyFavoriteIDs(userID)
        favorites = []
        for each in property_favorites:
            favorites.append(each['favorite_propertyID'])
      
        
      
        if property_favorites:
            return {"favorite_propertyIDs": favorites},200
        else:
            return {"message":"No property favorites found"}, 200

