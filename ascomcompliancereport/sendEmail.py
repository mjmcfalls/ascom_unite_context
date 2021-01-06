import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "from@email.address"
receiver_email = "to@email.address"
# password = input("Type your password and press enter:")
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Ascom Compliance Report"

message = """Ascom Compliance Report"""
msg.attach(MIMEText(message, 'plain'))
try:

    smtpObj = smtplib.SMTP('smtp-server')
    # smtpObj.ehlo()
    # smtpObj.starttls()
    # smtpObj.ehlo()
    smtpObj.sendmail(sender_email, receiver_email, msg.as_string())         
    print("Successfully sent email")
except Exception as e:
    print(e)
    print("Error: unable to send email")    