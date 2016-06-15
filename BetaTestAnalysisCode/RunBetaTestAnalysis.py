from GPSBetaTest import Gps
from StepCountBetaTest import StepCount
from RoomLocationBetaTest import RoomLocation
from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
import multiprocessing
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import Encoders


class RunBetaTestAnalysis(DatabaseWrapper, multiprocessing.Process):

    def __init__(self, database):
        multiprocessing.Process.__init__(self)
        DatabaseWrapper.__init__(self, database)
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

    '''
    get_patient_files assumes that the only files in save folders
    for gps, step count, and room location data are from the current
    instance of main.py being run. It takes advantage of predictable file
    naming to pull all files for the passed in patient_id.
    If there is more than one file for gps, step, or room data an error message
    results and those files are not touched.
    '''
    @staticmethod
    def get_patient_files(patient_id):
        file_list = []
        current_dir = os.getcwd()

        gps_dir = os.path.join(current_dir, 'gpsSaves')
        step_dir = os.path.join(current_dir, 'stepSaves')
        room_dir = os.path.join(current_dir, 'roomSaves')

        gps_file  = [fg for fg in os.listdir(gps_dir) if fg.split('_')[0] == patient_id]
        step_file = [fs for fs in os.listdir(step_dir) if fs.split('_')[0] == patient_id]
        room_file = [fr for fr in os.listdir(room_dir) if fr.split('_')[0] == patient_id]

        start_error = '************Email Error*************\n\n' \
                         'multiple files for %s in ' % patient_id
        end_error = '\nfiles will not be emailed nor deleted\n' \
                    '\n****************************************'

        if len(gps_file) == 1:
            file_list += [gps_dir + '/' + gps_file[0]]
        elif len(gps_file) > 1:
            print start_error + 'gps' + end_error

        if len(step_file) == 1:
            file_list += [step_dir + '/' + step_file[0]]
        elif len(step_file) > 1:
            print start_error + 'step count' + end_error

        if len(room_file) == 1:
            file_list += [room_dir + '/' + room_file]
        elif len(room_file) > 1:
            print start_error + 'room location' + end_error

        return file_list

    '''
    email_beta_data has a hardcoded dictionary for dce to email
    as well as dce to name. The method takes in a list of file paths
    eg [['C:/stepSaves/2772_2016-06-01_Wednesday_StepCount.png'] ['C:/gpsSaves/2772_2016-06-01_Wednesday_GPSData.kml']]
    predictable file names are used to retrieve the dce from the file path
    an email is then sent with survey links to each beta tester with data
    if the dce doesn't have an email in the dictionary, the data is not processed
    '''
    @staticmethod
    def email_beta_data(file_path_list, patient_id):
        email_dict = {'2747': 'kschenk@randolphcollege.edu',
                      '2749': 'savannah.carroll@ucsf.edu',
                      '2750': 'Reilly.Walker@ucsf.edu',
                      '2751': 'tamara.braley@unmc.edu',
                      '2762': 'Michael.Schaffer@ucsf.edu',
                      '2769': 'afella@randolphcollege.edu',
                      '2770': 'sbonasera@unmc.edu',
                      '2771': 'ssdill@randolphcollege.edu',
                      '2772': 'erhuber@randolphcollege.edu',
                      '2773': 'segrissom@randolphcollege.edu',
                      '2774': 'amhart@randolphcollege.edu',
                      '2775': 'stucker@randolphcollege.edu',
                      '2776': 'gishen@uchicago.edu',
                      '2777': 'Kasia.Gawlas@ucsf.edu',
                      '2780': 'denise.kreski@unmc.edu',
                      '2781': 'paige.scholer@unmc.edu',
                      '2782': 'ifortune@unmc.edu',
                      'george.netscher': 'gnetscher@gmail.com',
                      'sarah.dulaney': 'Sarah.Dulaney@ucsf.edu',
                      'julien.jacquemot': 'julien.jacquemot@gmail.com'
                      }

        dce_dict = {'2747': 'Katrin Schenk',
                    '2749': 'Savannah',
                    '2750': 'Reilly',
                    '2751': 'Tami',
                    '2762': 'Michael Schaffer',
                    '2769': 'Alex Fella',
                    '2770': 'Steve',
                    '2771': 'Sophia',
                    '2772': 'Eric',
                    '2773': 'Sarah',
                    '2774': 'Allison',
                    '2775': 'Sonja',
                    '2776': 'Galen',
                    '2777': 'Kasia',
                    '2779': 'Test 5',
                    '2780': 'Denise',
                    '2781': 'Paige',
                    '2782': 'Ileana',
                    'george.netscher': 'George',
                    'sarah.dulaney': 'Sarah',
                    'julien.jacquemot': 'Julien'}

        survey_dict = {'GPS': 'https://www.surveymonkey.com/r/BetaTestAccuracyReport',
                       'StepCount': 'https://www.surveymonkey.com/r/StepCountAccuracyReview',
                       'RoomLocation': 'No link available'}

        host_email = 'CMSFM2016@gmail.com'

        previous_dce = patient_id
        if previous_dce not in email_dict:
            print 'no email on file for %s' % previous_dce
            return []

        # make sure data is being passed in
        if file_path_list != []:
            # make sure all files attached are supposed to go to the same person
            previous_dce = os.path.basename(file_path_list[0].split('_', 1)[0])
            if previous_dce not in email_dict:
                print 'no email on file for %s' % previous_dce
                return []

            for f in range(len(file_path_list)):
                current_dce = os.path.basename(file_path_list[f].split('_', 1)[0])
                if email_dict[current_dce] != email_dict[previous_dce]:
                    print 'email attachment or directory mismatch: %s != %s' % (previous_dce, current_dce)
                    return []
                previous_dce = current_dce

        hack_add = email_dict[previous_dce].split('@')[-1]
        if hack_add == 'randolphcollege.edu' or hack_add == 'uchicago.edu':
            hack_add = 'randolph'
        if hack_add == 'ucsf.edu' or hack_add == 'gmail.com':
            hack_add = 'ucsf'
        if hack_add == 'unmc.edu':
            hack_add = 'unmc'

        if not hack_add == 'ucsf':
            for kill_file in range(len(file_path_list)):
                os.remove(file_path_list[kill_file])
            return []

        recipient = email_dict[previous_dce]
        #recipient = 'afella@randolphcollege.edu'
        yesterday = datetime.now() - timedelta(days=1)
        yesterday = yesterday.date()

        # get the types of files that are included
        file_types = [os.path.basename(file_path_list[f].split('_')[-1]) for f in range(len(file_path_list))]

        msg = MIMEMultipart()
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(host_email, 'Django1138')

        from_email = host_email
        msg['Subject'] = '%s FM Beta Data Verification for %s' % (dce_dict[previous_dce], str(yesterday))
        msg['From'] = from_email
        msg['To'] = recipient

        body = MIMEMultipart('alternative')
        if len(file_types) > 0:
            body_base = 'Please fill out the following surveys for the corresponding attached data:\n\n'
        else:
            body_base = 'Please fill out the following surveys for %s:\n\n' % yesterday

        if any(t == 'GPSData.kml' for t in file_types):
            gps_request = 'GPS: %s\n' % survey_dict['GPS']
        else:
            gps_request = 'We have no GPS data for you\nGPS: %s\n' % survey_dict['GPS']

        if any(t == 'StepCount.png' for t in file_types):
            step_request = 'Step Count: %s\n' % survey_dict['StepCount']
        else:
            step_request = 'We have no Step Count data for you\nStep Count: %s\n' % survey_dict['StepCount']

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

        to_email = [recipient]
        to_email += ['afella@randolphcollege.edu']
        s.sendmail(from_email, to_email, msg.as_string())

        #for kill_file in range(len(file_path_list)):
        #    os.remove(file_path_list[kill_file])

    '''
    launch_beta_evals creates an instance of each data analysis class
    for a given patient_id (dce) and runs them each
    the process data method in each class ought to return a file path
    but it isn't used since I gave up on figuring out how to get these
    to actually return the file path (multiprocessing is not something I know about)
    '''
    def launch_beta_evals(self, patient_id):
        betaGPStest = Gps(self.database, patient_id)
        betaGPStest.start()
        betaGPStest.join()

        betaStepstest = StepCount(self.database, patient_id)
        betaStepstest.start()
        betaStepstest.join()

        betaRoomtest = RoomLocation(self.database, patient_id)
        betaRoomtest.start()
        betaRoomtest.join()

    '''
    calls each function in appropriate order to process all data for the day
    '''
    def run(self):
        patient_ids = self.get_patients_list()
        for patient_id in patient_ids:
            self.launch_beta_evals(patient_id)
            file_list = self.get_patient_files(patient_id)
            self.email_beta_data(file_list, patient_id)
