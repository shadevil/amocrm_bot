import time, re, getpass, os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

# already_read = []
xpath_dict = {
    "leads":
        "//a[@href='/leads/']",

    "overlay":
        "left-menu-overlay",

    "datetime":
        '//div[@class="feed-note__date"][1]',

    "purchases_main":
        "//div[1]/div/div/div/div/a[@class='pipeline_leads__title-text h-text-overflow js-navigate-link']",

    "purchases_partner":
        "//div[@class='pipeline-unsorted__item-from']",

    "content_main":
        "//div[@class='note--body--content-not-sliced__scroll-wrapper custom-scroll']/p",

    "content_partner":
        "//div[@class='feed-note__body']/p",

    "back":
        "//div[@class='js-back-button card-fields__top-back']"
}

reg_dict = {    
    "reg":          r"(?i)(?:\w*)?(?:вебхук|api|cайты24|php|разработать|help[ -]?desk|интернет[ -]?магазин|маркет|бесплатн|розничн(?:ая|ой|ые|ых|ую) торговл(?:е|я|и|ей|ю))(?:\w*)",

    "city":         r"(?i)(?:\w*)?(?:уфа|москва|санкт-петербург|новосибирск|самара|казань|екатеринбург|челябинск|нижний новгород|омск|самара|ростов-на-дону|красноярск|краснодар|пермь|воронеж|волгоград)(?:\w*)"
}

def match_log(matches):
    if matches:
        for match in matches:
            write_log("Match found: " + match)

def auth_data():   
    site = input("Введите сайт(без https://): ")
    set_auth_data('site','https://' + site)

    login = input("Введите логин: ")
    set_auth_data('login',login)

    password = getpass.getpass("Введите пароль: ")
    set_auth_data('password',password)

def get_auth_data(query):
    file = 'auth'
    with open(file, 'r') as file:
        for line in file:
            if query in line:
                tab_index = line.index('\t')
                return line[tab_index+1:].strip()

def set_auth_data(type,data):
    with open("auth", "a") as f:
        f.write(type + '\t' + data + "\n")

def write_log(message):
    date_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    data = date_time + ' ' + message
    print(data)
    with open("log", "a") as f:
        f.write(data + ' ' + "\n")

def reg_search(reg,query): return re.findall(reg, query)

def start():
    try:
        if not os.path.exists('auth'): auth_data()
        site = get_auth_data('site')
        login = get_auth_data('login')
        password = get_auth_data('password')
        
        if(site != '' and login != '' and password != ''):
            options = webdriver.ChromeOptions()
            prefs = {"profile.default_content_setting_values.notifications" : 2}
            options.add_experimental_option("prefs",prefs)
            # options.headless = True
            # изменить, если запуск не на windows               service=Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(executable_path=r'chromedriver',chrome_options=options)

            driver.get(site)
            driver.implicitly_wait(0.5)

            login_el = driver.find_element(by=By.ID, value="session_end_login")
            password_el = driver.find_element(by=By.ID, value="password")
            submit_button = driver.find_element(by=By.CLASS_NAME, value="auth_form__submit")

            login_el.send_keys(login)
            password_el.send_keys(password)

            
            submit_button.click()
            overlay_exist = True
            move_to_purchases(driver,overlay_exist)
        else: write_log('Данные не найдены')
    except WebDriverException as ex:
        write_log(ex.msg)
        start()

def datetime_result(driver):
    wait = WebDriverWait(driver,10)
    dt = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dict['datetime']))).get_attribute('innerHTML')
    if(len(dt) != 16):
        now = datetime.now()
        yesterday = datetime.now() - timedelta(days=1)
        today = re.findall("сегодня", dt, flags=re.IGNORECASE)
        time_str = dt.split(" ")[1]
        time_dt = datetime.strptime(time_str, '%H:%M:%S.%f')
        if today:
            return datetime(now.year, now.month, now.day, time_dt.hour, time_dt.minute, time_dt.second, time_dt.microsecond)
        else:
            return datetime(yesterday.year, yesterday.month, yesterday.day, time_dt.hour, time_dt.minute, time_dt.second, time_dt.fold)
    elif(dt is None): return None
    else: return datetime.strptime(dt, '%d.%m.%Y %H:%M:%S.%f')

def search(driver,type):
    wait = WebDriverWait(driver, 10)
    # FIXME: accept button
    cards = driver.find_elements(by=By.XPATH, value=xpath_dict['purchases_'+type])
    write_log('Всего карточек ' + str(len(cards)))      
    write_log(type.upper())
    for card in cards:                    
        wait.until(EC.element_to_be_clickable(card)).click()
        write_log("====================================")
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        result = datetime_result(driver)
        if(result is not None): diff = datetime.now() - result
        write_log("Прошло времени " + str(diff))
        back = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dict['back'])))
        if(result is not None and diff >= timedelta(minutes=15) and diff >= timedelta(milliseconds=15) and diff < timedelta(days=3)):
            time.sleep(3)
            elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_dict['content_'+type])))
            write_log("Количество строк в описании " + str(len(elements)))                    
            for x in elements:
                #Uncommit this for test
                # write_log(str(x.get_attribute('innerHTML')))
                content = x.get_attribute('innerHTML')
                reg = reg_search(reg_dict['reg'],content)
                city = reg_search(reg_dict['city'],content)
                match_log(reg)
                match_log(city)
                
                if(not reg and city):
                    # accept = driver.find_element(by=By.ID, value="card_unsorted_accept")
                    write_log('Найдено совпадение!')
                    # accept.click()     
        back.click()

def is_mouse_on_element(driver, xpath):
    elements = driver.find_element(By.XPATH,xpath)
    action = ActionChains(driver)
    for element in elements:
        action.move_to_element(element).perform()
        is_mouse_on_element = driver.execute_script('return document.elementFromPoint(arguments[0], arguments[1]) === arguments[2];', 0, 0, element)
        if is_mouse_on_element:
            return True
    return False
    

def move_to_purchases(driver,overlay_exist):
    wait = WebDriverWait(driver, 10)  
    try:        
        if(overlay_exist):
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dict['leads']))).click()
            element = wait.until(EC.visibility_of_element_located((By.ID, xpath_dict['overlay'])))                                           
            action = webdriver.ActionChains(driver)           
            action.move_to_element(element)
            action.perform()
            overlay_exist = True
        while True:
            search(driver,'partner')        
            search(driver,'main')
            # time.sleep(30)
        # driver.quit()
    
    except TimeoutException as ex:
        write_log(ex.screen)
        overlay_exist = False
        move_to_purchases(driver,overlay_exist)

if __name__ == '__main__':
    start()