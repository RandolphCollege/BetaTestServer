from DatabaseManagementCode.databaseWrapper import DatabaseWrapper


class DataLearn(DatabaseWrapper):
    def __init__(self):
        host = "localhost"
        user = "brad"
        password = "moxie100"
        database = (host, user, password)

        DatabaseWrapper.__init__(self,database=database)

    def data_grab(self):
        if not self.fetch_from_database(database_name='_foo',
                                        table_name='dataHMACC.bak.0',
                                        order_by=['timestamp', 'ASC']):

            return []
        else:
            analysis_data = self.fetchall()

        if len(analysis_data) == 0:
            return []
        else:
            return zip(*list(zip(*analysis_data)))

test = DataLearn()
data= test.data_grab()
print data[0][0]
