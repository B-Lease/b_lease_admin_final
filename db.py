from config import mysql


def get_data(table:str, field:str, value:str)->dict:
    cur = mysql.connection.cursor() 
    cur.execute(f'''SELECT * FROM {table} WHERE `{field}` = "{value}" ''')
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data

def get_items(table:str, field:str, value:str)->dict:
    cur = mysql.connection.cursor() 
    print(f'SELECT * FROM {table} WHERE `{field}` = "{value}" ')
    cur.execute(f'SELECT * FROM {table} WHERE `{field}` = "{value}" ')
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def check_existing_data(table:str, field:str, value:str)->bool:
    cur = mysql.connection.cursor()
    cur.execute(f'''SELECT EXISTS(SELECT * FROM `{table}` WHERE `{field}` = "{value}") AS check_existing''')
    data:bool = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data['check_existing']

def get_all_data(table:str)->dict:
    cur = mysql.connection.cursor()
    cur.execute(f'''SELECT * FROM {table}''')
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def get_all_data_properties()->dict:
    cur = mysql.connection.cursor()
    cur.execute(f'''SELECT * FROM property''')
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def count_data(table:str)->dict:
    cur = mysql.connection.cursor()
    cur.execute(f'''SELECT COUNT(*) AS total FROM `{table}`''')
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data


def insert_data(table:str, fields, value)->bool:
    cur = mysql.connection.cursor()

    flds = '`,`'.join(fields)
    dta = ""
    last_item = value[-1]
    for each in value:
        if each != last_item:
            if type(each) == str:
                dta = dta + f'''"{each}",'''
            else:
                dta = dta + f'''{each},'''
        else:
            if type(each) == str:
                dta = dta + f'''"{each}"'''
            else:
                dta = dta + f'''{each}'''
    cur.execute(f'''INSERT INTO `{table}`(`{flds}`) VALUES({dta})''')
    mysql.connection.commit()
    cur.close()
    return True

def delete_data_where(table:str, fields, data)-> bool:
    cur = mysql.connection.cursor()
    flds = []
    if len(fields) == len(data):

        for i in range(0, len(fields),1):
            flds.append(f'''`{fields[i]}` = "{data[i]}" ''')

        flds_final = ' AND '.join(flds)
        print(f"DELETE FROM `{table}` WHERE {flds_final}")
        cur.execute(f"DELETE FROM `{table}` WHERE {flds_final} ")
        mysql.connection.commit()
        cur.close()
        return True
    else:
        return False

def delete_data(table:str, field, value)->bool:
    cur = mysql.connection.cursor()
    cur.execute(f'''DELETE FROM `{table}` WHERE `{field}` = "{value}" ''')
    mysql.connection.commit()
    cur.close()
    return True


def update_data(table:str, fields, values)->bool:
    cur = mysql.connection.cursor()
    flds = []
    if len(fields) == len(values):
        for i in range(len(fields)):
            if type(values[i]) == str:
                flds.append(f'''`{fields[i]}` = "{values[i]}"''')
            else:
                flds.append(f'''`{fields[i]}` = {values[i]}''')
        flds_final = ", ".join(flds)
        cur.execute(f'''UPDATE `{table}` SET {flds_final} WHERE `{fields[0]}` = "{values[0]}"''')
        mysql.connection.commit()
        cur.close()
        return True
    else:
        return False


def get_specific_data(table:str, fields, values):
    cur = mysql.connection.cursor()
    flds = []
    
    if len(fields) == len(values):
        for i in range(len(fields)):
            if type(values[i]) == str:
                flds.append(f'''`{fields[i]}` = "{values[i]}"''')
            else:
                flds.append(f'''`{fields[i]}` = {values[i]}''')
            
        flds_final = " AND ".join(flds)
        cur.execute(f'''SELECT * FROM {table} WHERE {flds_final}''')
        data:dict = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        return data
    
def get_all_specific_data(table:str, fields, values):
    cur = mysql.connection.cursor()
    flds = []
    
    if len(fields) == len(values):
        for i in range(len(fields)):
            if type(values[i]) == str:
                flds.append(f'''`{fields[i]}` = "{values[i]}"''')
            else:
                flds.append(f'''`{fields[i]}` = {values[i]}''')
            
        flds_final = " AND ".join(flds)
        cur.execute(f'''SELECT * FROM {table} WHERE {flds_final}''')
        data:dict = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return data

def get_specific_data(table:str, fields, values):
    cur = mysql.connection.cursor()
    flds = []
    
    if len(fields) == len(values):
        for i in range(len(fields)):
            if type(values[i]) == str:
                flds.append(f'''`{fields[i]}` = "{values[i]}"''')
            else:
                flds.append(f'''`{fields[i]}` = {values[i]}''')
            
        flds_final = " AND ".join(flds)
        cur.execute(f'''SELECT * FROM {table} WHERE {flds_final}''')
        data:dict = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        return data

def get_all_specific_data(table:str, fields, values):
    cur = mysql.connection.cursor()
    flds = []
    
    if len(fields) == len(values):
        for i in range(len(fields)):
            if type(values[i]) == str:
                flds.append(f'''`{fields[i]}` = "{values[i]}"''')
            else:
                flds.append(f'''`{fields[i]}` = {values[i]}''')
            
        flds_final = " AND ".join(flds)
        cur.execute(f'''SELECT * FROM {table} WHERE {flds_final}''')
        data:dict = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return data

#not a database abstraction
#only used temporarily for getting the conversations per inquired property
def join_tables(userID:str):
    cur = mysql.connection.cursor() 
    cur.execute(f'''
        SELECT 
            l.leasingID,
            u1.userID as lessorID,
            u1.user_fname as lessor_fname,
            u1.user_mname as lessor_mname,
            u1.user_lname as lessor_lname,
            u2.userID as lesseeID,
            u2.user_fname as lessee_fname,
            u2.user_mname as lessee_mname,
            u2.user_lname as lessee_lname,
            p.propertyID as propertyID,
            p.address,
            p.land_description,
            m.msg_content,
            m.sent_at
        FROM 
            user u
        JOIN
            leasing l ON 
                u.userID  = l.lessorID  || u.userID  = l.lesseeID 
        JOIN 
            user u1 ON l.lessorID  = u1.userID
        JOIN 
            user u2 ON l.lesseeID  = u2.userID
        JOIN
            property p ON l.propertyID  = p.propertyID
        LEFT JOIN
            (SELECT 
                leasingID, 
                MAX(sent_at) AS latest_sent_at 
            FROM 
                message 
            GROUP BY 
                leasingID) AS latest_msg
        ON 
            l.leasingID = latest_msg.leasingID
        JOIN 
            message m
        ON 
            latest_msg.leasingID = m.leasingID AND latest_msg.latest_sent_at = m.sent_at
        WHERE 
        u.userID  = '{userID}';
    ''')
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def get_leasing_contracts(table:str, fields, values):
    cur = mysql.connection.cursor()
    flds = []
    
    if len(fields) == len(values):
        for i in range(len(fields)):
            if type(values[i]) == str:
                flds.append(f'''`{fields[i]}` = "{values[i]}"''')
            else:
                flds.append(f'''`{fields[i]}` = {values[i]}''')
            
        flds_final = " OR ".join(flds)
        cur.execute(f'''SELECT * FROM {table} WHERE {flds_final}''')
        data:dict = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return data

def get_transactions(userID:str):
    cur = mysql.connection.cursor() 
    cur.execute(f'''
        SELECT p.*, l.leasing_payment_frequency, pr.address 
        FROM payment p
        INNER JOIN leasing l ON p.leasingID = l.leasingID
        INNER JOIN property pr on l.propertyID = pr.propertyID
        WHERE `pay_lessorID` = "{userID}" || `pay_lesseeID` = "{userID}"
    ''')
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def get_name_of_user(userID):
    cur = mysql.connection.cursor() 
    cur.execute(f'''SELECT `user_fname`,`user_lname` FROM `user` WHERE `userID` = "{userID}" ''')
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data

def get_address_of_property(propertyID):
    cur = mysql.connection.cursor() 
    cur.execute(f'''SELECT `address` FROM `property` WHERE `propertyID` = "{propertyID}" ''')
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return str(data['address'])


def insert_json_data(table,field,data,id):
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE `{table}` SET (`{field[1]}` = '{data}') WHERE `{field[0]}` = '{id}' ")
    mysql.connection.commit()
    cur.close()
    return True

def emptyLeasingProperty(propertyID):
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE `leasing` SET `propertyID` = NULL WHERE `propertyID` = '{propertyID}' ")
    mysql.connection.commit()
    cur.close()
    return True

def checkOngoingLeasing(propertyID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM leasing WHERE propertyID = '{propertyID}' AND (leasing_status = 'ongoing' OR leasing_status = 'pending' OR leasing_status = 'for review' )")
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data


def get_complaints(table:str, field:str, value:str)->dict:
    cur = mysql.connection.cursor() 
    print(f'SELECT * FROM {table} WHERE {field} = "{value}" ')
    cur.execute(f'SELECT * FROM {table} WHERE {field} = "{value}" ORDER BY created_at')

def getPropertyFeedback(propertyID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT f.feedbackID,f.userID,u.user_fname, u.user_lname, f.propertyID,f.feedback_rating,f.feedback_content,f.created_at FROM `user_feedback` f, `user` u WHERE f.userID = u.userID AND f.propertyID = '{propertyID}' ")

    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data


def get_thread(complaintID):
    cursor = mysql.connection.cursor() 
    cursor.execute(f'SELECT * FROM complaint_thread WHERE `complaintID` = "{complaintID}" order by `created_at` ASC')
    result:dict = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    if result:
        return result
        
    else:
        return None


def getLoggingReport():
    cur = mysql.connection.cursor()
    query = """
        SELECT u.userID, u.user_fname, u.user_mname, u.user_lname, u.user_email, s.status, MAX(s.loginTime) as lastLogin
        FROM user u
        JOIN session s ON u.userID = s.userID
        GROUP BY u.userID, u.user_fname, u.user_mname, u.user_lname, u.user_email, s.status
        ORDER BY lastLogin DESC
    """
    cur.execute(query)
    result = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return result

def totalPropertyFeedback(propertyID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT COUNT(*) FROM `user_feedback`  WHERE `propertyID` = '{propertyID}'")
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data

def averagePropertyRating(propertyID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT IFNULL(ROUND(AVG(`feedback_rating`),1),0) AS `average_rating` FROM `user_feedback` WHERE `propertyID` = '{propertyID}'")
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data


def countMessage(leasingID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT IFNULL(COUNT(*),0) AS countMessage FROM `message` WHERE `leasingID` = '{leasingID}'")
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data


def countUnreadNotifications(userID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT IFNULL(COUNT(*),0) as unreadNotifications FROM b_lease.notifications WHERE `userID` = '{userID}' AND `read` = 'unread'")
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data['unreadNotifications']

def getLeasingInfo(leasingID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT l.leasingID,l.propertyID,p.address,l.leasing_status,l.lessorID,l.lesseeID FROM leasing l, property p WHERE l.propertyID = p.propertyID AND l.leasingID = '{leasingID}' GROUP BY l.leasingID")
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data

def getMyPropertyFavoriteIDs(userID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT `propertyID` AS favorite_propertyID FROM property_favorites WHERE `userID` = '{userID}'")
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def getMyPropertyFavorites(userID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT p.* FROM property p INNER JOIN property_favorites pf ON p.propertyID = pf.propertyID WHERE pf.userID = '{userID}'")
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def getIndividualPropertyListing(propertyID):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT p.*, u.user_fname, u.user_lname FROM property p INNER JOIN user u ON p.userID = u.userID WHERE propertyID = '{propertyID}'")
    data:dict = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return data


def getSearchProperties(query:str):
    cur = mysql.connection.cursor() 
    cur.execute(f"SELECT * FROM property WHERE `address` LIKE '%{query}%' AND `property_status` = 'open'")
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data


    