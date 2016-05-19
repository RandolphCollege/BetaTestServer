from BetaTestInterface import BetaTestInterface
import numpy


class Gps(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'GPSbeta', 'dataMMGPS')
        self.patientID = patientID
    '''
    # Expected numpy array as data with utc timestamps in the first column,
    # latitude in the second, and longitude in the third. All data is expected to
    # be from the same day. Each data point in sent to a kml file labeled with the 24
    # hour time taken from the timestamp. The file path of the saved KML is returned
    '''

    def process_data(self, data):
        # simplekml module allows for easy conversion of data to kml filetype
        import simplekml
        import calendar

        kml = simplekml.Kml()

        # looping through the entirety of the input data...
        for i in range(len(data)):
            # convert to datetime
            current_datetime = self.utc_to_datetime(data.item(i, 0))
            # add point to the kml labeled with the 24 hour time and coordinates
            pnt = kml.newpoint(name=str(current_datetime.time()),
                               description="Latitude: %s\nLongitude: %s" % (data.item(i, 1), data.item(i, 2)),
                               coords=[(data.item(i, 2), data.item(i, 1))])

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(data.item(0, 0))[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date()
        data_day = calendar.day_name[start_datetime.weekday()]

        # set the file path and save name
        file_name = "%s_%s_%s_GPSData.kml" % (str(self.patientID), str(data_day), str(start_date))
        file_path = "C:\Users\Eric\Documents\Summer Research 2016\GPS Data\Eric Huber\\test\\%s" % file_name
        # save the kml file and return the location
        kml.save(file_path)
        return file_path
