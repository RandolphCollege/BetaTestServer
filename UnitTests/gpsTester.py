import unittest
import numpy
from BetaTestAnalysisCode.GPSBetaTest import Gps

class gpsTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "moxie100")
        self.data = numpy.array([[1462120856000, 37.4395, -79.1699],
                        [1462120766000, 37.4377, -79.1706],
                        [1462120675000, 37.4377, -79.1701],
                        [1462120585000, 37.4395, -79.1699],
                        [1462120224000, 37.4395, -79.1707]])

    def testGPS(self):
        gpsClass = Gps(self.database, '_foo')
        gpsClass.process_data(self.data)

if __name__ == '__main__':
    runner = unittest.main()
