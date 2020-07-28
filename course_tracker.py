import time
import random
import notify2
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

username = input("Username: ")
password = getpass("Password: ")
course_id = input("Course (exact title  on Zambeel e.g. 'CS 466-S1'): ")

main_url = 'https://zambeel.lums.edu.pk/'

print("Make sure you have changed the post_login_url to your Add Class page.")
post_login_url = 'https://zambeel.lums.edu.pk/psp/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_CART.GBL?Page=SSR_SSENRL_CART&Action=A&ACAD_CAREER=UGDS&EMPLID=19206&INSTITUTION=LUMS&STRM=2001'

proceed_btn_locator = 'DERIVED_REGFRM1_LINK_ADD_ENRL$82$'
finish_btn_locator = 'DERIVED_REGFRM1_SSR_PB_SUBMIT'

notif_title = course_id + ' IS OPEN'
notif_body = 'Your course %s is now open. Attempting to enroll.' % course_id
status = ''
path = ''
# try:

print("INITIATING COURSE TRACKER FOR %s TO GET %s" % (username, course_id))

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
try:
  path = ChromeDriverManager().install()
except:
  print("Using chromdriver.exe that came with the script for Windows...")
  path = './chromedriver.exe'

browser = webdriver.Chrome(executable_path=path, options=chrome_options)
browser.get(main_url)
wait = WebDriverWait(browser, 3)

loginform = WebDriverWait(browser, 3).until(EC.visibility_of_element_located((By.ID, "login")))
print("Current Page Title: %s" % browser.title)

userid = browser.find_element_by_id("userid")
pwd = browser.find_element_by_id("pwd")

userid.clear()
pwd.clear()
userid.send_keys(username)
pwd.send_keys(password)
pwd.send_keys(Keys.RETURN)
# logs in

while (status != "Open"): 
  browser.get(post_login_url)
  browser.switch_to.frame("ptifrmtgtframe")

  course_link = browser.find_element_by_partial_link_text(course_id)
  # status_div is available, get image inside
  print(course_link.get_attribute("text"))

  # print(table_div)
  course_row = course_link.find_element_by_xpath("./../../../../..")
  status_img = course_row.find_element_by_xpath("//img[@alt='Closed']")
  status = status_img.get_attribute("alt")
  print(status)

  minutes = random.randint(5, 20) # between 5 to 20 minutes
  delay = 60 * minutes

  print("Trying again in %d minutes..." % minutes)
  time.sleep(delay)


print(notif_title)
notify2.init(notif_title)
n = notify2.Notification(notif_title, notif_body)
n.show()

proceed_btn = browser.find_element_by_id(proceed_btn_locator)
proceed_btn.click()

finish_btn = WebDriverWait(browser, 3).until(EC.visibility_of_element_located((By.ID, finish_btn_locator)))
finish_btn.click()

browser.close()