from BetaTestInterface import BetaTestInterface
import numpy
import simplekml
import calendar
import os


class Gps(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'GPSbeta', 'dataMMGPS')
        self.patientID = patientID
    '''
    # Expected array of tuples as data with utc timestamps in the first column,
    # latitude in the second, and longitude in the third. All data is expected to
    # be from the same day. Each data point in sent to a kml file labeled with the 24
    # hour time taken from the timestamp. The file path of the saved KML is returned
    # skips duplicate entries
    '''

    def process_data(self, data):
        # simplekml module allows for easy conversion of data to kml file type
        kml = simplekml.Kml()

        time, lat, lon = zip(*data)
        new_time = [t - self.fuck_up_hack for t in time]
        data = zip(new_time, lat, lon)

        previous_datetime = []
        duplicates_skipped = 0
        # looping through the entirety of the input data...
        for i in range(len(data)):
            # convert to datetime
            current_datetime = self.utc_to_datetime(data[i][0])
            # if there is anything novel about this datapoint
            if current_datetime != previous_datetime or data[i][1] != previous_lat or data[i][2] != previous_lon:
                # add point to the kml labeled with the 24 hour time and coordinates
                pnt = kml.newpoint(name=current_datetime.time().strftime("%H:%M:%S"),
                                   description="Latitude: %s\nLongitude: %s" % (data[i][1], data[i][2]),
                                   coords=[(data[i][2], data[i][1])])
                previous_datetime = current_datetime
                previous_lat = data[i][1]
                previous_lon = data[i][2]
            # otherwise it was a duplicate
            else:
                duplicates_skipped += 1

        # error message to display if there are duplicate data points
        dup_message = "***********GPSBetaTest************* \
        \n\nduplicate data points rejected \
        \n%s data points rejected\nPatient: %s\nDate: %s \
        \n\n**************************************" % (duplicates_skipped, self.patientID, previous_datetime.date())

        # if there were any duplicates, print the error message
        if duplicates_skipped > 0:
            print dup_message

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(data[0][0])[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date()
        data_day = calendar.day_name[start_datetime.weekday()]

        # set the file path and save name
        file_name = "%s_%s_%s_GPSData.kml" % (str(self.patientID), str(start_date), str(data_day))
        current_dir = os.getcwd()
        save_file_path = 'gpsSaves'
        gps_save_path = os.path.join(current_dir, save_file_path)
        if not os.path.exists(gps_save_path):
            os.makedirs(gps_save_path)
        file_path = os.path.join(gps_save_path, file_name)
        # save the kml file and return the location
        kml.save(file_path)
        return file_path
