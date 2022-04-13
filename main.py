from credentials import USERNAME, PASSWORD
import selenium
from utils import *



def LoginPage(USERNAME,PASSWORD):
	username_field = fill_box('txtNRIC', USERNAME)
	password_field = fill_box('txtpassword', PASSWORD)
	login_button = driver.find_element_by_id('loginbtn')
	login_button.click()

id_box.send_keys('my_username')
if __name__ == "__main__":
	driver = webdriver.Chrome()
	driver.get('https://info.bbdc.sg/members-login/')
	main()