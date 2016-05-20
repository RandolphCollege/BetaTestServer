import multiprocessing
from DatabaseManagementCode.databaseWrapper import DatabaseWrapper
from datetime import datetime, timedelta
import abc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import utc
from FileManagementCode.signalHandler import SignalHandler
import signal
import time

class BetaTestInterface(multiprocessing.Process, DatabaseWrapper):

    def __init__(self, database, patient_id, analysis_name, table_name):
        '''
        Interface for running any beta test analysis code
        :param database: tuple containing (host, username, password) for connecting to database
        :param patient_id: The DCE-ID of the patient being processed
        :param analysis_name: The type of analysis being done
        :param table_name: The table to fetch from database for analysis
        :return:
        '''
        multiprocessing.Process.__init__(self)
        DatabaseWrapper.__init__(self, database)

        self.database_name = '_' + patient_id
        self.analysis_name = analysis_name
        self.table_name    = table_name
        executors = {
            'default': ThreadPoolExecutor(20),
        }

        self.scheduler = BackgroundScheduler(executors=executors,
                                             timezone=utc)


        if not self.table_exists(self.database_name, 'BetaTestProfile'):
            self.create_table(database_name = self.database_name,
                              table_name    = 'BetaTestProfile',
                              column_names  = ['table_name', 'analysis_name', 'timestamp'],
                              column_types  = ['VARCHAR(100)', 'VARCHAR(100) NOT NULL PRIMARY KEY', 'BIGINT(20)'])

    @staticmethod
    def datetime_to_utc(timestamp):
        """ Converts the given timestamp to UTC in ms. """

        epoch      = datetime.utcfromtimestamp(0)
        delta      = timestamp-epoch

        return long(delta.total_seconds() * 1000)

    @staticmethod
    def utc_to_datetime(utc):
        seconds = float(utc)/float(1000)
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
        return [self.datetime_to_utc(datetime(year  = timestamp.year,
                                              month = timestamp.month,
                                              day   = timestamp.day,
                                              hour  = 0)),
                self.datetime_to_utc(datetime(year  = timestamp.year,
                                              month = timestamp.month,
                                              day   = timestamp.day,
                                              hour  = 0) + timedelta(days=1))]

    def write_timestamp(self, timestamp):
        """
        Write the latest timestamp, in this case it means the end of a window
        :param timestamp:
        :return:
        """
        return self.insert_into_database(database_name       = self.database_name,
                                         table_name          = 'analysisprofile',
                                         column_names        = ['table_name', 'type_name', 'timestamp'],
                                         values              = [self.table_name, self.analysis_name, timestamp],
                                         on_duplicate_update = [ 2 ])

    def get_latest_data_stamp(self):
        if not self.fetch_from_database(database_name = self.database_name,
                                        table_name    = self.table_name,
                                        to_fetch      = 'timestamp',
                                        order_by      = ['timestamp', 'DESC'],
                                        limit         = 1):
            return []
        else:
            latest_data = self.fetchall()

        if len(latest_data) == 0:
            return []
        else:
            return zip(*list(zip(*latest_data)))[0][0]


    def get_latest_stamp_window(self):
        latest_time = datetime.now()
        latest_time = self.datetime_to_utc(latest_time)
        return self.get_stamp_window_from_utc(latest_time)

    def get_yesterday_window(self):
        """
        Create a list of timestamp windows -24 from the latest window to insure all data has arrived.

        :return:
        """
        ms_per_metric_window = 86400000*3
        late_window  = self.get_latest_stamp_window()
        return [late_window[0] - ms_per_metric_window, late_window[1] - ms_per_metric_window]

    @abc.abstractmethod
    def process_data(self, data):
        """
        Do the analysis on the data
        :param windowed_data:
        :return:
        """
        return

    def get_analysis_data(self, start_stamp, end_stamp):
        """
        @param data_type: str of the column selected, pass * for all data in table
        @param table_name: str of the name of the table
        @return: data
        """

        if not self.table_exists(self.database_name, self.table_name):
            return []

        if not self.fetch_from_database(database_name = self.database_name,
                                        table_name    = self.table_name,
                                        where         = [['timestamp', '>=', start_stamp],
                                                         ['timestamp', '<', end_stamp]],
                                        order_by      = ['timestamp', 'ASC']):
            return []
        else:
            analysis_data = self.fetchall()

        if len(analysis_data) == 0:
            return []
        else:
            return zip(*list(zip(*analysis_data)))

    def scheduled_job(self):
        window = self.get_yesterday_window()
        data = self.get_analysis_data(window[0], window[1])
        if data:
            processed_data = self.process_data(data)

    def run(self):
        self.scheduled_job()
