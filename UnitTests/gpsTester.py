import unittest
import numpy
from BetaTestAnalysisCode.GPSBetaTest import Gps

class gpsTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "moxie100")

    def testGPS(self):
        gpsClass = Gps(self.database, '3567')
        gpsClass.start()
        gpsClass.join()

if __name__ == '__main__':
    runner = unittest.main()
