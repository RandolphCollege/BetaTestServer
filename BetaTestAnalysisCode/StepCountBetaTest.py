from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib.pyplot as plt


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

        # define figure, set bin size, et cetera
        bin_width = 60000
        plt.figure()
        plt.axis([0, max(data[:, 0]), 0, max(data[:, 1])])
        plt.hist(data, bins=np.arange(min(data[:, 0]), max(data[:, 0]) + bin_width, bin_width))

        # Set labels on the graph
        plt.title('Step Count by Minute for %s' % self.patientID)
        plt.xlabel('time')
        plt.ylabel('steps')
