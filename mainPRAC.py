
import sys
sys.path.append('../')

from utils import *
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
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
    print('username and password done')
    login_button = driver.find_element(By.ID, 'loginbtn')
    login_button.click()
    try:
        driver.find_element(By.ID, 'proceed-button').click()
    except NoSuchElementException:
        pass
    print('[login] login successful')

    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it(driver.find_element(By.NAME, 'leftFrame')))
    wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'Booking without Fixed Instructor'))).click()
    print('[hometoprac] successfully entered prac booking')

    # I agree page
    driver.switch_to.default_content()
    frame = driver.find_element(By.NAME, 'mainFrame')
    driver.switch_to.frame(frame)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn"))).click()
    print("[I agree] accepted")

    # booking date/time selection page
    wait = WebDriverWait(driver, 300)
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it(driver.find_element(By.NAME, 'mainFrame')))
    wait.until(EC.visibility_of_element_located((By.ID, "checkMonth")))
    for x in user.month_selection:
        months = driver.find_elements_by_id('checkMonth')
        months[x].click()  # all months
    print('[pracselect], months done')
    sessions = driver.find_elements_by_name('Session')
    for x in user.time_selection:
        sessions = driver.find_elements_by_name('Session')
        sessions[x].click()  # all sessions
    print('[pracselect], timesession done')
    for x in user.day_selection:
        days = driver.find_elements_by_name('Day')
        days[x].click()  # all days
    print('[pracselect], dayselection done')
    print("[preparation] preparation complete!")
    return


def main(username, password, headless = True):
    count = 0
    RESTART_TIME = random.randint(300, 1000)
    driver = initialize_driver(headless)
    # v = random.randint(10, 20)
    while 1:
        if driver:
            driver.quit()
            driver = initialize_driver(headless)
        print('[openpage] executing openpage')
        # try:
        open_page(driver, username, password)
        # except:
        #     print("[fatal] openpage could not execute properly.")
        #     logging.critical("[fatal] openpage could not execute properly.")
        #     print("sleeping for {} seconds.".format(RESTART_TIME))
        #     time.sleep(RESTART_TIME)
        try:
            count = count + 1
            print("[3A PRAC ", count, "] starting attempt", count)
            logging.info("[3A PRAC {0}] starting attempt {0}".format(count))
            print("[3A PRAC ", count, "] searching for slots")

            try:
                driver.find_element(By.NAME, 'btnSearch').click()
            except NoSuchElementException:
                pass

            print("[booking] on slots page!")
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
                # print("[3A PRAC ", count, "] delaying reopening page for", int(v), "seconds")
                # time.sleep(v)
                # driver = initialize_driver(headless)
                # open_page(driver, username, password)
                # print("[3A PRAC ", count, "] delaying for another", v, "seconds")
                # time.sleep(v)
                # wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn"))).click()
                # driver.find_element(By.NAME, 'btnSearch').click()

            else:
                print("[3A PRAC ", count, "] slots detected, checking dates.")
                logging.info("[3A PRAC {}] slots detected, checking dates.".format(count))
                print('[3A PRAC', count, '] Removing slots not within date range {} !'.format(user.date_range))

                slots = []
                table_ended = False
                row_counter = 3


                while not table_ended:
                    date_xpath = "/html/body/table/tbody/tr/td[2]/form/table[1]/tbody/tr[10]/td/table/tbody/tr[{}]/td[1]".format(
                        row_counter)
                    try:
                        date_found = driver.find_element(By.XPATH, date_xpath).text.splitlines()[0]
                        print("[3A PRAC ", count, "] date found :", date_found)
                        within_date = date_check(date_found, user.date_range)

                        if within_date:
                            for j in range(3,11):
                                slot_xpath = "/html/body/table/tbody/tr/td[2]/form/table[1]/tbody/tr[10]/td/table/tbody/tr[{}]/td[{}]/input".format(
                                    row_counter, j)

                                try:
                                    slot = driver.find_element(By.XPATH, slot_xpath)
                                    slots.append(slot)

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
                    driver.find_element_by_xpath("//input[@value='Confirm']").click()
                    print("[3A PRAC ", count, "] Slot booked! Please check webpage for details")
                    logging.info("[3A PRAC {}] Slot booked! Please check webpage for details.".format(count))
                    time.sleep(2)
                    driver.switch_to.alert.accept()
                    if len(driver.find_elements_by_id("errtblmsg")) == 1:
                        print("[3A PRAC ", count, "] Error button - may have failed to snatch slot.")

                    time.sleep(2)
            driver.delete_all_cookies()
            print('[3A PRAC', count, ']deleted all cookies, closing driver')
            driver.quit()
            print("[3A PRAC ", count, "] attempting to restart script in", RESTART_TIME, "seconds..")
            time.sleep(RESTART_TIME)

        except Exception as e:
            print("[3A PRAC ", count, "] Something went wrong during excecution .")
            print(e)
            logging.critical("[3A PRAC {}] Something went wrong during excecution.".format(count))
            logging.critical("[3A PRAC {0}] {1}.".format(count, e))



if __name__ == "__main__":
    database_filename = "database.pkl"
    if not os.path.isfile("database.pkl"):
        pickle_reset(database_filename)
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
    except:
        print('invalid inputs!')
    user = initialize_user(username, password, database_filename)


    main(username, password, headless)
