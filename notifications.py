from datetime import datetime, timedelta
from util import generateUUID, hashMD5, JSONEncoder, generate_otp
import os
import db
import hashlib
import time
import json
import util





def generate_notifications(data:dict):
    # Data values:
    # -----------------------------------
    # userID
    # notification_categ
    # notification_desc
    # notification_data
    # notification_date
    # -----------------------------------

    userID = data['userID']
    notification_categ = data['notification_categ']
    notification_desc = data['notification_desc']
    notification_date = str(datetime.now())
    read = "unread"
    data = data['notification_data']


    notificationID = util.generateUUID(f"{userID},{notification_categ},{notification_desc},{notification_date},{read},{data}")
    notification_fields = ['notificationID','userID','notification_categ','notification_desc','notification_date','read', 'data']
    notification_data = [notificationID, userID, notification_categ, notification_desc, notification_date,read,data]


    insert_notification = db.insert_data('notifications', notification_fields, notification_data)

    if insert_notification:
        return True
    else:
        return False
     
 