import unittest
import numpy as np
import random
from BetaTestAnalysisCode.RoomLocationBetaTest import RoomLocation

class RoomLocationTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "moxie100")
        times = [1462220567000, 1462179425000, 1462179064000, 1462178974000, 1462178707000, 1462147988000]
        room_list = ['family', 'living', 'bedroom', 'bathroom', 'utility']
        locations = []
        for i in range(len(times)):
            locations += [str(room_list[random.randrange(0, len(room_list))])]

        self.data = np.column_stack((times, locations))

    def testRoomLocation(self):
        roomlocationClass = RoomLocation(self.database, 'foo')
        roomlocationClass.process_data(self.data)

if __name__ == '__main__':
    runner = unittest.main()
