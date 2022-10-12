import pickle
import sys
from datetime import date, timedelta, datetime


class User:
    database_filename = "database.pkl"

    def __init__(self, initial_data):
        for key in initial_data:
            setattr(self, key, initial_data[key])

    @classmethod
    def from_user_input(cls):  # usage: zexian (new instance name) = User.from_user_input()
        list_of_fields = ['username', 'password', 'date_range']
        new_dict = dict.fromkeys(list_of_fields)
        print("please follow these format for keying in your values: 'all' or space delimited entries such as '0 1 2 3 4'' or '0 5 6'.")
        print()
        print(
            """Example:
            username: 123A14021999 [BBDC USERNAME]
            password: 123456 [BBDC PASSWORD]
            date_range: 06/05/22-08/05/22: all [DD/MM/YY-DD/MM/YY: X,X,X-X format] (inclusive)
                        23/05/22: 0, 2, 3-4 [DD/MM/YY-DD/MM/YY: X,X,X-X format]
            """)

        for key in new_dict:
            if key == 'date_range':
                print("""\
                    Session 0: 07:30 - 09:10
                    Session 1: 09:20 - 11:00
                    Session 2: 11:30 - 13:10
                    Session 3: 13:20 - 15:00
                    Session 4: 15:20 - 17:00
                    Session 5: 17:10 - 18:50
                    Session 6: 19:20 - 21:00
                    Session 7: 21:10 - 22:50
                     
                    date_range: [DD/MM/YY-DD/MM/YY: X,X,X-X format] (inclusive). Can use 'all' as well:
                    Examples:
                        06/05/22-08/05/22: all
                        23/05/22: 0, 2-4, 7
                        09/09/22-10/09/22: 1
                        """)
            try:
                user_input = input("Please type your " + key + " : ")
                if user_input[-1] == ' ':
                    user_input = user_input.rstrip(' ')

                if key in ['username', 'name']:
                    new_dict[key] = str(user_input)

                if key == 'password':
                    new_dict[key] = str(user_input)

                elif key == 'date_range':
                    date_ranges = dict()
                    user_is_done = False
                    while not user_is_done:
                        if user_input == '':
                            user_is_done = True
                            print('Here are the keyed in dates: If there is an issue, press Ctr-C to retype.')
                            for k, value in date_ranges.items():
                                print(k.strftime("%d/%m/%Y"), 'sessions: ', value)
                        else:
                            date_ranges = user_date_to_dict(date_ranges, user_input)
                            user_input = input("Please type the next date! Hit Enter to stop keying in dates: ")
                    new_dict[key] = date_ranges
            except Exception as e:
                print('Please retype the fields again and follow the example.')
                print(e)
                sys.exit()

        return cls(new_dict)

    def selection_print(self):  # meant to spell out every info possible about you.
        keylist = []
        valuelist = []
        for key, value in self.__dict__.items():
            if type(value) is dict:
                print()
                print('Dates are as follows: ')
                for date, sessions in value.items():
                    print(date.strftime("%d/%m/%Y"), 'sessions: {}'.format(', '.join([str(i) for i in sessions])))
                print()
                continue
            keylist.append(key)
            valuelist.append(value)
        for i in range(len(valuelist)):
            try:
                print('{} is saved as: {}'.format(keylist[i], eval(valuelist[i])))
            except:
                print('{} is saved as: {}'.format(keylist[i], valuelist[i]))
        return

    def __repr__(self):
        return "User: ('{}')".format(self.name)

    def __str__(self):
        return "User: ('{}')".format(self.name)

def sessions_breakdown(sessions_list):
    result_list = []
    if sessions_list == 'all':
        return [i for i in range(0,8)]
    else:
        sessions_list = sessions_list.split(',')
        # print(sessions_list)
        for session in sessions_list:
            if '-' in session:
                s1, s2 = session.split('-')
                result_list.extend(range(int(s1), int(s2) + 1))
            else:
                result_list.append(int(session))
    return result_list



def user_date_to_dict(date_ranges, user_input):
    user_input = [i for i in user_input.splitlines() if i != '']
    for entry in user_input:
        if len(entry.split(':')) == 2:
            date_entry, sessions = [i.replace(' ', '') for i in entry.split(':')]
        else:
            raise ValueError('Wrong input! Please follow the format given.')
        # print('before', sessions)
        sessions = sessions_breakdown(sessions)
        # print('after', sessions)
        if len(date_entry.split('-')) >= 2:
            start_date = datetime.strptime(date_entry.split('-')[0], "%d/%m/%y")
            end_date = datetime.strptime(date_entry.split('-')[1], "%d/%m/%y")
            for single_date in day_increment(start_date, end_date):
                date_ranges[single_date] = sessions
        else:
            date_ranges[datetime.strptime(date_entry, "%d/%m/%y")] = sessions
    return date_ranges


def pickle_reset(filename):  # FOR DEBUGGING
    sample = {'username': '123A14021999', 'password': "123456",
              'month_selection': range(0, 1), 'time_selection': range(0, 8),
              'day_selection': range(0, 7), 'date_range': ['01/08/2022-03/08/2022']}
    smple = User(sample)
    empty_list = [smple]
    openfile = open(filename, 'wb')
    pickle.dump(empty_list, openfile)
    openfile.close()
    return



def day_increment(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
