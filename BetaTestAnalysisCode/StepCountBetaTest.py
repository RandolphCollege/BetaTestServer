from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib.pyplot as plt
import calendar
import datetime as dt
import os


class StepCount(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'StepCountbeta', 'dataHMDSC')
        self.patientID = patientID

    '''
    # Expected input data as numpy array 2 columns
    # column 1 as time stamp of data
    # column 2 as number of steps between current and last timestamp
    # code creates bin histogram of steps with 1 minute time windows
    # and returns the path of the save location
    '''

    def process_data(self, data):
        # turn interactive off so that the figure is not automatically displayed
        plt.ioff()

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(data[0][1])[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date()
        data_day = calendar.day_name[start_datetime.weekday()]

        # set file name and save folder path
        file_name = "%s_%s_%s_StepCount.png" % (self.patientID, data_day, start_date)
        current_dir = os.getcwd()
        save_file_path = 'stepSaves'
        step_save_path = os.path.join(current_dir, save_file_path)
        if not os.path.exists(step_save_path):
            os.makedirs(step_save_path)
        file_path = os.path.join(step_save_path, file_name)

        # create new array (data_in) to copy timestamps for each step in that timestamp's pull
        delta_utc = self.datetime_to_utc(start_datetime)
        data_in = []
        for i in range(len(data)):
            data_in += data[i][1] * [data[i][0] - delta_utc]

        # set up figure, set bin width and plot the histogram
        fig = plt.figure(1)
        bin_width = 900000
        # Set time axis label
        labels = [str(i) for i in range(24)]
        values = [86400000 * t / 24 for t in range(24)]

        # AM Plot
        ax1 = fig.add_subplot(211)
        ax1.hist(data_in, bins=np.arange(0, 43200000, bin_width))
        ax1.set_xticks(values[:12])
        ax1.set_xticklabels(labels[:12])
        ax1.set_xlim([0, 43200000])

        # PM Plot
        ax2 = fig.add_subplot(2, 1, 2, sharey=ax1)
        ax2.hist(data_in, bins=np.arange(43200000, 86400000, bin_width))
        ax2.set_xticks(values[12:])
        ax2.set_xticklabels(labels[12:])
        ax2.set_xlim([43200000, 86400000])

        # Set labels on the graph
        plot_title ='%s\'s steps on %s, %s' % (self.patientID, str(data_day), str(start_date))
        ax1.set_title(plot_title)
        ax2.set_xlabel('Time', fontsize=18)
        fig.text(.028, .525, 'Steps', rotation='vertical', fontsize=18)

        # Save and close figure and return save location
        plt.savefig(file_path)
        plt.close()
        return file_path
