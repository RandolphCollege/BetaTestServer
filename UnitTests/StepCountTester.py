import unittest
import numpy as np
import random
from BetaTestAnalysisCode.StepCountBetaTest import StepCount

class StepCountTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "")
        times = [1462220567000, 1462220477000, 1462186956000, 1462186851000, 1462179425000, 1462179154000,
                 1462179064000, 1462178974000, 1462178883000, 1462178790000, 1462178707000, 1462148105000,
                 1462147988000, 1462146348000, 1462146256000, 1462146167000, 1462146071000, 1462144625000,
                 1462144531000, 1462144260000, 1462143989000, 1462143718000]
        count_list = []
        for i in range(len(times)):
            count_list.append(random.randrange(20, 30))
        counts = np.array(count_list)
        self.data = np.column_stack((times, counts))

    def testStepCount(self):
        stepcountClass = StepCount(self.database, 'george.netscher')
        stepcountClass.start()
        stepcountClass.join()

if __name__ == '__main__':
    runner = unittest.main()
