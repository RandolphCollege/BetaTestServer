import unittest
import numpy
from BetaTestAnalysisCode.GPSBetaTest import Gps

class gpsTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "moxie100")
        self.data = numpy.array()

    def testGPS(self):
        gpsClass = Gps(self.database, '_foo')
        gpsClass.process_data(self.data)