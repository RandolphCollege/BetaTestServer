import smtplib
import base64

filename = "/home/careeco/BetaTestServer/databaseLearner.py"

# Read a file and encode it into base64 format
fo = open(filename, "rb")
filecontent = fo.read()
encodedcontent = base64.b64encode(filecontent)  # base64

sender = 'fuckyou@outlook.com'
receiver = 'erhuber@randolphcollege.edu '

marker = "AUNIQUEMARKER"

body ='''
FUCK YOU
'''
# Define the main headers.
part1 = """From: A Silly Cunt <fuck@you.net>
To: Another Silly Cunt <silly.cunt@gmail.com>
Subject: Sending Attachement
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=%s
--%s
""" % (marker, marker)

# Define the message action
part2 = """Content-Type: text/plain
Content-Transfer-Encoding:8bit

%s
--%s
""" % (body,marker)

# Define the attachment section
part3 = """Content-Type: multipart/mixed; name=\"%s\"
Content-Transfer-Encoding:base64
Content-Disposition: attachment; filename=%s

%s
--%s--
""" %(filename, filename, encodedcontent, marker)
message = part1 + part2 + part3

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, receiver, message)
   print "Successfully sent email"
except Exception:
   print "Error: unable to send email"