from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib.pyplot as plt
import calendar


class StepCount(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'GPSbeta', 'dataMMGPS')
        self.patientID = patientID

    '''
    #Expected input data as numpy array 3 columns
    #column 1 as time stamp of data
    #column 2 as number of steps between current and last timestamp
    #code creates bin histogram of steps with 1 minute time windows
    '''

    def process_data(self, data):
        # turn ingeractive off so that the figure is not automatically displayed
        plt.ioff()

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(data.item(0, 0))[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date
        data_day = calendar.day_name[start_datetime.weekday()]

        # set file name and save folder path
        file_name = "%s %s %s StepCount.png" % (self.patientID, data_day, data_date)
        file_path = "'C:\Users\Eric\Documents\Summer Research 2016\GPS Data\Eric Huber\\test\\%s" % file_name

        # set up figure
        fig = plt.figure()
        delta_utc = self.datetime_to_utc(start_date)
        data_in = []
        for i in range(len(data)):
            data_in += data.item(i, 0) * [data.item(i, 1) - delta_utc]

        # set bin width and file name/save location
        bin_width = 60000
        plt.hist(data_in, bins=np.arange(0, 86400000 + bin_width, bin_width))

        # Set labels on the graph
        plt.title('%s\'s steps on %s %s' % (self.patientID, data_day, data_date))
        plt.xlabel('time')
        plt.ylabel('steps')

        # Save and close figure and return save location
        plt.savefig(file_path)
        plt.close(fig)
        return file_path

