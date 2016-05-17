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

        # set bin width and file name/save location
        bin_width = 60000
        t_naught = data.item(0, 0)
        data_date = t_naught.date()
        data_day = calendar.day_name[t_naught.weekday()]
        file_name = "%s %s %s StepCount.png" % (self.patientID, data_day, data_date)
        file_path = "'C:\Users\Eric\Documents\Summer Research 2016\GPS Data\Eric Huber\\test\\%s" % file_name

        # define figure, set bin size, et cetera
        fig = plt.figure()
        plt.axis([0, max(data[:, 0]), 0, max(data[:, 1])])
        plt.hist(data, bins=np.arange(min(data[:, 0]), max(data[:, 0]) + bin_width, bin_width))

        # Set labels on the graph
        plt.title('Step Count by Minute for %s' % self.patientID)
        plt.xlabel('time')
        plt.ylabel('steps')

        # Save and close figure and return save location
        plt.savefig(file_path)
        plt.close(fig)
        return file_path

