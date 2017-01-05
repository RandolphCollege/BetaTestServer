from BetaTestInterface import BetaTestInterface
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import calendar
import datetime
import os
import pickle


class RoomLocation(BetaTestInterface):
    def __init__(self, database, patientID, day):
        BetaTestInterface.__init__(self, database, patientID, 'RoomLocationBeta', 'AnalysisRoomLocation', day)
        self.patientID = patientID

    '''
    # Expected array of tuples input as data.
    # First column as timestamp formatted as an integer or long
    # Second column as room location formatted as a string
    # Returns file save location of bar chart with location
    # on the y axis and time on the x axis
    '''
    def get_room_list(self):
        print('in room list')
        self.fetch_from_database(database_name = self.database_name,
                                 table_name ='rooms',
                                 to_fetch ='ROOM_NAME')
        data  = self.fetchall()
        rooms = zip(*data)[0]
        rooms = list(rooms)
        rooms.append('RNK')
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
            print(metric_data)
            return []
        else:
            go_one = pickle.loads(zip(*list(zip(*metric_data)))[0][0])[0]
            step_one = zip(*metric_data)
            step_two = list(step_one)
            step_three = zip(*step_two)
            step_four = step_three[0]
            step_five = step_four[0]
            step_six = pickle.loads(step_five)
            step_seven = step_six[0]
            step_eight = step_seven[0]
            return np.array(step_seven)

    def filter_room_data(self, data):
        last_values_list = []
        prior_room       = ''
        room_trans       = 0
        filtered_data    = []
        data = [row[1] for row in data]
        for i in data:
            if i[1] != prior_room:
                if len(last_values_list) >= 10:
                    room_trans      += 1
                    last_values_list = [i[1]]
                    prior_room       = i[1]
                    filtered_data.append(i)
                else:
                    last_values_list = [i[1]]
                    prior_room       = i[1]
                    filtered_data    = filtered_data[:(len(filtered_data) - len(last_values_list)-1)]
            if i[1] == prior_room:
                last_values_list.append(i[1])
                filtered_data.append(i)
        return np.array(filtered_data)

    def process_data(self, data):
        times, room_data = zip(*data)
        timeout_time = 60000 * 1

        times = list(times)
        room_data = list(room_data)
        time_data = map(lambda x: int(x), times)
        if not isinstance(time_data[0], long):
            new_time = [t - self.fuck_up_hack for t in time_data] #[self.sql_datetime_to_utc(t) - self.fuck_up_hack for t in time_data]
        else:
            new_time = [t - self.fuck_up_hack for t in time_data]


        #Use this if there is a day with both utc timestamps and new timestamps. It's stupid slow but will work
        '''
        new_time = []
        for t in time_data:
            if not isinstance(t, long):
                new_time += [self.sql_datetime_to_utc(t) - self.fuck_up_hack]
            else:
                new_time += [t - self.fuck_up_hack]
        '''
        time_data = new_time

        # turn interactive off so that the figure is not automatically displayed
        plt.ioff()

        # get the date information for this data
        start_utc      = self.get_stamp_window_from_utc(time_data[0])[0]
        end_utc        = self.get_stamp_window_from_utc(time_data[0])[1]
        start_datetime = self.utc_to_datetime(start_utc)
        start_date     = start_datetime.date()
        data_day       = calendar.day_name[start_datetime.weekday()]

        # get the list of rooms in the house
        room_list = self.get_room_list()

        # set file name and save folder path
        file_name      = "%s_%s_%s_RoomLocation.png" % (self.patientID, start_date, data_day)
        current_dir    = os.getcwd()
        save_file_path = 'roomSaves'
        room_save_path = os.path.join(current_dir, save_file_path)
        if not os.path.exists(room_save_path):
            os.makedirs(room_save_path)
        file_path = os.path.join(room_save_path, file_name)

        # set up variable for previously occupied room and lists to fill
        # with durations of room occupations and the corresponding rooms
        previous_room  = 'No Connection'
        previous_time  = start_utc
        time_in = start_utc
        room_durations = []
        room_locations = []
        duplicate_count = 0

        print self.patientID

        # looping through the entire day's data...
        for i in range(len(time_data)):
            current_room = room_data[i]
            current_time = time_data[i]
            current_duration = current_time - previous_time  # Get how long between this data point and the last

            timeout = current_time - time_in >= timeout_time
            if current_room != previous_room and not timeout:
                # if the room just changed and it's been less than a minute since the last data point
                #  if we have data in the first minute of the day, mark it rather than No Connection
                if previous_room == 'No Connection':
                    previous_room = current_room

                room_durations += [current_duration]  # Add the current duration to the time list
                room_locations.append(previous_room)  # Add the last room to the room list paired with current duration
                if previous_room not in room_list:
                    room_list.append(previous_room)
                previous_room = current_room          # Set the previous room as the one we just looked at
                previous_time = current_time

            elif timeout:
                # If don't have data for one minute or more, we've lost connection
                # Count the first minute to the previous room
                room_durations += [time_in - previous_time + timeout_time]
                room_locations.append(previous_room)
                if previous_room not in room_list:
                    room_list.append(previous_room)

                # Then add a no connection time block until the next data point
                room_durations += [current_time - time_in - timeout_time]
                room_locations.append('No Connection')

                # And resume normal operations
                previous_room = current_room
                previous_time = current_time
            elif time_in == 0:
                duplicate_count += 1
                continue
            time_in = current_time  # Update when our last data point was

        # include end of day data missed by the for loop
        current_duration = time_data[-1]-previous_time
        if end_utc - time_data[-1] > timeout_time:
            room_durations += [current_duration + timeout_time]
            room_locations.append(room_data[-1])
            room_durations += [end_utc - time_data[-1] - timeout_time]
            room_locations.append('No Connection')
        else:
            room_durations += [current_duration + (end_utc - time_data[-1])]
            room_locations.append(room_data[-1])

        if room_data[-1] not in room_list:
            room_list.append(previous_room)

        dup_message = "********RoomLocationBetaTest********** \
        \n\nduplicate data point rejected \
        \n%s data points rejected\nPatient: %s\nDate: %s \
        \n\n***************************************" % (duplicate_count, self.patientID, start_date)

        if duplicate_count > 0:
            print dup_message

        """
        # Don't hate me for being a hack now...
        # This is actually pretty funny: we plot a set of stacked horizontal bar graphs
        # such that every room has the entire day filled, but when the room isn't
        # occupied, the color of the bar is white, and there's no border so it appears empty
        """

        # Create lists for each time frame as full or empty
        null_keys = ['null_%s' % n for n in range(len(room_locations))]
        full_keys = ['full_%s' % n for n in range(len(room_locations))]
        null_dict = dict.fromkeys(null_keys)
        full_dict = dict.fromkeys(full_keys)
        null_dict.update(dict(null_dict))
        full_dict.update(dict(full_dict))

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
        labels = ['19','20','21','22','23','0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']
        values = [86400000* t/24 for t in range(24)]
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

        # looping through remaining time frames
        for p in range(len(null_dict)):
            time_add = room_durations[p]
            ax.barh(ind, full_dict['full_%s' % p], bar_width, color='b',
                    align='center', edgecolor='none', left=left_bound)
            ax.barh(ind, null_dict['null_%s' % p], bar_width, color='w',
                    align='center', edgecolor='none', left=left_bound)
            left_bound += time_add

        # save the plot and return the save location
        plt.savefig(file_path)
        plt.close(fig)
        return file_path