from flask_mysqldb import MySQL
from app import mysql


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

def get_transactions(table:str, userID:str):
    cur = mysql.connection.cursor() 
    cur.execute(f'SELECT * FROM {table} WHERE `pay_lessorID` = "{userID}" || `pay_lesseeID` = "{userID}"')
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
    data:dict = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

def get_thread(complaintID):
    cursor = mysql.connection.cursor() 
    cursor.execute(f'SELECT * FROM complaint_thread WHERE `complaintID` = "{complaintID}"')
    result:dict = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    if result:
        return result
        
    else:
        return None
