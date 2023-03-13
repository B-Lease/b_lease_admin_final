import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage



def email_verification(email:str, code:str):
    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.



    # Define these once; use them twice!
    strFrom = 'thehackncode@gmail.com'
    strTo = email
    try:
        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'B-Lease OTP Verification'
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText('This is the alternative plain text message.')
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        msgText = MIMEText(
            f"""
            <html>
        <head></head>
        <body>
    
            <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
            
                <div style="margin:50px auto;width:70%;padding:20px 0">
                    <div style="border-bottom:1px solid #eee">
                        <center>
                        <img src="cid:image1" alt="" style="width:17%; margin: auto;">
                        </center>
                        <br>
                
                    </div>
                        <p style="font-size:1.1em">Hi,</p>
                        <p>Thank you for signing up. Use the following OTP to complete your Sign Up procedures. OTP is valid for 2 minutes</p>
                        <h2 style="background: #40A047;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{code}</h2>
                        <p style="font-size:0.9em;">Regards,<br />B-Lease</p>
                        <hr style="border:none;border-top:1px solid #eee" />
                    <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
                        <p>B-LEASE</p>
                        <p>HACK N' Code</p>
                        <p>Sanciangko St, Cebu City, 6000 Cebu</p>
                        <p>Philippines</p>
                    </div>
                </div>
            </div>
            </body>
        </html>
            """
            , 'html'
            )
        msgAlternative.attach(msgText)

        # This example assumes the image is in the current directory
        fp = open('static/images/b-lease_main.png', 'rb')
        msgImage = MIMEImage(fp.read(), _subtype="png")
        fp.close()

        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)

        # Send the email (this example assumes SMTP authentication is required)
        import smtplib
    
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('thehackncode@gmail.com', 'jrdkqpbfsfinasbw')
        mail.sendmail(strFrom, strTo, msgRoot.as_string())
        mail.quit()

        return True
    except Exception as e:
        error_message = str(e)
        return error_message
   