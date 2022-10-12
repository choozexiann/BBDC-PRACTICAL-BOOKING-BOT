import sys
sys.path.append('../')
from oop import *
from selenium import webdriver
import urllib.request
from datetime import date, timedelta, datetime
global username, password
import requests
import zipfile

def pickle_loader(filename):
    with open(filename, 'rb') as inp:
        import_list = pickle.load(inp)
    return import_list


def pickle_dumper(instances_list, filename):  # appends to list and dumps list
    pickle_loader(filename)
    with open(filename, 'wb') as outp:
        pickle.dump(instances_list, outp, pickle.HIGHEST_PROTOCOL)
    return


def view_database(filename):
    with open(filename, 'rb') as inp:
        import_list = pickle.load(inp)
    return import_list


def attrib_decomposer(username, password, filename):
    user_data = None
    database = pickle_loader(filename)
    for i in range(len(database)):
        if str(database[i].username) == str(username) and int(database[i].password) == int(password):
            user_data = database[i]
            return user_data
    if user_data is None:
        print('[attrib_decomposer], USER NOT FOUND!')
        user_data = initialize_user(username, password, filename)
        return user_data


def check_date_today(website_date, days_within):
    website_date = datetime.datetime.strptime(website_date, '%d/%m/%Y').date()
    today = date.today()
    if website_date <= today + timedelta(days_within):
        return True
    else:
        return False


def save_pickle(self, filename):
    # saving to pickle
    current_list = pickle_loader(filename)
    current_list.append(self)  # append to list before saving again
    pickle_dumper(current_list, database_filename)


def initialize_user(username, password, filename):
    user_data = None
    answer = None
    count = None
    database = pickle_loader(filename)
    for i in range(len(database)):
        if str(database[i].username) == str(username) and int(database[i].password) == int(password):
            user_data = database[i]
    if user_data is None:
        print('[Initialization], USER NOT FOUND!')
        count = 1
    else:
        user_data.selection_print()
        print("\n\n")
        answer = input("are all of these correct? Input Y/N: ").upper()
    if answer == "Y":
        return user_data
    if answer == "N" or count == 1:
        try:
            for i in range(len(database)):
                if database[i].username == username and database[i].password == password:
                    database.pop(i)
        except Exception:
            pass
        user_data = User.from_user_input()
        database.append(user_data)
        pickle_dumper(database, filename)
        print('User successfully saved to DB')
        return user_data
    else:
        print('unrecognized input')
        exit()
        return


def initialize_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--remote-debugging-port=9222")
    options.page_load_strategy = 'normal'
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--log-level=3')
    # options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def slots_check(BBDCdate, date_ranges):
    BBDC_datetimeobj = datetime.strptime(BBDCdate, "%d/%m/%Y")
    for key, value in date_ranges.items():
        if BBDC_datetimeobj.date() == key.date():
            return value
    return False


database_filename = "database.pkl"



def session_check(BBDCdate, date_ranges): #hopefully dict of date times
    within_dates = False
    for i, date_range in enumerate(date_ranges):
        date1 = datetime.strptime(date_range.split('-')[0], "%d/%m/%y")
        date2 = datetime.strptime(date_range.split('-')[1], "%d/%m/%y")
        if date1 <= datetime.strptime(BBDCdate, "%d/%m/%Y") <= date2:
            within_dates = True
    return within_dates



def download_chromedriver():
    response = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE')
    latest_version = response.content.decode('UTF-8')
    file_url = ('https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip'.format(latest_version))
    filehandle, _ = urllib.request.urlretrieve(file_url)
    zip_file_object = zipfile.ZipFile(filehandle, 'r')
    first_file = zip_file_object.namelist()[0]
    file = zip_file_object.open(first_file)
    content = file.read()
    f = open("chromedriver.exe", "wb").write(content)

