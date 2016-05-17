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
            # add point to the kml labeled with the 24 hour time
            kml.newpoint(name=current_datetime.date(), coords=[(data.item(i, 2), data.item(i, 1))])

        # use the first time in the input data to get the date and day of the week
        t_naught = data.item(0, 0)
        data_date = t_naught.date()
        data_day = calendar.day_name[t_naught.weekday()]
        # set the file path and save name
        file_name = "%s %s %s GPSData.kml" % (self.patientID, data_day, data_date)
        file_path = "C:\Users\Eric\Documents\Summer Research 2016\GPS Data\Eric Huber\\test\\%s" % file_name
        # save the kml file and return the location
        kml.save(file_path)
        return file_path
