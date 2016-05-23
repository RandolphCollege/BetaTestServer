from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib.pyplot as plt
import calendar
import datetime as dt
import os
import pickle


class RoomLocation(BetaTestInterface):
    def __init__(self, database, patientID):
        BetaTestInterface.__init__(self, database, patientID, 'RoomLocationBeta', 'AnalysisRoomLocation')
        self.patientID = patientID

    '''
    # Expected structured numpy array input as data. 2 columns.
    # First column as timestamp formatted as an integer or long
    # Second column as room location formatted as a string
    # Returns file save location of bar chart with location
    # on the y axis and time on the x axis
    '''
    def get_room_list(self):
        self.fetch_from_database(database_name =self.database_name,
                                 table_name    ='rooms',
                                 to_fetch      ='ROOM_NAME')
        data = self.fetchall()
        rooms = zip(*data)[0]
        rooms = list(rooms)
        rooms.append('Room Not Know')
        rooms.append('No Connection')
        return rooms

    def get_analysis_data(self, start_stamp, end_stamp):
        """
        Returns the data between the time frame specified
        :return:
        """

        if not self.fetch_from_database(database_name=self.database_name,
                                        table_name=self.table_name,
                                        to_fetch='analysis_data',
                                        where=['start_window', '=', start_stamp]):
            return []
        else:
            metric_data = self.fetchall()

        if len(metric_data) == 0:
            return []
        else:
            return np.array(pickle.loads(zip(*list(zip(*metric_data)))[0][0])[0])

    def filter_room_data(self, data):
        last_values_list = []
        prior_room = ''
        room_trans = 0
        #data = [row[1] for row in data]
        filtered_data = []
        for i in data:
            if i[1] != prior_room:
                if len(last_values_list) >= 10:
                    room_trans += 1
                    last_values_list = [i[1]]
                    prior_room = i[1]
                    filtered_data.append(i)
                else:
                    last_values_list = [i[1]]
                    prior_room = i[1]
                    filtered_data = filtered_data[:(len(filtered_data) - len(last_values_list)-1)]
            if i[1] == prior_room:
                last_values_list.append(i[1])
                filtered_data.append(i)
        return np.array(filtered_data)

    def process_data(self, data):
        #data = self.filter_room_data(data)
        #print data
        time_data = np.hsplit(data, 2)[0].tolist()
        time_data = map(lambda x: int(x[0]), time_data)
        room_data = np.hsplit(data, 2)[1]

        # turn interactive off so that the figure is not automatically displayed
        plt.ioff()

        # get the date information for this data
        start_utc = self.get_stamp_window_from_utc(time_data[0])[0]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date = start_datetime.date()
        data_day = calendar.day_name[start_datetime.weekday()]

        # get the list of rooms in the house
        room_list = self.get_room_list()

        # set file name and save folder path
        file_name = "%s_%s_%s_RoomLocation.png" % (self.patientID, start_date, data_day)
        current_dir = os.getcwd()
        save_file_path = 'roomSaves'
        gps_save_path = os.path.join(current_dir, save_file_path)
        if not os.path.exists(gps_save_path):
            os.makedirs(gps_save_path)
        file_path = os.path.join(gps_save_path, file_name)

        # set up variable for previously occupied room and lists to fill
        # with durations of room occupations and the corresponding rooms
        previous_room = 'No Connection'
        previous_time = start_utc
        room_durations = []
        room_locations = []

        # looping through the entire day's data...
        for i in range(len(data)):
            current_room = room_data[i]
            current_duration = time_data[i] - previous_time
            if current_room != previous_room and current_duration <= 60000:
                # if the room just changed,
                if previous_room == 'No Connection':
                    previous_room = current_room
                room_durations += [current_duration]
                room_locations.append(previous_room)
                previous_time = time_data[i]
                previous_room = current_room
            elif current_duration > 60000:
                room_durations += 60000
                room_locations.append(previous_room)
                room_durations += [current_duration - 60000]
                room_locations.append('No Connection')
                previous_time = time_data[i]
                previous_room = current_room

        # include end of day data missed by the for loop
        room_durations += [time_data[-1] - previous_time]
        room_locations.append(previous_room)

        # Don't hate me for being a hack...
        # Create lists for each time frame as full or empty
        null_dict = {}
        full_dict = {}

        # looping through each room location and duration pair...
        for n in range(len(room_locations)):
            # create two lists, one for the occupied room, and one for the empty rooms
            # The occupied (full) room list will have the duration in the index of the occupied room
            # and zeros for all other room indices.
            # The empty (null) room list will have the duration in the indices of all empty rooms
            # and a zero in the index of the occupied room
            room_index = room_list.index(room_locations[n])
            null_dict['null_%s' % n] = [room_durations[n]] * len(room_list)
            full_dict['full_%s' % n] = [0] * len(room_list)
            null_dict['null_%s' % n][room_index] = 0
            full_dict['full_%s' % n][room_index] = room_durations[n]

        ind = np.arange(len(room_list))
        bar_width = 2 / float(len(room_list))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # set axis labels and graph title
        ax.set_ylabel('Location')
        ax.set_xlabel('Time')
        plot_title = '%s\'s room location on %s, %s' % (self.patientID, str(data_day), str(start_date))
        ax.set_title(plot_title)

        # Set time axis labels
        labels = [str(i) for i in range(24)]
        values = [86400000 * t / 24 for t in range(24)]
        ax.set_xticks(values)
        ax.set_xticklabels(labels)
        ax.set_xlim([0, 86400000])

        # set location axis labels
        ax.set_yticks(ind)
        ax.set_yticklabels(room_list)
        auto_top = ax.get_ylim()[1]
        ax.set_ylim(-bar_width, auto_top + bar_width)

        # fix figure so that axis labels aren't cutoff
        plt.gcf().tight_layout()

        # set base of plot
        left_bound = np.zeros(len(room_list))
        left_bound += [time_data[0] - start_utc]
        ax.barh(ind, full_dict['full_0'], bar_width, color='b', align='center', edgecolor='none', left=left_bound)
        ax.barh(ind, null_dict['null_0'], bar_width, color='w', align='center', edgecolor='none', left=left_bound)

        # looping through remaining time frames
        for p in range(1, len(null_dict)):
            time_add = room_durations[p - 1]
            left_bound += time_add
            ax.barh(ind, full_dict['full_%s' % p], bar_width, color='b',
                    align='center', edgecolor='none', left=left_bound)
            ax.barh(ind, null_dict['null_%s' % p], bar_width, color='w',
                    align='center', edgecolor='none', left=left_bound)

        # save the plot and return the save location
        plt.savefig(file_path)
        plt.close(fig)
        return file_path
