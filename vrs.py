from selenium import webdriver
from dotenv import load_dotenv, find_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import json
import os
from shutil import move


def wait_and_click(xpath, wait_time=180):
    ActionChains(driver).move_to_element(WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH,
                                                                                                     xpath)))).click().perform()


def wait_till(xpath, wait_time=180):
    ActionChains(driver).move_to_element(WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath))))


def create_path(path):
    dirs = path.split('/')
    for d in dirs:
        path = ''
        for x in range(0, dirs.index(d) + 1):
            path += str(dirs[x]) + '/'
            if not os.path.exists(path):
                os.makedirs(path)


def load_name_data():
    if not os.path.exists(os.getcwd() + '\\data.txt'):
        pass
    with open(os.getcwd() + '\\data.txt') as json_file:
        try:
            return json.load(json_file)
        except:
            pass

def save_name_data(car_names):
    with open(os.getcwd() + '\\data.txt', 'w') as outfile:
        json.dump(car_names, outfile)


def enable_download_clickless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)


def load_chrome():
    capabilities = webdriver.DesiredCapabilities.CHROME
    chromeOptions = webdriver.ChromeOptions()
    prefs = {
        'profile.managed_default_content_settings.images': os.getenv(
        'chrome_settings_profile.managed_default_content_settings.images'),
        'download.prompt_for_download': os.getenv("chrome_settings_download.prompt_for_download"),
        'download.directory_upgrade': os.getenv('chrome_settings_download.directory_upgrade'),
        'safebrowsing.enabled': os.getenv('chrome_settings_safebrowsing.enabled'),
        'safebrowsing.disable_download_protection': os.getenv(
        'chrome_settings_safebrowsing.disable_download_protection'),
        'download.default_directory': os.getenv('chrome_settings_download.default_directory')
    }
    capabilities["pageLoadStrategy"] = "normal"
    chromeOptions.add_experimental_option("prefs", prefs)
    if(os.getenv('chrome_settings_headless') == 'True'):
        chromeOptions.add_argument("--headless")
    chromeOptions.add_argument('--no-sandbox')
    chromeOptions.add_argument("user-data-dir=" + str(os.getenv('chrome_profile')))  # Path to your chrome profile
    chromeOptions.add_argument('--disable-dev-shm-usage')
    chromeOptions.add_argument('log-level=' + str(os.getenv('chrome_settings_log-level')))
    driver = webdriver.Chrome(desired_capabilities=capabilities, chrome_options=chromeOptions)
    enable_download_clickless(driver, os.getenv('chrome_settings_download.default_directory'))
    return driver

def login_check():
    menu_first_item_xpath = '/html/body/div[1]/div/div/ul/ul/li[1]/div[1]/a/div/span[2]'
    wait_till(menu_first_item_xpath)
    return driver.find_element_by_xpath(menu_first_item_xpath).text[-13:-1] == 'Google login'

def google_login():
    print("Loading VRS home page: {}".format(base_url))
    driver.get(base_url)
    menu_xpath = '/html/body/div[1]/div/div/header/nav/div/a[1]'
    wait_till(menu_xpath) #simply wait till the page has loaded properly
    wait_and_click(menu_xpath)
    logged_in = login_check()
    wait_and_click(menu_xpath)
    if not logged_in:
        #google login url
        print("Logging in...")
        driver.get('https://virtualracingschool.appspot.com/openid_provider/googleplus?begin_login&return_to=https%3A%2F%2Fvirtualracingschool.appspot.com%2F%23%2FHome')
    else:
        print("Logged in")


def check_car_in_list(car_name_unformatted):
    if car_name_unformatted not in car_names:
        model_search_string = input("Enter Car Name For " + str(car_name_unformatted) + ": ")
        car_names[car_name_unformatted] = model_search_string
        save_name_data()
        load_name_data()


def get_series_count():
    driver.get(base_url + '/#/DataPacks')
    table_rows_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div/div[5]/div/div/div/div[1]/div[2]/table/tbody/tr'
    print("Loading data pack table")
    wait_till(table_rows_xpath)
    table_rows = driver.find_elements_by_xpath(table_rows_xpath)
    series_count = len(table_rows)
    print("Found " + str(series_count) + " series")
    return series_count


def get_series_details(series_id, series_in_table_xpath, series_count):
    driver.get(base_url + '/#/DataPacks')
    car_name_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div/div[5]/div/div/div/div[1]/div[2]/table/tbody/tr['+str(series_id)+']/td[2]/div/span[1]'
    season_tr_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div/div[5]/div/div/div/div[1]/div[2]/table/tbody/tr['+str(series_id)+']/td[3]/div/span/span'
    series_name_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div/div[5]/div/div/div/div[1]/div[2]/table/tbody/tr['+str(series_id)+']/td[1]/div/span[1]'
    wait_till(car_name_xpath)
    wait_till(season_tr_xpath)
    season = driver.find_element_by_xpath(season_tr_xpath).text
    car_name_unformatted = driver.find_element_by_xpath(car_name_xpath).get_attribute('innerHTML')
    series_name = driver.find_element_by_xpath(series_name_xpath).get_attribute('innerHTML') + str(car_name_unformatted)
    check_car_in_list(car_name_unformatted)
    car_name = car_names[car_name_unformatted]
    series = {}
    series['series_id'] = series_id
    series['xpath'] = series_in_table_xpath
    series['car_name'] = car_name
    series['season'] = season
    series['name']  = series_name
    print("[" + str(series_id) + "/" + str(series_count) + "] Loading info for " + str(car_name))
    enter_button_xpath = series_in_table_xpath + '/td[8]/a/span'
    wait_and_click(enter_button_xpath)
    time.sleep(1)
    series['url'] = str(driver.current_url)
    return series


def list_races_in_series(series_url):
    driver.get(series_url)
    try:
        show_previous_weeks_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div[4]/div/table/tbody/tr[1]/td/a'
        wait_and_click(show_previous_weeks_xpath, 3)
    except:
        pass


def get_series():
    series_count = get_series_count()
    start = 1
    series = []
    #check data.txt contains all cars in all series
    for series_id in range(start, series_count + 1):
        unformatted_car_name_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div/div[5]/div/div/div/div[1]/div[2]/table/tbody/tr['+str(series_id)+']/td[2]/div/span[1]'
        check_car_in_list(driver.find_element_by_xpath(unformatted_car_name_xpath).get_attribute('innerHTML'))

    #get series' details
    for series_id in range(start, series_count + 1):
        series_in_table_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div/div[5]/div/div/div/div[1]/div[2]/table/tbody/tr['+str(series_id)+']'
        series.append(get_series_details(series_id, series_in_table_xpath, series_count))

    return series


def get_races_count_in_series(series):
    list_races_in_series(series['url'])
    return int(driver.find_element_by_xpath('/html/body/div[1]/div/div/main/div[2]/div/div[3]/div/div[1]/div[2]/div/span[4]/span').text)


def download_setups(series):
    ok_path = '/html/body/div[7]/div/div/div[3]/a[2]' #t&c box
    file_list_li_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div[3]/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/ul/li'
    file_list_li = driver.find_elements_by_xpath(file_list_li_xpath)
    tries = 0
    while tries < 5:
        try:
            for i in range(1, len(file_list_li) + 1):
                file_xpath = file_list_li_xpath + '[' + str(i) +']/div/div/form/div/a'
                wait_till(file_xpath)
                file = driver.find_element_by_xpath(file_xpath)
                if file.text[-4:] == '.sto':
                    wait_and_click(file_xpath)
                    print("Downloading {}".format(file.text))
                    try:
                        wait_and_click(ok_path, 1)
                        wait_and_click(file_xpath)
                    except:
                        pass
                    try:
                        lap_time = file.find_element_by_xpath('../../../div').get_attribute('innerHTML')[11:-1].replace(":",
                                                                                                                        ".")
                    except:
                        lap_time = 'missing'
                    path = "{}/{}/{}/".format(series['car_name'], series['name'], series['season'])
                    create_path("{}/{}".format(destination_folder, path))
                    if(lap_time != 'missing'):
                        move(tmp + file.text,
                             str(destination_folder) + '/' + str(path) + str(file.text[:-4]) + '_BEST TIME_' + str(
                                 lap_time) + str(file.text[-4:]))
                    else:
                        move(tmp + file.text, str(destination_folder) + '/' + str(path) + str(file.text))
                tries = 5
        except:
                tries += 1


def get_races(series, all_series):
    race_count = get_races_count_in_series(series)
    print("["+str(series['series_id'])+"/"+str(len(all_series))+"] Found " + str(race_count) + " race(s) in " + str(series['name']))
    series['race_count'] = race_count
    loaded_races = 0
    for race_id in range(race_count, 0, -1):
        if(int(loaded_races) >= int(max_week)):
            break
        list_races_in_series(series['url'])
        race_enter_button_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div[4]/div/table/tbody/tr['+str(race_id)+']/td[7]/a/span'
        wait_and_click(race_enter_button_xpath)
        track_name_xpath = '/html/body/div[1]/div/div/main/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[1]/div/div[1]/div/span[2]/span'
        time.sleep(2)
        track_name = driver.find_element_by_xpath(track_name_xpath).get_attribute('innerHTML')
        print("[{}/{}] [{}/{}] Loading Car: {} | Track: {}".format(str(series['series_id']),str(len(all_series)),str(race_id),str(race_count),series['car_name'], track_name))
        download_setups(series)

    return series


def main():
    global driver, base_url, car_names, max_week, destination_folder, tmp
    load_dotenv(find_dotenv())
    destination_folder = os.getenv('destination_folder')
    tmp = os.getenv('chrome_settings_download.default_directory') + '\\'
    max_week = os.getenv('max_week')
    base_url = 'https://virtualracingschool.appspot.com'
    car_names = load_name_data()
    driver = load_chrome()
    google_login()
    series = get_series()
    for s in series:
        get_races(s, series)


if __name__ == "__main__":
    main()
