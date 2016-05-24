from GPSBetaTest import Gps
from StepCountBetaTest import StepCount
from RoomLocationBetaTest import RoomLocation
from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
import multiprocessing



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

    def run(self):
        patient_ids = self.get_patients_list()
        for patient_id in patient_ids:
            self.launch_beta_evals(patient_id)


database = ("localhost", 'root', 'moxie100')
tester = RunBetaTestAnalysis(database)
tester.start()
tester.join()
