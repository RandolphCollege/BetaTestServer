from GPSBetaTest import Gps
from StepCountBetaTest import StepCount
from RoomLocationBetaTest import RoomLocation
from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
import multiprocessing
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import Encoders


class RunBetaTestAnalysis(DatabaseWrapper, multiprocessing.Process):

    def __init__(self, database):
        multiprocessing.Process.__init__(self)
        DatabaseWrapper.__init__(self,database)
        self.database = database

    def get_patients_list(self):
        if not self.fetch_from_database(database_name='config',
                                        table_name='caregiverPatientPairs',
                                        to_fetch='patient',
                                        to_fetch_modifiers='DISTINCT'):
            return []
        patient_list = [row[0] for row in self]

        for patient in patient_list:
            # If the patient does not have a valid profile, remove from list
            if not self.fetch_from_database(database_name='_' + patient,
                                            table_name='profile',
                                            to_fetch='VALID',
                                            where=['VALID', '=', 1]):
                patient_list.remove(patient)
        return patient_list

    def email_beta_data(self, file_path_list):
        email_dict = {'julien.jacquemot': 'julien.jacquemot@gmail.com',
                      '2773': 'segrissom@randolphcollege.edu',
                      '2771': 'ssdill@randolphcollege.edu',
                      '2774': 'amhart@randolphcollege.edu',
                      '2775': 'stucker@randolphcollege.edu',
                      '2751': 'tamara.braley@unmc.edu',
                      'george.netscher': 'gnetscher@gmail.com',
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
                       'StepCount': 'https://www.surveymonkey.com/r/StepCountAccuracyReview',
                       'RoomLocation': 'No link available'}

        file_path_list = [f for f in file_path_list if f is not None]
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

        wouldbe_recipient = email_dict[previous_dce]
        recipient = 'afella@randolphcollege.edu'

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

        wouldbe_string = "\n*****************************************************************\n\n" + \
                         "This message would have been sent to %s\n\n" % wouldbe_recipient + \
                         "******************************************************************\n"

        body.attach(MIMEText(body_base + gps_request + step_request + room_request + wouldbe_string))
        msg.attach(body)

        for att in range(len(file_path_list)):
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file_path_list[att], "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_path_list[att]))
            msg.attach(part)

        s.sendmail(fromEmail, toEmail, msg.as_string())

    def launch_beta_evals(self, patient_id):
        betaGPStest = Gps(self.database, patient_id)
        gpsPath = betaGPStest.run()


        betaStepstest = StepCount(self.database, patient_id)
        stepPath = betaStepstest.run()

        betaRoomtest = RoomLocation(self.database, patient_id)
        roomPath = betaRoomtest.run()

        return [gpsPath, stepPath, roomPath]

    def run(self):
        patient_ids = self.get_patients_list()
        for patient_id in patient_ids:
            file_list = self.launch_beta_evals(patient_id)
            self.email_beta_data(file_list)
