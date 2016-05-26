import smtplib
import base64
import datetime


class Email:
    def __init__(self, receiver):
        self.receiver = receiver
        self.sender   = "cmsfm2016@outlook.com"
        self.marker = "AUNIQUEMARKER"

    def headers(self):
        today = datetime.date.today()
        part1  = "From: Daily Beta Test Metrics <%s>\n" % self.sender
        part1 += "To:<%s>\n" % self.receiver
        part1 += "Subject: %s\n" % today.strftime('%d, %b %Y Beta Test Metrics 2')
        part1 += "MIME-Version: 1.0\n"
        part1 += "Content-Type: multipart/mixed; boundary=%s\n" % self.marker
        part1 += "--%s\n" % self.marker
        return part1

    def body_headers(self):
        part2  = "Content-Type: text/plain\n"
        part2 += "Content-Transfer-Encoding:8bit\n"
        part2 += "\n"
        part2 += "%s\n" % self.compose_body()
        part2 += "--%s\n" %self.marker
        return part2

    def compose_body(self):
        body  = "\nAttached are your summary metrics. Please review and complete the\n"
        body += "respective survey.\n"
        body += "\n"
        body += "Thank you,\n"
        body += "The Functional Monitoring Team\n"
        return body


    def add_attachment(self, filename):
        # Define the attachment section
        fo = open(filename, "rb")
        filecontent = fo.read()
        encodedcontent = base64.b64encode(filecontent)
        part3 = "Content-Type: multipart/mixed; name=\"%s\"\n" % filename
        part3 += "Content-Transfer-Encoding:base64\n"
        part3 += "Content-Disposition: attachment; filename=%s\n" % filename
        part3 += "%s\n" % encodedcontent
        part3 += "--%s--\n" % self.marker
        return part3

    def send_email(self):
        part1 = self.headers()
        part2 = self.body_headers()
        part3 = self.add_attachment("main.py")
        #part3 += self.add_attachment("EmailClass.py")
        message = part1 + part2 + part3
        print message
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(self.sender, self.receiver, message)
            print "Successfully sent email"
        except Exception:
            print "Error: unable to send email"
email = Email("bbzylstra@randolphcollege.edu")
email.send_email()
