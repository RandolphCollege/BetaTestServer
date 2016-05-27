import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import Encoders
import os


def send_message(file_path_list):
    email_dict = {'julien.jacquemot': 'julien.jacquemot@gmail.com',
                  '2773': 'segrissom@randolphcollege.edu',
                  '2771': 'ssdill@randolphcollege.edu',
                  '2774': 'amhart@randolphcollege.edu',
                  '2775': 'stucker@randolphcollege.edu',
                  '2751': 'tamara.braley@unmc.edu',
                  'george.netscher': 'erhuber@randolphcollege.edu',  # ''gnetscher@gmail.com',
                  '2762': 'Michael.Schaffer@ucsf.edu',
                  '2777': 'Kasia.Gawlas@ucsf.edu',
                  '2770': 'sbonasera@unmc.edu',
                  'sarah.dulaney': 'Sarah.Dulaney@ucsf.edu',
                  '2747': 'kschenk@randolphcollege.edu',
                  '2776': 'gishen@uchicago.edu',
                  '2772': 'erhuber@randolphcollege.edu',
                  '2750': 'Kasia.Gawlas@ucsf.edu',
                  '2749': 'Kasia.Gawlas@ucsf.edu',
                  '2781': 'tamara.braley@unmc.edu',
                  '2780': 'tamara.braley@unmc.edu',
                  '2782': 'tamara.braley@unmc.edu'}

    survey_dict = {'GPS': 'https://www.surveymonkey.com/r/BetaTestAccuracyReport',
                   'StepCount': 'No link available',
                   'RoomLocation': 'No link available'}

    # make sure data is being passed in
    if file_path_list == []:
        return []

    # make sure all files attached are supposed to go to the same person
    previous_dce = os.path.basename(file_path_list[0].split('_', 1)[0])
    for f in range(len(file_path_list)):
        current_dce = os.path.basename(file_path_list[f].split('_', 1)[0])
        if email_dict[current_dce] != email_dict[previous_dce]:
            print 'email attachment or directory mismatch: %s != %s' % (previous_dce, current_dce)
            return []
        previous_dce = current_dce

    recipient = email_dict[previous_dce]

    # get the types of files that are included
    file_types = [os.path.basename(file_path_list[f].split('_')[-1]) for f in range(len(file_path_list))]

    msg = MIMEMultipart()
    s = smtplib.SMTP('localhost')

    toEmail, fromEmail = recipient, 'func@you.net'
    msg['Subject'] = 'FM Beta Data Verification'
    msg['From'] = fromEmail
    msg['To'] = ', ' + toEmail

    body = MIMEMultipart('alternative')
    body_base = 'Please fill out the following surveys for the corresponding attached data:\n\n'

    if any(t == 'GPSData.kml' for t in file_types):
        gps_request = 'GPS: %s\n' % survey_dict['GPS']
    else:
        gps_request = ''

    if any(t == 'StepCount.png' for t in file_types):
        step_request = 'Step Count: %s\n' % survey_dict['StepCount']
    else:
        step_request = ''

    if any(t == 'RoomLocation.png' for t in file_types):
        room_request = 'Room Location: %s\n' % survey_dict['RoomLocation']
    else:
        room_request = ''

    body.attach(MIMEText(body_base + gps_request + step_request + room_request))
    msg.attach(body)

    for att in range(len(file_path_list)):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_path_list[att], "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_path_list[att]))
        msg.attach(part)

    s.sendmail(fromEmail, toEmail, msg.as_string())


file_name = "george.netscher_2016-05-25_Wednesday_GPSData.kml"
current_dir = os.path.dirname(os.getcwd())
gps_file_path = 'gpsSaves'
gps_save_path = os.path.join(current_dir, gps_file_path)
gps_path = os.path.join(gps_save_path, file_name)

step_file_name = 'george.netscher_2016-05-25_Wednesday_StepCount.png'
step_file_path = 'stepSaves'
step_save_path = os.path.join(current_dir, step_file_path)
step_path = os.path.join(step_save_path, step_file_name)

send_message([gps_path, step_path])
