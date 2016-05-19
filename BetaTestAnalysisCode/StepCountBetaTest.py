from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib.pyplot as plt
import calendar
import datetime as dt


class StepCount(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'StepCountbeta', 'dataHMDSC')
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
        fig = plt.figure(1)
        bin_width = 900000
        # Set time axis label
        labels = [str(i) for i in range(24)]
        values = [86400000 * t / 24 for t in range(24)]

        # AM Plot
        ax1 = fig.add_subplot(211)
        ax1.hist(data_in, bins=np.arange(0, 43200000, bin_width))
        ax1.xticks(values[:12], labels[:12])
        ax1.xlim([0, 43200000])

        # PM Plot
        ax2 = fig.add_subplot(212)
        ax2.hist(data_in, bins=np.arange(43200000, 86400000, bin_width))
        ax2.xticks(values[12:], labels[12:])
        ax2.xlim([43200000, 86400000])

        # Set labels on the graph
        plot_title ='%s\'s steps on %s, %s' % (self.patientID, str(data_day), str(start_date))
        ax1.title(plot_title)
        fig.text(0.5, 0.04, 'Time', ha='center', va='center)')
        fig.text(0.06, 0.5, 'Steps', ha='center', va='center', rotation='vertical')

        # Save and close figure and return save location
        plt.savefig(file_path)
        plt.close(fig)
        return file_path
