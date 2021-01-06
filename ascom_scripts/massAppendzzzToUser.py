import pandas as pd
import time
import csv
import re
import logging
import sys
import getopt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import configparser


def getUserName(driver):
    print(
        "Person's name: ",
        driver.find_element_by_css_selector(
            ".table-form > tbody:nth-child(3) > tr:nth-child(2) > td:nth-child(2) > input:nth-child(1)"
        ).get_attribute("value"),
    )
    # Get user name from web
    userName = driver.find_element_by_css_selector(
        ".table-form > tbody:nth-child(3) > tr:nth-child(2) > td:nth-child(2) > input:nth-child(1)"
    ).get_attribute("value")
    return userName


def changeUserName(driver, user):
    # Clear current name from field.
    # print(user)
    try:
        driver.find_element_by_css_selector(
            ".table-form > tbody:nth-child(3) > tr:nth-child(2) > td:nth-child(2) > input:nth-child(1)"
        ).clear()
        # Get user name from web
        driver.find_element_by_css_selector(
            ".table-form > tbody:nth-child(3) > tr:nth-child(2) > td:nth-child(2) > input:nth-child(1)"
        ).send_keys(user)
        return True
    except:
        return False


def check_user(driver, row, **options):

    # Select All Hospitals in Hospital drop down.
    driver.find_element_by_xpath("/html/body/div[4]/div[2]/form/table/tbody/tr/td[2]/select/option[1]").click()
    # time.sleep(1)
    # driver.find_element_by_css_selector('#menu > li:nth-child(3) > ul > li:nth-child(1) > a').click()
    # Select search box and clear contents
    driver.find_element_by_css_selector("#selectHospitalForm > table > tbody > tr > td:nth-child(2) > input.short").clear()
    # time.sleep(1)
    # Enter text into search box
    driver.find_element_by_css_selector("#selectHospitalForm > table > tbody > tr > td:nth-child(2) > input.short").send_keys(row['Username'])
    # time.sleep(1)
    # Click search
    driver.find_element_by_xpath("/html/body/div[4]/div[2]/form/table/tbody/tr/td[2]/input[2]").click()
    # time.sleep(1)
    # Clicked edit button for user
    # try:
    driver.find_element_by_css_selector(".purple").click()
    results = changeUserName(driver=driver, user=row['NewFullName'])
    time.sleep(0.5)
    
    # click Cancel
    # driver.find_element_by_xpath("/html/body/div[4]/div[2]/form/input[6]").click()
    
    # Click Apply
    driver.find_element_by_css_selector("body > div.content > div:nth-child(2) > form > input.button.purple").click()


def main(argv):
    clearSess = False
    user = None

    settings_files = "bot_config.ini"
    # path = 'test_file.xls'
    settings = configparser.ConfigParser()
    settings.read(settings_files)
    # settings.get('userinfo','user')

    url = settings.get("ascom", "unitecontext")
    update = False
    hospitalDict = settings._sections["hospitals"]

    chrome_options = Options()
    chrome_options.add_argument('ignore-certificate-errors')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    time.sleep(1)
    driver.find_element_by_id("j_username").send_keys(settings.get("userinfo", "user"))
    driver.find_element_by_id("j_password").send_keys(settings.get("userinfo", "password"))
    driver.find_element_by_xpath('//*[@id="loginForm"]/table/tbody/tr[2]/td/p/input').click()
    driver.get(url + settings.get("ascom", "userUrl"))
    time.sleep(1)

    df = pd.read_csv('csvs/AscomInactiveUsersChanged_202011241516.csv')
    # print(df)
    df['NewFullName'] = "zzz" + df['User Full Name']
    # df['Processed'] = False
    dflength = df.shape[0]
    try:
        for index, row in df.iterrows():
            if row['Processed'] is True:
                pass
            else:
                print("{} of {} - Changing {} to {}".format(index, dflength, row['User Full Name'],row['NewFullName']))
                check_user(driver=driver, row=row)
                # driver.get(url + settings.get("ascom", "userUrl"))
                df.at[index, 'Processed'] = True
    except:
        pass
    driver.close()
    driver.quit()
    timestr = time.strftime("%Y%m%d%H%M")
    file_name = "csvs/AscomInactiveUsersChanged_{}.csv".format(timestr)
    df.to_csv(file_name, encoding='utf-8', index=False)

if __name__ == "__main__":
    startTime = time.time()
    main(sys.argv[1:])
    print ('Changes took {0} seconds.'.format(time.time() - startTime))
