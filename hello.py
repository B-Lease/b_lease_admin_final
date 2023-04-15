from flask import request
import db
from datetime import datetime
from dateutil.relativedelta import relativedelta
import util

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
paymentID = util.generateUUID(str(datetime.now()))

fields = ['paymentID', 'leasingID','pay_status','pay_lessorID','pay_lessorID','pay_date','pay_fee']
# loop over the range of dates and insert records
current_date = leasing_start
while current_date <= leasing_end:
    # check if the current date occurs within the leasing period
    if current_date < leasing_start or current_date >= leasing_end:
        current_date += relativedelta(months=1)
        continue
    
    paymentID = util.generateUUID(str(datetime.now()))
    val = (current_date).strftime("%Y-%m-%d")
    data = [paymentID, leasingID, 'pending', pay_lessorID, pay_lesseeID, val, pay_fee]
    db.insert_data('payment',fields,data)
    # increment the current date by one month
    current_date += relativedelta(months=1)


