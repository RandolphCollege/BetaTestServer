from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
import json
from datetime import datetime, timedelta
import os


'''
this class is used to pull data from one database and write it to a file
or pull a file that's been written with this class and push the data
into the current database. File is assumed to be in the current working directory
'''
class DataLearn(DatabaseWrapper):
    def __init__(self):
        host = "localhost"
        user = "root"
        password = "moxie100"
        database = (host, user, password)

        DatabaseWrapper.__init__(self, database=database)

    def get_analysis_data(self, database_name, table_name, start_stamp, end_stamp):
        """
        @param database_name: str of the database selected in form "_1234"
        @param table_name: str of the name of the table
        @param start_stamp: utc timestamp of beginning of data to be retrieved (included)
        @param end_stamp: utc timestamp of end of data to be retrieved (excluded)
        @return: data
        """

        if not self.table_exists(database_name, table_name):
            return []

        if not self.fetch_from_database(database_name=database_name,
                                        table_name=table_name,
                                        where=[['timestamp', '>=', start_stamp],
                                               ['timestamp', '<', end_stamp]],
                                        order_by=['timestamp', 'ASC']):
            return []
        else:
            analysis_data = self.fetchall()

        if len(analysis_data) == 0:
            return []
        else:
            return zip(*list(zip(*analysis_data)))

    def get_room_analysis_data(self, database_name, table_name, start_stamp):
        """
        @param database_name: str of the database selected in form "_1234"
        @param table_name: str of the name of the table
        @param start_stamp: utc timestamp of beginning of data to be retrieved (included)
        @return: data
        """

        if not self.table_exists(database_name, table_name):
            return []

        if table_name == 'AnalysisRoomLocation':
            if not self.fetch_from_database(database_name=database_name,
                                            table_name=table_name,
                                            where=['start_window', '>=', start_stamp],
                                            order_by=['start_window', 'ASC']):
                return []
            else:
                analysis_data = self.fetchall()
        elif table_name == 'profile':
            if not self.fetch_from_database(database_name=database_name,
                                            table_name=table_name):
                return []
            else:
                analysis_data = self.fetchall()

        if len(analysis_data) == 0:
            return []
        else:
            return zip(*list(zip(*analysis_data)))

    @staticmethod
    def datetime_to_utc(timestamp):
        """ Converts the given timestamp to UTC in ms. """

        epoch = datetime.utcfromtimestamp(0)
        delta = timestamp - epoch

        return long(delta.total_seconds() * 1000)

    @staticmethod
    def utc_to_datetime(utc):
        seconds = float(utc) / float(1000)
        date = datetime.utcfromtimestamp(seconds)
        return date

    def get_stamp_window_from_utc(self, timestamp):
        """
        Gets the earliest window in utc numerical time
        Windows are as follow:
        Midnight <= time < Noon
        Noon <= time < Next Day Midnight
        :param timestamp: timestamp in numerical utc time
        :return: 2 element list of [start_window, end_window]
        """
        timestamp = self.utc_to_datetime(timestamp)
        return [self.datetime_to_utc(datetime(year=timestamp.year,
                                              month=timestamp.month,
                                              day=timestamp.day,
                                              hour=0)),
                self.datetime_to_utc(datetime(year=timestamp.year,
                                              month=timestamp.month,
                                              day=timestamp.day,
                                              hour=0) + timedelta(days=1))]

    def get_tables(self, database):
        all_tables = self.tables_list('_' + database)
        table_list = [s for s in all_tables if s == "AnalysisRoomLocation" or s == 'profile' or
                      s[:4] == 'data' and s.split('.')[0][-3:] != 'LOG']
        return table_list

    def get_database_names(self):
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
    writes one days worth of data from the given datetime into a txt file
    in a format which can be read by the read_one_day method
    '''
    def write_one_day(self, time_stamp, file_name):
        utc_time = self.datetime_to_utc(time_stamp)
        start_stamp = self.get_stamp_window_from_utc(utc_time)[0]
        end_stamp = self.get_stamp_window_from_utc(utc_time)[1]

        current_dir = os.getcwd()
        save_file_path = 'databaseSaves'
        database_save_path = os.path.join(current_dir, save_file_path)

        if not os.path.exists(database_save_path):
            os.makedirs(database_save_path)
        file_path = os.path.join(database_save_path, file_name)
        f = open(file_path, 'w')

        database_list = self.get_database_names()
        for db in range(len(database_list)):
            # Next_Database indicates a new dce always then a new table
            # Next_Table indicates a new table on the next line unless Next_Database
            '''
            Example:
            Next_Database
            _2772
            dataHMDSC
            column titles (json)
            column types (json)
            data (json)
            Next_Table
            dataMMGPS
            '''
            f.write('Next_Database\n')
            f.write(database_list[db])
            f.write('\n')

            current_database = '_' + database_list[db]
            table_list = self.get_tables(database_list[db])
            for tbl in range(len(table_list)):
                f.write(table_list[tbl])
                f.write('\n')

                column_titles = self.table_columns(current_database, table_list[tbl])
                column_types = self.table_column_types(current_database, table_list[tbl])
                if table_list[tbl] != 'AnalysisRoomLocation' and table_list[tbl] != 'profile':
                    data = self.get_analysis_data(current_database, table_list[tbl], start_stamp, end_stamp)
                else:
                    data = self.get_room_analysis_data(current_database, table_list[tbl], start_stamp)

                json_column_titles = json.dumps(column_titles)
                json_types = json.dumps(column_types)
                json_table = json.dumps(data)

                f.write(json_column_titles)
                f.write('\n')
                f.write(json_types)
                f.write('\n')
                f.write(json_table)
                f.write('\nNext_Table\n')
        f.close()

    '''
    reads files written by above function and writes them into
    the current server database in mysql
    '''
    def read_one_day(self, file_path):
        f = open(file_path, 'r')
        new_database = False
        new_table = False
        fill_table = 0
        for line in f:
            if line == 'Next_Database\n':
                new_database = True
                new_table = False
                continue

            elif line == 'Next_Table\n':
                new_table = True
                continue

            elif line == '':
                break

            else:
                line = line.rstrip('\n')
                if new_database:
                    current_database = '_' + line
                    new_table = True
                    new_database = False
                    if not self.database_exists(current_database):
                        self.create_database(current_database)
                    continue

                if new_table:
                    fill_table = 1
                    current_table = line
                    new_table = False
                    continue

                if fill_table == 1:
                    fill_table += 1
                    current_columns = json.loads(line)
                    continue

                elif fill_table == 2:
                    fill_table += 1
                    current_column_types = json.loads(line)
                    if not self.table_exists(current_database, current_table):
                        self.create_table(current_database, current_table, current_columns, json.loads(line))

                elif fill_table == 3:
                    fill_table = 0
                    if json.loads(line) != []:
                        if len(current_columns) == len(self.table_columns(current_database, current_table)):
                            self.insert_into_database(current_database, current_table, current_columns, json.loads(line))
                        else:
                            self.drop_table(current_database, current_table)
                            self.create_table(current_database, current_table, current_columns, current_column_types)
                            self.insert_into_database(current_database, current_table, current_columns, json.loads(line))
        f.close()

data_grab = DataLearn()
current_dir = os.getcwd()
file_name = 'dataJune14'
file_path = os.path.join(current_dir, file_name)

data_grab.read_one_day(file_path)
#data_grab.write_one_day(datetime.now() - timedelta(days=1, hours=4), file_name)
