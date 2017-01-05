from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import calendar
import datetime
import math
from collections import Counter
import os
import csv


class StepCount(BetaTestInterface):
    def __init__(self, database, patientID, day):
        BetaTestInterface.__init__(self, database, patientID, 'StepCountbeta', 'dataHMDSC', day)
        self.patientID = patientID

    '''
    # Expected input data as array of tuples
    # column 1 as time stamp of data
    # column 2 as number of steps between current and last timestamp
    # code creates bin histogram of steps with 1 minute time windows
    # and returns the path of the save location
    # skips duplicate entries
    '''

    def process_data(self, data):
        # turn interactive off so that the figure is not automatically displayed
        plt.ioff()

        # if the time data is not utc, make it so
        time, steps = zip(*data)
        if not isinstance(time[0], long):
            new_time = [self.sql_datetime_to_utc(t) - self.fuck_up_hack for t in time]
        else:
            new_time = [t - self.fuck_up_hack for t in time]

        '''
        #Use this if there is a day with both utc timestamps and new timestamps. It's stupid slow but will work
        new_time = []
        for t in time:
            if not isinstance(t, long):
                new_time += [self.sql_datetime_to_utc(t) - self.fuck_up_hack]
            else:
                new_time += [t - self.fuck_up_hack]
        '''
        data = zip(new_time, steps)

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(data[0][0])[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date()
        data_day = calendar.day_name[start_datetime.weekday()]

        # set file name and save folder path
        file_name = "%s_%s_%s_StepCount.png" % (self.patientID, start_date, data_day)
        current_dir = os.getcwd()
        save_file_path = 'stepSaves'
        step_save_path = os.path.join(current_dir, save_file_path)
        if not os.path.exists(step_save_path):
            os.makedirs(step_save_path)
        file_path = os.path.join(step_save_path, file_name)

        # create new array (data_in) to copy timestamps for each step in that timestamp's pull
        delta_utc = self.datetime_to_utc(start_datetime)
        data_in = []
        previous_time = []
        previous_count = []
        step_total = 0
        duplicates_skipped = 0
        for i in range(len(data)):
            if data[i][0] != previous_time or data[i][1] != previous_count:
                data_in += data[i][1] * [data[i][0] - delta_utc]
                previous_time = data[i][0]
                previous_count = data[i][1]
                step_total += data[i][1]
            else:
                duplicates_skipped += 1

        dup_message = "********StepCountBetaTest********** \
        \n\nduplicate data point rejected \
        \n%s data points rejected\nPatient: %s\nDate: %s \
        \n\n***********************************" % (duplicates_skipped, self.patientID, start_date)

        if duplicates_skipped > 0:
            print dup_message

        # set up figure, set bin width and plot the histogram
        plt.ioff()
        fig = plt.figure()
        bin_width = 900000
        if not 86400000 % bin_width == 0:
            error_message = "The day must be split into even and complete bins"
            print "****************StepCountError*******************\n\n %s\n\n " \
                  "*************************************************" % error_message

        # Set time axis label
        labels = [str(i) for i in range(24)]
        values = [86400000 * t / 24 for t in range(24)]

        # plot empties
        bin_borders = [bin_width*b for b in range(86400000/bin_width+1)]
        time_list, step_list = zip(*data)
        null_data = []
        counts = Counter(data_in)
        top_count = counts.most_common(1)
        if not top_count == []:
            top_tuple = top_count[0]
            ymax = top_tuple[1]
        else:
            ymax = 10
        for n in range(1, len(bin_borders)):
            if not any(bin_borders[n - 1] <= i - delta_utc < bin_borders[n] for i in time_list):
                null_data += [bin_borders[n-1] + 450000] * int(math.ceil(ymax/50.))

        # AM Plot
        ax1 = fig.add_subplot(211)
        n_am, bin_am, hist = ax1.hist(data_in, facecolor='blue', bins=np.arange(0, 43200000 + bin_width, bin_width))

        null_am, null_bin_am, hust = ax1.hist(null_data, facecolor='red', bins=np.arange(0, 43200000 + bin_width, bin_width))
        ax1.set_xticks(values)
        ax1.set_xticklabels(labels)
        ax1.set_xlim([0, 43200000])

        # PM Plot
        ax2 = fig.add_subplot(2, 1, 2, sharey=ax1)
        n_pm, bin_pm, hist = ax2.hist(data_in, facecolor='blue', bins=np.arange(43200000, 86400000 + bin_width, bin_width))
        null_pm, null_bin_pm, hist = ax2.hist(null_data, facecolor='red', bins=np.arange(43200000, 86400000 + bin_width, bin_width))
        ax2.set_xticks(values[12:])
        ax2.set_xticklabels(labels[12:])
        ax2.set_xlim([43200000, 86400000])

        # adjust y axis if there are few steps for the day
        if ymax < 50:
            ax1.set_yticks(range(0, 60, 10))
            ax2.set_yticks(range(0, 60, 10))

        # Set labels on the graph
        plot_title ='total steps: %s\n%s\'s steps on %s, %s ' % (step_total, self.patientID, str(data_day), str(start_date))
        ax1.set_title(plot_title)
        ax2.set_xlabel('Time (each rectangle represents 15 minutes)', fontsize=18)
        fig.text(.028, .525, 'Steps', rotation='vertical', fontsize=18)

        # Save and close figure and return save location
        plt.savefig(file_path)
        plt.close()
        total_n = np.append(n_am, n_pm)
        null_n = np.append(null_am, null_pm)
        total_bin = np.append(bin_am, bin_pm)
        total_save_path = os.path.join(current_dir, 'totalSteps')
        filepath = os.path.join(total_save_path, "%s_%s_%s_StepCount.csv" % (self.patientID, start_date, data_day))
        with open(filepath, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['Bin Start Time', 'Steps', 'Valid'])
            for index, step in enumerate(total_n):
                start_time = (total_bin[index]/86400000.0)*24
                steps = step
                if steps != 0.:
                    valid = 1
                elif null_n[index] == 0:
                    valid = 1
                else:
                    valid = 0
                writer.writerow([start_time, int(steps), valid])



        return file_path
