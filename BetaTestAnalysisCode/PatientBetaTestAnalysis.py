from GPSBetaTest import Gps
from StepCountBetaTest import StepCount
from RoomLocationBetaTest import RoomLocation
from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
import multiprocessing
import os
import smtplib
from datetime import datetime, timedelta


class PatientBetaTestAnalysis(DatabaseWrapper, multiprocessing.Process):

    def __init__(self, database, day=1):
        multiprocessing.Process.__init__(self)
        DatabaseWrapper.__init__(self, database)
        self.database = database
        self.day = day

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
            file_list += [room_dir + '/' + room_file[0]]
        elif len(room_file) > 1:
            print start_error + 'room location' + end_error

        return file_list

    @staticmethod
    def expunge_old_files():
        current_dir = os.getcwd()
        dir_list = []

        dir_list += [os.path.join(current_dir, 'gpsSaves')]
        dir_list += [os.path.join(current_dir, 'stepSaves')]
        dir_list += [os.path.join(current_dir, 'roomSaves')]

        for folder in dir_list:
            for delete_file in os.listdir(folder):
                file_path = os.path.join(folder, delete_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

    '''
    email_beta_data has a hardcoded dictionary for dce to email
    as well as dce to name. The method takes in a list of file paths
    eg [['C:/stepSaves/2772_2016-06-01_Wednesday_StepCount.png'] ['C:/gpsSaves/2772_2016-06-01_Wednesday_GPSData.kml']]
    predictable file names are used to retrieve the dce from the file path
    an email is then sent with survey links to each beta tester with data
    if the dce doesn't have an email in the dictionary, the data is not processed
    '''
    def record_beta_data(self, file_path_list, patient_id):
        dce_dict = {
            '3567': 'Patient 1',
            '1525': 'Patient 2',
            '2384': 'Patient 3',
            '2638': 'Patient 4',
            '2675': 'Patient 5',
            '2682': 'Patient 6',
            '2751': 'Randolph 1',
            '2769': 'Beta New',
            '2771': 'Randolph 2',
            '2774': 'Randolph 3',
            '2775': 'Randolph 4',
            '2776': 'Randolph 5',
            '4361': 'Patient 7',
            '4404': 'Patient 8',
            '4420': 'Patient 9',
            '4449': 'Patient 10',
            '4764': 'Patient 11',
            '4791': 'Patient 12',
            '4874': 'Patient 13',
            '5231': 'Patient 14',
            '5724': 'Patient 15',
            '5750': 'Patient 16',
            '5767': 'Patient 17',
            '5778': 'Patient 18'
            }



        previous_dce = patient_id

        # dUct-TAPe
        hack_add = previous_dce

        # Eliminate all files that don't go to the specified group without emailing
        #if hack_add == '3567':
        #    for kill_file in range(len(file_path_list)):
        #        os.remove(file_path_list[kill_file])
        #    return []


        # Define a date object to let the beta testers know what day the data is for
        yesterday = datetime.now() - timedelta(days=self.day, hours=4)
        yesterday = yesterday.date()

        # get the types of files that are included
        file_types = [os.path.basename(file_path_list[f].split('_')[-1]) for f in range(len(file_path_list))]




    '''
    launch_beta_evals creates an instance of each data analysis class
    for a given patient_id (dce) and runs them each
    the process data method in each class ought to return a file path
    but it isn't used since I gave up on figuring out how to get these
    to actually return the file path (multiprocessing is not something I know about)
    '''
    def launch_beta_evals(self, patient_id):

        betaGPStest = Gps(self.database, patient_id, self.day)
        betaGPStest.start()
        betaGPStest.join()

        betaStepstest = StepCount(self.database, patient_id, self.day)
        betaStepstest.start()
        betaStepstest.join()

        betaRoomtest = RoomLocation(self.database, patient_id, self.day)
        betaRoomtest.start()
        betaRoomtest.join()

    '''
    calls each function in appropriate order to process all data for the day
    '''
    def run(self):
        self.expunge_old_files()
        patient_ids = self.get_patients_list()
        for patient_id in patient_ids:
            self.launch_beta_evals(patient_id)
            file_list = self.get_patient_files(patient_id)
            self.record_beta_data(file_list, patient_id)
