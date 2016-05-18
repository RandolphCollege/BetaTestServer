from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib.pyplot as plt
import calendar
import datetime as dt


class StepCount(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'StepCountbeta', 'dataMMGPS')
        self.patientID = patientID

    '''
    # Expected input data as numpy array 3 columns
    # column 1 as time stamp of data
    # column 2 as number of steps between current and last timestamp
    # code creates bin histogram of steps with 1 minute time windows
    # and returns the path of the save location
    '''

    def process_data(self, data):
        # turn interactive off so that the figure is not automatically displayed
        plt.ioff()

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(data.item(0, 1))[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date()
        data_day = calendar.day_name[start_datetime.weekday()]

        # set file name and save folder path
        file_name = "%s_%s_%s_StepCount.png" % (self.patientID, data_day, start_date)
        folder_path = "C:\Users\Eric\Documents\Summer Research 2016\GPS Data\Eric Huber\\test\\"
        file_path = folder_path + file_name

        # create new array (data_in) to copy timestamps for each step in that timestamp's pull
        delta_utc = self.datetime_to_utc(start_datetime)
        data_in = []
        for i in range(len(data)):
            data_in += data.item(i, 0) * [data.item(i, 1) - delta_utc]

        # set up figure, set bin width and plot the histogram
        fig = plt.figure()
        bin_width = 60000
        plt.hist(data_in, bins=np.arange(0, 86400000, bin_width))

        # Set labels on the graph
        plot_title ='%s\'s steps on %s, %s' % (self.patientID, str(data_day), str(start_date))
        plt.title(plot_title)
        plt.xlabel('time')
        plt.ylabel('steps')

        # Set time axis label
        labels = [str(i) for i in range(24)]
        values = [86400000 * t / 24 for t in range(24)]
        plt.xticks(values, labels)
        plt.xlim([0, 86400000])

        # Save and close figure and return save location
        plt.savefig(file_path)
        plt.close(fig)
        return file_path
