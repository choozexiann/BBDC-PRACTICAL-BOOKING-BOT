
import sys
sys.path.append('../')

from utils import *
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import warnings
import logging


warnings.filterwarnings("ignore", category=DeprecationWarning)
global driver

logging.basicConfig(filename = '3APRAC.log', level = logging.INFO,
                    format = '%(asctime)s:%(message)s')


def open_page(driver, username, password):
    while True:
        try:
            driver.get('https://info.bbdc.sg/members-login/')
            break
        except Exception as e:
            logging.critical(e, exc_info=True)
            sleep_time = random.randint(1500, 2000)
            driver.quit()
            print("Sleeping for {} seconds".format(sleep_time))
            time.sleep(sleep_time)
            print("Retrying open_page now.")
            driver = initialize_driver(headless)
            continue

    time.sleep(4)
    database_filename = "database.pkl"
    wait = WebDriverWait(driver, 300)
    user = attrib_decomposer(username, password, database_filename)  # Search for User in DB
    wait.until(EC.visibility_of_element_located((By.NAME, 'txtNRIC'))).send_keys(user.username)
    wait.until(EC.visibility_of_element_located((By.NAME, 'txtpassword'))).send_keys(user.password)
    login_button = driver.find_element(By.ID, 'loginbtn')
    login_button.click()
    try:
        driver.find_element(By.ID, 'proceed-button').click()
    except NoSuchElementException:
        pass
    print("[3A PRAC] successfully logged in!")

    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it(driver.find_element(By.NAME, 'leftFrame')))
    wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'Booking without Fixed Instructor'))).click()

    # I agree page
    driver.switch_to.default_content()
    frame = driver.find_element(By.NAME, 'mainFrame')
    driver.switch_to.frame(frame)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn"))).click()

    # booking date/time selection page
    wait = WebDriverWait(driver, 300)
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it(driver.find_element(By.NAME, 'mainFrame')))
    wait.until(EC.visibility_of_element_located((By.ID, "checkMonth")))
    for x in range(0, 12):
        months = driver.find_elements_by_id('checkMonth')
        months[x].click()  # all months
    sessions = driver.find_elements_by_name('Session')
    for x in range(0, 8):
        sessions[x].click()  # all sessions
    for x in range(0, 7):
        days = driver.find_elements_by_name('Day')
        days[x].click()  # all days
    return


def main(username, password, headless = True, RESTART_TIME = [1000, 1500]):
    error_count = 0
    count = 0
    booked_slots = []
    driver = None
    # v = random.randint(10, 20)
    try:
        while 1:
            if not driver:
                driver = initialize_driver(headless)
            else:
                driver.quit()
                driver = initialize_driver(headless)
            cycle_sleep = random.randint(RESTART_TIME[0], RESTART_TIME[1])
            open_page(driver, username, password)
            count = count + 1
            print("[3A PRAC ", count, "] starting attempt", count)
            logging.info("[3A PRAC {0}] starting attempt {0}".format(count))
            print("[3A PRAC ", count, "] searching for slots")

            try:
                driver.find_element(By.NAME, 'btnSearch').click()
            except NoSuchElementException:
                pass

            print("[3A PRAC ", count, "] on slots page!")
            # booking process
            wait = WebDriverWait(driver, 10)
            time.sleep(2)

            try:
                driver.switch_to.alert.accept()

            except NoAlertPresentException:
                pass

            if len(driver.find_elements_by_id("TblSpan2")) == 1:  # [ALL SLOTS BOOKED]
                print("[3A PRAC ", count, "] no available slots detected")
                logging.info("[3A PRAC {}] no available slots detected, closing driver".format(count))

            else:
                print("[3A PRAC ", count, "] slots detected, checking dates.")
                logging.info("[3A PRAC {}] slots detected, checking dates.".format(count))
                print('[3A PRAC ', count, '] Removing slots not within date range!')
                slots = []
                table_ended = False
                row_counter = 3

                while not table_ended:
                    date_xpath = "/html/body/table/tbody/tr/td[2]/form/table[1]/tbody/tr[10]/td/table/tbody/tr[{}]/td[1]".format(
                        row_counter)
                    try:
                        date_found = driver.find_element(By.XPATH, date_xpath).text.splitlines()[0]
                        user_slots = slots_check(date_found, user.date_range)
                        if user_slots:
                            for j in range(3, 11):
                                slot_xpath = "/html/body/table/tbody/tr/td[2]/form/table[1]/tbody/tr[10]/td/table/tbody/tr[{}]/td[{}]/input".format(
                                    row_counter, j)
                                try:
                                    slot = driver.find_element(By.XPATH, slot_xpath)
                                    if int(j - 3) in user_slots:
                                        slots.append(slot)
                                        print("[3A PRAC {0}] slot {1} found on date {2}. ".format(count, j-3, date_found))
                                        logging.info("[3A PRAC {0}] slot {1} found on date {2}. ".format(count, j-3, date_found))
                                except NoSuchElementException:
                                    continue

                    except NoSuchElementException:
                        table_ended = True
                        break
                    row_counter += 1

                if not slots:
                    print("[3A PRAC ", count, "] all slots did not fall into date range.")
                    logging.info("[3A PRAC {}] all slots did not fall into date range.".format(count))

                else:
                    for slot in slots:  # Selecting all checkboxes
                        slot.click()
                        driver.find_element_by_class_name(
                            'pgtitle').click()  # clicking random element to hide hover effect

                    # Selecting Submit
                    driver.find_element(By.NAME, 'btnSubmit').click()
                    # Selecting confirm
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@value='Confirm']")))
                    driver.execute_script("window.confirm = function(){return true;}")
                    driver.find_element_by_xpath("//input[@value='Confirm']").click()
                    print("""\
                    [3A PRAC " {} "] Slot has been booked, unless consecutive or insufficient balance. 
                    Please check webpage for details)\
                    """.format(count))
                    logging.info("[3A PRAC {}] Slot booked! Please check webpage for details.".format(count))
                    time.sleep(2)

                    try:
                        driver.switch_to.alert.accept()
                    except NoAlertPresentException:
                        pass

                    if len(driver.find_elements_by_id("errtblmsg")) == 1:
                        print("[3A PRAC ", count, "] Error button - may have failed to snatch slot.")

                    time.sleep(2)


            driver.delete_all_cookies()
            print('[3A PRAC ', count, '] deleted all cookies, closing driver')
            driver.quit()
            print("[3A PRAC ", count, "] slots attempted to book are {}".format(booked_slots))
            logging.info("[3A PRAC {0}] slots attempted to book are {1}.".format(count, booked_slots))
            print("[3A PRAC ", count, "] attempting to restart script in", cycle_sleep, "seconds..")
            print("[3A PRAC ", count, "] press Ctr-C to stop script at any time!")
            time.sleep(cycle_sleep)

    except Exception as e:
        print("[3A PRAC ", count, "] Something went wrong during excecution. Feel free to report this on github")
        print(e)
        logging.critical("[3A PRAC {0}] Something went wrong during excecution (Error Count: {1}).".format(count, error_count))
        logging.critical("[3A PRAC {0}] {1}.".format(count, e))

        if error_count >= 4:
            print("[3A PRAC ", count, "] Critical error after 4 retries")
            logging.critical("[3A PRAC {0}] Critical error after 4 retries, shutting down. (Error Count: {1})".format(count, error_count))
            os.system("pause")
            sys.exit()
        else:
            error_count += 1
            if driver:
                driver.quit()
            error_sleep = random.randint(1000, 2000)
            print("[3A PRAC {0}] Restarting script now after {2} seconds (Error Count: {1}). Script will exit once error count reaches 4".format(count, error_count, error_sleep))
            time.sleep(error_sleep)
            main(username, password, headless, RESTART_TIME)




if __name__ == "__main__":
    database_filename = "database.pkl"
    if not os.path.isfile("database.pkl"):
        pickle_reset(database_filename)
    if not os.path.isfile("chromedriver.exe"):
        download_chromedriver()
    try:
        username = input('BBDC username: ')
        if username == 'reset':
            pickle_reset(database_filename)
            exit()
        password = int(input('BBDC password: '))
        headless = str(input('Headless Chrome (without GUI) [Y/N]'))
        if headless.lower() == 'y':
            headless = True
        else:
            headless = False
        RESTART_TIME = input("""
        Please key in restart time range in seconds between each cycle of checks (E.g. "200 - 900"). 
        I typically run 1000-1500 seconds and let it sit for the day.) If the requests are too fast it may lead to ip bans.
        In the case of IP ban, if your IP is dynamically assigned (DHCP) just restart your wifi after waiting ~24hours, you will change IP.
        Hit Enter if you wish to use default( 1000-1500 seconds):
        """)
        if RESTART_TIME == '':
            RESTART_TIME = [1000, 1500]
        else:
            RESTART_TIME = [int(i) for i in RESTART_TIME.replace(' ', '').split('-')]
    except:
        print('invalid inputs!')
    user = initialize_user(username, password, database_filename)


    main(username, password, headless, RESTART_TIME)
