import time
import random
try:
  import notify2
except:
  print("Notifications are available on Linux only.")
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

main_url = 'https://zambeel.lums.edu.pk/'
post_login_url = 'https://zambeel.lums.edu.pk/psp/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_CART.GBL?Page=SSR_SSENRL_CART&Action=A&ACAD_CAREER=UGDS&EMPLID=19206&INSTITUTION=LUMS&STRM=2001'

username = input("Username: ")
password = getpass("Password: ")
course_ids_raw = input("Courses (comma delimited list of exact titles as on Zambeel e.g. 'CS 370-S1, CS 466-S1'): ").split(',')
course_ids = list(map(lambda s: s.strip(), course_ids_raw)) # strip all string spaces L&R

print("Make sure you have changed the post_login_url to your Add Class page inside the script.")
statuses = ['' for x in range(len(course_ids))] # statuses of all courses
path = ''


print("INITIATING COURSE TRACKER FOR %s TO GET %s" % (username, course_ids))

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

while not ("Open" in statuses): 
  browser.get(post_login_url)
  browser.switch_to.frame("ptifrmtgtframe")

  for i, course_id in enumerate(course_ids):
    try:
      course_link = browser.find_element_by_partial_link_text(course_id)
      course_row = course_link.find_element_by_xpath("./../../../../..")

      # status_div is available, get image inside
      status_img = course_row.find_element_by_xpath("//img[@alt='Closed']")
      statuses[i] = status_img.get_attribute("alt")
      print(course_link.get_attribute("text"), "is", statuses[i])
    except:
      print("An error occurred checking for the course %s. Make sure it exists in your cart and was entered in the correct format." % course_id)
    
  if (not "Open" in statuses):
    minutes = random.randint(5, 20) # between 5 to 20 minutes
    delay = 60 * minutes

    print("Trying again in %d minutes..." % minutes)
    time.sleep(delay)


for i, course_id in enumerate(course_ids):
  if (statuses[i] == "Open"):
    try:
      notif_title = course_id + ' IS OPEN'
      notif_body = 'Your course %s is now open. Attempting to enroll.' % course_id
      print(notif_title)
      notify2.init(notif_title)
      n = notify2.Notification(notif_title, notif_body)
      n.show()
    except:
      pass
    
    try:
      browser.get(post_login_url)
      browser.switch_to.frame("ptifrmtgtframe")
      
      proceed_btn = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.ID, 'DERIVED_REGFRM1_LINK_ADD_ENRL$82$')))
      proceed_btn.click()

      finish_btn = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.ID, finish_btn_locator)))
      finish_btn.click()
      break
    except RuntimeError as re:
      print("Could not enroll.", re)


browser.close()
