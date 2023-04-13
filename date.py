import mysql.connector
from datetime import datetime
from dateutil.relativedelta import relativedelta

# define your leasing start and end dates
leasing_start_str = '2023-03-31'
leasing_end_str = '2025-03-31'
leasing_start = datetime.strptime(leasing_start_str, '%Y-%m-%d').date()
leasing_end = datetime.strptime(leasing_end_str, '%Y-%m-%d').date()


# loop over the range of dates and insert records
current_date = leasing_start
while current_date <= leasing_end:
    # check if the current date occurs within the leasing period
    if current_date < leasing_start or current_date >= leasing_end:
        current_date += relativedelta(months=1)
        continue

    val = (current_date)
    print(str(val))

    # increment the current date by one month
    current_date += relativedelta(months=1)