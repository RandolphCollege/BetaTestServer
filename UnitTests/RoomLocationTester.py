import unittest
import numpy as np
import random
from BetaTestAnalysisCode.RoomLocationBetaTest import RoomLocation


class RoomLocationTester(unittest.TestCase):

    def setUp(self):
        # Write your init code here
        self.database = ("localhost", "root", "moxie100")
        times = [1462146167000, 1462143357000, 1462141001000, 1462139166000, 1462126467000,
                 1462123324000, 1462122094000, 1462120947000, 1462077707000, 1462092263000,
                 1462084847000, 1462105764000]
        times.sort()
        room_list = ['family', 'living', 'bedroom', 'bathroom', 'utility']
        locations = []
        for i in range(len(times)/2):
            locations += [str(room_list[random.randrange(0, len(room_list))])] * 2

        self.data = np.column_stack((times, locations))

    def testRoomLocation(self):
        roomlocationClass = RoomLocation(self.database, '2750')
        roomlocationClass.start()
        roomlocationClass.join()
    def testRoomGrab(self):
        roomlocationClass = RoomLocation(self.database, '2750')
        print roomlocationClass.get_room_list()
    def testDataGrab(self):
        roomlocationClass = RoomLocation(self.database, '2750')
        window = roomlocationClass.get_yesterday_window()
        data = roomlocationClass.get_analysis_data(window[0], window[1])
        print data

if __name__ == '__main__':
    runner = unittest.main()
