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


def getlogs(driver, row):

    # Clear, then Set start Date
    driver.find_element_by_xpath('//*[@id="_START_DATE_"]').clear()
    driver.find_element_by_xpath('//*[@id="_START_DATE_"]').send_keys("6/21/2018")

    # Set end Date
    driver.find_element_by_xpath('//*[@id="_END_DATE_"]').clear()
    driver.find_element_by_xpath('//*[@id="_END_DATE_"]').send_keys("8/01/2018")

    # Enter Username
    driver.find_element_by_xpath('//*[@id="_USERNAME_"]').clear()
    driver.find_element_by_xpath('//*[@id="_USERNAME_"]').send_keys(row[0])

    # Click search
    driver.find_element_by_xpath(
        "/html/body/div[4]/div[2]/form/table/tbody/tr/td[9]/input"
    ).click()

    # Build Call history report url for a user
    reportUrlStub = "https://server-fqdn:8443/heartbeat/SimpleReports.action?viewReport=Search&reportId=85&__fp=IaSCVcUPUECuBNhrZ6aqqSpkY7q-FlgWwpGLay_gsQY%3D&paramValuesMap[%27$END_DATE$%27]=08%2F01%2F2018&paramValuesMap[%27$START_DATE$%27]=06%2F27%2F2018&paramValuesMap[%27$USER_NUMBER$%27]=&selectedCategory.categoryId=1&_sourcePage=uUkp6S7Doo6Dzs8lacM1xSCK00he4fm3qITGlBIlRjLadHpkbuQNvaO24tD0KyJR&d-49653-e=2&paramValuesMap[%27$OTHER_PARTY_NAME$%27]=&paramValuesMap[%27$OTHER_PARTY_NUMBER$%27]=&selectedHospitalId=0&paramValuesMap[%27$USERNAME$%27]=USERTARGET&6578706f7274=1&paramValuesMap[%27$ROLE_NAME$%27]="
    # print("URL: {}".format(reportUrlStub.replace("USERTARGET", row[0])))
    # Try to dowload call history report for user.
    try:
        # driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[2]/a").click()
        driver.get(reportUrlStub.replace("USERTARGET", row[0]))
    except:
        e = sys.exc_info()[0]
        print("ERROR: {}".format)

    time.sleep(1)
    # Check if exists:
    # /html/body/div[4]/div[2]/div[2]/a


def main(argv):
    clearSess = False
    user = None

    try:
        opts, args = getopt.getopt(argv, "hi:")
        print("opts", opts)
        print("args", args)
    except getopt.GetoptError:
        print("Error: ", opts, args)
        sys.exit(2)

    if len(args) == 1 and not opts:
        print("Process individual files")
    else:
        for opt, arg in opts:
            print("Len(arg): ", len(arg))
            if opt in ("-", ""):
                print("-h if: ", opt, arg)
                print("HELP!")
            elif opt in ("-i", ""):
                print("-i if: ", opt, arg)
                inputFile = arg
            else:
                assert False, "Unknown option"

    settings_files = "bot_config.ini"
    # path = 'test_file.xls'
    settings = configparser.ConfigParser()
    settings.read(settings_files)
    # settings.get('userinfo','user')
    # user = 'cnspge'
    # user = "clnxjs"
    # user = "ascom7"
    # user = "Rachel Wax"
    # downloadDir =  settings.get('ascom','downloadDir')
    url = settings.get("ascom", "unitecontext")
    callHistoryUrl = "https://server-fqdn:8443/heartbeat/SimpleReports.action?viewReport=&reportId=85&selectedCategory.categoryId=1"
    update = False
    hospitalDict = settings._sections["hospitals"]
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # enable_download_in_headless_chrome(None, driver, downloadDir)
    driver.get(url)
    # Login
    driver.find_element_by_id("j_username").send_keys(settings.get("userinfo", "user"))
    driver.find_element_by_id("j_password").send_keys(
        settings.get("userinfo", "password")
    )
    driver.find_element_by_xpath(
        '//*[@id="loginForm"]/table/tbody/tr[2]/td/p/input'
    ).click()
    # driver.get(url + settings.get("ascom", "userUrl"))
    driver.get(callHistoryUrl)
    # check_user(driver, user, hospitals=hospitalDict)
    # check_user(driver, user, cleardevice=True)

    readCsv = open(inputFile)
    csvFile = csv.reader(readCsv)
    url = ""
    for i, row in enumerate(csvFile):
        print(row[0])
        if not i == 0:
            # getlogs(driver, row)
            urls = [
                "https://server-fqdn:8443/heartbeat/SimpleReports.action?viewReport=Search&reportId=85&__fp=IaSCVcUPUECuBNhrZ6aqqSpkY7q-FlgWwpGLay_gsQY%3D&paramValuesMap[%27$END_DATE$%27]=08%2F01%2F2018&paramValuesMap[%27$START_DATE$%27]=06%2F27%2F2018&paramValuesMap[%27$USER_NUMBER$%27]=&selectedCategory.categoryId=1&_sourcePage=uUkp6S7Doo6Dzs8lacM1xSCK00he4fm3qITGlBIlRjLadHpkbuQNvaO24tD0KyJR&d-49653-e=2&paramValuesMap[%27$OTHER_PARTY_NAME$%27]=&paramValuesMap[%27$OTHER_PARTY_NUMBER$%27]=&selectedHospitalId=0&paramValuesMap[%27$USERNAME$%27]=USERTARGET&6578706f7274=1&paramValuesMap[%27$ROLE_NAME$%27]=",
                "https://server-fqdn:8443/heartbeat/SimpleReports.action?viewReport=Search&reportId=118&__fp=QVMc7go0RjiuBNhrZ6aqqSpkY7q-FlgWwpGLay_gsQY%3D&paramValuesMap[%27$END_DATE$%27]=8%2F1%2F2018&paramValuesMap[%27$SENDROLE$%27]=&paramValuesMap[%27$START_DATE$%27]=06%2F27%2F2018&selectedCategory.categoryId=1&_sourcePage=lq1rfyr7Nf2Dzs8lacM1xSCK00he4fm3qITGlBIlRjLadHpkbuQNvaO24tD0KyJR&d-49653-e=2&paramValuesMap[%27$RECUSERNAME$%27]=&selectedHospitalId=0&paramValuesMap[%27$RECROLE$%27]=&paramValuesMap[%27$RECUSER$%27]=&6578706f7274=1&paramValuesMap[%27$SENDUSER$%27]=USERTARGET",
            ]
            try:
                # driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[2]/a").click()
                [driver.get(url.replace("USERTARGET", row[0])) for url in urls]
                # driver.get(reportUrlStub.replace("USERTARGET", row[0]))
            except:
                e = sys.exc_info()[0]
                print("ERROR: {}".format)

    # if driver.find_element_by_class_name('pagebanner').text:
    #     print(driver.find_element_by_class_name('pagebanner').text)
    # driver.get_screenshot_as_file("capture.png")

    driver.close()
    driver.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
