import restapi
from config import api


#---------------------------------------------------------------
#API Endpoints are added here.
#API Endpoints classes are defined in the restapi.py
#---------------------------------------------------------------

# User management
api.add_resource(restapi.user, '/user')
api.add_resource(restapi.delete_user, '/delete_user')
api.add_resource(restapi.changepassword, '/changepassword')
api.add_resource(restapi.session, '/session')
api.add_resource(restapi.user_payment_method, '/user_payment_method')
api.add_resource(restapi.register, '/register')
api.add_resource(restapi.login, '/login')

# Leasing management
api.add_resource(restapi.Leasing, '/leasing')
api.add_resource(restapi.LeasingContracts, '/leasingcontracts')
api.add_resource(restapi.Leasing_Documents, '/leasingdocs')
api.add_resource(restapi.Leasing_Status, '/leasingstatus')

# Property management
api.add_resource(restapi.property, '/property')
api.add_resource(restapi.properties, '/properties')
api.add_resource(restapi.propertyimages, '/propertyimages/<string:propertyID>/<string:image>')
api.add_resource(restapi.NextPay, '/payLinks')

# Payment management
api.add_resource(restapi.Payment, '/pay')
api.add_resource(restapi.Paymongo, '/paymentintent/get')

# Notification management
api.add_resource(restapi.notifications, '/notifications')
api.add_resource(restapi.CountUnreadNotifications, '/notifications/countUnread')

# Feedback and complaint management
api.add_resource(restapi.feedback, '/feedback')
api.add_resource(restapi.countfeedback, '/countfeedback')
api.add_resource(restapi.countrating, '/countrating')
api.add_resource(restapi.complaint, '/complaints')
api.add_resource(restapi.complaintThread, '/complaintThread')

# Messaging
api.add_resource(restapi.Message, '/messages')
api.add_resource(restapi.CountMessage, '/messages/count')

# Document management
api.add_resource(restapi.leasingdocuments, '/leasingdocuments/<string:leasingID>/<string:contractDocument>')
api.add_resource(restapi.propertydocuments, '/propertydocuments/<string:propertyID>/<string:docName>')

#Property Favorites
api.add_resource(restapi.Favorites, '/favorites')

#Get Property Favorite IDs
api.add_resource(restapi.PropertyFavorites, '/propertyFavorites')


