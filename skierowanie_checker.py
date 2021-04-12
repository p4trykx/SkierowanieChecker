import time
import datetime
import os
import codecs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import msg_send
import secrets

def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check_skierowanie( send_all_msg=True):
    start_time = time.time()

    current_dir = os.path.dirname(__file__)
    print('working dir ',current_dir)

    #PATH = "C:\\Program Files (x86)\\chromedriver.exe"
    PATH = os.path.join(current_dir,'chromedriver.exe')
    PATH = os.path.join(current_dir,'geckodriver.exe')

    site = 'https://pacjent.erejestracja.ezdrowie.gov.pl/zaloguj'


    #do not show 
    #options = webdriver.ChromeOptions() 
    #options.add_experimental_option("excludeSwitches", ["enable-logging"])
    #driver = webdriver.Chrome(options=options, executable_path=PATH)

    driver = 0
    if (os.name == 'posix'):
        driver = webdriver.Firefox()
    else:
        driver = webdriver.Firefox(executable_path=PATH)

    driver.get(site)
    #driver.maximize_window()
    print(f"{bcolors.WARNING}Current ulr in browser{bcolors.ENDC}")
    first_url = driver.current_url 
    print (first_url)
    print(f"{bcolors.BOLD}Waiting for pz click{bcolors.ENDC}")

    try:#if timeout 
        #driver.implicitly_wait(10)
        login_redirected = WebDriverWait(driver,45).until( 
            EC.url_contains( 'https://login.gov.pl/login')
        )
        print (driver.current_url)
        #klikniecie z w logowanie w profil zaufany
        profil_zaufany_a = WebDriverWait(driver,45).until( 
            EC.element_to_be_clickable( (By.ID,'aLargeId_6689986577400963516'))
        )
        #wait because of javascript 
        time.sleep(2)
        profil_zaufany_a.click()
        #time.sleep(1)
        #wait for redirection
        print(f"{bcolors.WARNING}Waiting for redirection to PZ login page{bcolors.ENDC}")
        pz_page= WebDriverWait(driver,45).until( 
                 EC.url_contains('https://pz.gov.pl/dt/login') 
        )
        print (driver.current_url)
        #wait for login form
        login_input = WebDriverWait(driver,45).until( 
            EC.presence_of_element_located( (By.ID,'loginForm:login'))
        )
        login_pass = driver.find_element_by_id('loginForm:hasło')
        login_click = WebDriverWait(driver,45).until( 
            EC.element_to_be_clickable( (By.ID,'loginForm:loginButton'))
        )
        #if all present fill out the form
        if ( login_input and login_pass and login_click ):
            login_input.send_keys(secrets.login_str)
            time.sleep(1)    
            login_pass.send_keys(secrets.pass_str)
            time.sleep(1)    
            login_click.click()
        #wait for page change back to pacjent
        page_pacjent  = WebDriverWait(driver,45).until( 
            EC.url_contains('https://pacjent.erejestracja.ezdrowie.gov.pl/wizyty')
                )

        msg_body = ''
        time.sleep(1)
        
        #wait for 'brak wynikow'
        try:
            brak_wynikow = WebDriverWait(driver,45).until( 
                EC.presence_of_element_located( (By.CLASS_NAME,'sc-eCssSg'))
                )
        except Exception as e:
            #if "brak wynikow not found"
            pass
        
        if ( ('Brak wyników' in driver.page_source ) ):
            print(f"{bcolors.FAIL}'Brak WYNIKÓW!!!!'{bcolors.ENDC}")
            if ( send_all_msg ):#send msg 
                msg_body = "Brak Wyników e-skierowanie"
            else:
                msg_body =''
            #call.call_my_phone()
        else:
            print(f"{bcolors.OKGREEN}'JEST SKIEROWANIE'{bcolors.ENDC}")
            msg_body = "JEST E-SKIEROWANIE !!! UWAGA!"
            #call.call_my_phone()

        msg_send.whatsapp_send(msg_body)



    except Exception as e:
        print(f"{bcolors.FAIL}Exception!!!!{bcolors.ENDC}") 
        print(e)
        msg_send.whatsapp_send('Exception')

    finally:

        date_str = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S')
        page_str = str(driver.page_source)
        log_path = os.path.join(current_dir,'logs')
        ok = driver.save_screenshot( os.path.join(log_path,f'Screenshot{date_str}.png') )
        driver.quit()
        with codecs.open( os.path.join(log_path, f'PageOutput{date_str}.html'), 'w','utf-8') as text_file:
            text_file.write(page_str)

    end_time = time.time()
    time_lapsed = end_time - start_time
    time_convert(time_lapsed)


if (__name__ == '__main__'):
    
    while True:
        
        check_skierowanie(send_all_msg=True)

        print(f"{bcolors.OKCYAN}'Sleep'{bcolors.ENDC}")
        time.sleep(60*30)
        
