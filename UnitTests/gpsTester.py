import unittest
import numpy
from BetaTestAnalysisCode.GPSBetaTest import Gps

class gpsTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "")

    def testGPS(self):
        gpsClass = Gps(self.database, '2777')
        gpsClass.start()
        gpsClass.join()

if __name__ == '__main__':
    runner = unittest.main()
