from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
import json

class DataLearn(DatabaseWrapper):
    def __init__(self):
        host = "localhost"
        user = "brad"
        password = "moxie100"
        database = (host, user, password)

        DatabaseWrapper.__init__(self, database=database)

    def get_analysis_data(self, start_stamp, end_stamp):
        """
        @param data_type: str of the column selected, pass * for all data in table
        @param table_name: str of the name of the table
        @return: data
        """

        if not self.table_exists(self.database_name, self.table_name):
            return []

        if not self.fetch_from_database(database_name=self.database_name,
                                        table_name=self.table_name,
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

    def get_tables(self, database):
        all_tables = self.tables_list(database)
        table_list = [s for s in all_tables if s == "AnalysisRoomLocation" or s[:4] == 'data']
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

    def write_one_day(self, write_path, start_stamp, end_stamp):
        f = open(write_path, 'w')

        database_list = self.get_database_names
        for db in range(len(database_list)):
            f.write('Next_Database\n')
            f.write(database_list[db])
            f.write('\n')

            table_list = self.get_tables(database_list[db])
            for tbl in range(len(table_list)):
                f.write(table_list[tbl])

                column_titles = self.table_columns(database_list[db], table_list[tbl])
                column_types = [type(t) for t in column_titles]
                data = self.get_analysis_data(start_stamp, end_stamp)

                json_column_titles = json.dumps(column_titles)
                json_types = json.dumps(column_types)
                json_table = json.dumps(data)

                f.write(json_column_titles)
                f.write(json_types)
                f.write(json_table)
                f.write('\n')

    def read_one_day(self, file_path):
        f = open(file_path, 'r')
        new_database = False
        new_table = False
        for line in f:
            if line == 'New_Database\n':
                new_database = True
                new_table = False
                continue

            elif line == '\n':
                new_table = True
                continue

            else:
                if new_database:
                    current_database = line
                    new_table = True
                    new_database = False
                    if not self.database_exists(line):
                        self.create_database(line)
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
                    if not self.table_exists(current_database, line):
                        self.create_table(current_database, current_table, current_columns, json.loads(line))

                elif fill_table == 3:
                    fill_table = 0
                    self.insert_into_database(current_database, current_table, current_columns, json.loads(line))
