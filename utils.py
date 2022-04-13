
def fill_box(FieldInput, userinput):
	id_box = driver.find_element_by_name(str(FieldInput))
	return id_box.send_keys(userinput)

#def send_keys(FieldInput):
	#id_box.send_keys('my_username')
