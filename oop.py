import pickle
import sys



class User:
    database_filename = "database.pkl"

    def __init__(self, initial_data):
        # database_filename = "database.pkl"
        for key in initial_data:
            setattr(self, key, initial_data[key])
        # print('[init], nametest',self.name)
        # print('[init], vars', vars(self))

    @classmethod
    def from_user_input(cls):  # usage: zexian (new instance name) = User.from_user_input()
        list_of_fields = ['username', 'password', 'month_selection', 'time_selection', 'day_selection', 'date_range']
        new_dict = dict.fromkeys(list_of_fields)
        all_dict = {'month_selection': range(0, 12), 'time_selection': range(0, 8), 'day_selection': range(0, 7)}

        print("please follow these format for keying in your values: 'all' or space delimited entreis such as '0 1 2 3 4'' or '0 5 6'.")
        print()
        print('For date_range type in DD/MM/YY with hyphen, followed by space between the date ranges such as:')
        print('"25/01/22-28/01/22 02/02/22-05/02/22"')
        print('You can also type "25/01/22"')
        print(
            """Example:
            username: 123A14021999 [BBDC USERNAME]
            password: 123456 [BBDC PASSWORD]
            month_selection: 0 1 [Possible Entries: 0 1 2 3 4 5 6 7 8 9 10 11, with 0 being this month]
            time_selection: 0 2 5 6 [Possible Entries: 0 1 2 3 4 5 6 7, with 0 being session 1]
            day_selection: all [Possible Entries: 0 1 2 3 4 5 6, with 0 being Mon]
            date_range: 24/05/22-05/06/22 [DD/MM/YY format]
            """)

        for key in new_dict:
            user_input = input("Please type your " + key + " : ")
            if user_input[-1] == ' ':
                user_input = user_input.rstrip(' ')
            try:
                if key in list(all_dict.keys()):
                    if user_input == 'all':
                        new_dict[key] = all_dict[key]

                    elif len(user_input.split(' ')) > 1:
                        process_input = []
                        for i, v in enumerate(user_input.split(' ')):
                            process_input.append(int(v))
                        new_dict[key] = process_input

                    elif len(user_input.split(' ')) == 1:
                        new_dict[key] = range(int(user_input), int(user_input) + 1)


                elif key in ['username', 'name']:
                    new_dict[key] = str(user_input)

                elif key in ['password', 'tpdsmodule_selection']:
                    new_dict[key] = int(user_input)

                elif key == 'date_range':
                    if user_input == 'all':
                        new_dict[key] = "01/01/01-01/01/50"
                    elif len(user_input.split('-')) == 1:
                        new_dict[key] = ['{0}-{0}'.format(user_input)]
                    else:
                        new_dict[key] = user_input.split(' ')
            except:
                print('Please retype the fields again and follow the example.')
                sys.exit()
        return cls(new_dict)

    def selection_print(self):  # meant to spell out every info possible about you.
        keylist = []
        valuelist = []
        for key, value in self.__dict__.items():
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


def pickle_reset(filename):  # FOR DEBUGGING
    sample = {'username': '123A14021999', 'password': 123456,
              'month_selection': range(0, 1), 'time_selection': range(0, 8),
              'day_selection': range(0, 7), 'date_range': ['01/08/2022-03/08/2022']}
    smple = User(sample)
    empty_list = [smple]
    openfile = open(filename, 'wb')
    pickle.dump(empty_list, openfile)
    openfile.close()
    return
