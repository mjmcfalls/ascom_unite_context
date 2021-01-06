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


def checkPersonalDevice(driver):
    # Check personal/shared device
    try:
        if driver.find_elements_by_css_selector(
            "body > div.content > div:nth-child(2) > form > table > tbody > tr:nth-child(31) > td:nth-child(2) > label"
        ):
            # print("Shared Device -- Nothing to do")
            pass
    except:
        pass
    try:
        if driver.find_elements_by_css_selector(
            "body > div.content > div:nth-child(2) > form > table > tbody > tr:nth-child(31) > td:nth-child(2) > input"
        ):
            print("Clearing Personal Device")
            # Disabled during testing
            # driver.find_element_by_css_selector('body > div.content > div:nth-child(2) > form > table > tbody > tr:nth-child(31) > td:nth-child(2) > span > input.button.tiny.red').click()
            return True
    except:
        pass
    return False


def clearPersonalDevice(driver):
    # Disabled during testing
    driver.find_element_by_css_selector(
        "body > div.content > div:nth-child(2) > form > table > tbody > tr:nth-child(31) > td:nth-child(2) > span > input.button.tiny.red"
    ).click()

    driver.switch_to.alert.accept()
    # driver.accept()


def clearAuthSessions(driver, authSessions):
    if authSessions:
        for session in authSessions:
            clearSession(driver, session)


def clearSession(driver, authsession):
    currentUrl = driver.current_url
    print("Clearing session ", authsession)
    driver.get(authsession)
    driver.get(currentUrl)


def getauthSessionUrls(driver, authTokensTable):
    tempSessions = []

    for row in authTokensTable.find_elements_by_tag_name("tr"):
        for link in row.find_elements_by_css_selector("a"):
            tempSessions.append(link.get_attribute("href"))
    return tempSessions


def enable_download_in_headless_chrome(self, driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )

    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_dir},
    }
    command_result = driver.execute("send_command", params)


def checkRole(driver, targetRole):
    select = Select(
        driver.find_element_by_css_selector(
            "body > div.content > div:nth-child(2) > form > table > tbody > tr:nth-child(3) > td:nth-child(2) > select"
        )
    )
    currentRole = select.first_selected_option.get_attribute("value")
    print("Current role: ", currentRole, "Target role: ", targetRole)
    if not targetRole == currentRole:
        select.select_by_value(targetRole)
        print("Changed %s to %s" % (currentRole, targetRole))
        return True
    else:
        return False


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
    clearDevice = False
    update = []
    authSessions = []
    newUser = False
    personalDevice = False
    newRole = False
    targetRole = ""
    # Check for optional options
    if options.get("hospitals") and options.get("hospitalaccess"):
        hospitalDict = options.get("hospitals")
        addHospitals = options.get("hospitalaccess")
        # print(hospitalDict)
    else:
        hospitalDict = []

    if options.get("cleardevice"):
        clearDevice = True
    else:
        clearDevice = False

    if options.get("newname"):
        newName = options.get("newname")
    else:
        newName = False

    if options.get("newrole"):
        targetRole = options.get("newrole")
    else:
        targetRole = False

    if options.get("clearsessions"):
        clearSessions = options.get("clearsessions")
    else:
        clearSessions = False

    # Select All Hospitals in Hospital drop down.
    driver.find_element_by_xpath(
        "/html/body/div[4]/div[2]/form/table/tbody/tr/td[2]/select/option[1]"
    ).click()
    # driver.find_element_by_css_selector('#menu > li:nth-child(3) > ul > li:nth-child(1) > a').click()
    # Select search box and clear contents
    driver.find_element_by_css_selector(
        "#selectHospitalForm > table > tbody > tr > td:nth-child(2) > input.short"
    ).clear()
    # Enter text into search box
    driver.find_element_by_css_selector(
        "#selectHospitalForm > table > tbody > tr > td:nth-child(2) > input.short"
    ).send_keys(row[0])
    # Click search
    driver.find_element_by_xpath(
        "/html/body/div[4]/div[2]/form/table/tbody/tr/td[2]/input[2]"
    ).click()
    # Clicked edit button for user
    # try:
    driver.find_element_by_css_selector(".purple").click()
    userName = getUserName(driver)
    # # Check if new user:
    # # Is New user check box (checked): .table-form > tbody:nth-child(3) > tr:nth-child(4) > td:nth-child(2) > input:nth-child(1)
    # if driver.find_element_by_css_selector('.table-form > tbody:nth-child(3) > tr:nth-child(4) > td:nth-child(2) > input:nth-child(1)').is_selected():
    #     print("New User == True")
    #     newUser = True
    
    # time.sleep(2)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Need to pass hospital access and convert to function to verify hospital access
    print("Checking hospital settings")
    # hospitals = driver.find_elements_by_css_selector(
    #     "body > div.content > div:nth-child(2) > form > table > tbody > tr:nth-child(29) > td:nth-child(2) > input[type='checkbox']"
    # )
    # time.sleep(1)
    checkboxes = driver.find_elements_by_css_selector('input[type="checkbox"]')
    # print(checkboxes)
    for i, checkbox in enumerate(checkboxes):
        # print(
        #     checkbox.id,
        #     checkbox.tag_name,
        #     checkbox.text,
        #     checkbox.get_property("value"),
        # )
        # print("Checkbox: {}".format(checkbox))
        if checkbox.get_property("value") in hospitalDict:
            # print(
            #     "i: {}; get_property: {}; dictValue: {}; selected: {}".format(
            #         i,
            #         checkbox.get_property("value"),
            #         hospitalDict[checkbox.get_property("value")],
            #         checkbox.is_selected(),
            #     )
            # )
            # if 46 == hospitalDict[checkbox.get_property("value")]:
            if (
                # "46" == checkbox.get_property("value") or 
                # "47" == checkbox.get_property("value") or  
                # "48" == checkbox.get_property("value") or 
                # "45" == checkbox.get_property("value") or 
                # "49" == checkbox.get_property("value") or 
                # "46" == checkbox.get_property("value") or 
                "7" == checkbox.get_property("value") # or 
                # "2" == checkbox.get_property("value")
            ):
                if not checkbox.is_selected():
                    try:
                        checkbox.click()
                        # print(
                        #     "Clicked %s"
                        #     % (hospitalDict[checkbox.get_property("value")])
                        # )
                    except:
                        pass
                        # print(
                        #     "Could not click: %s"
                        #     % (hospitalDict[checkbox.get_property("value")])
                        # )
                        # print("Disabled: {}".format(checkbox.get_property("value")))
                else:
                    pass
                    # print("Checked: {}".format(checkbox.get_property("value")))
            else:
                pass
                # print("Checkbox does not match hospital")
    # time.sleep(1)
    # driver.find_elebody > div.content > div:nth-child(2) > form > input.button.purple
    driver.find_element_by_css_selector("body > div.content > div:nth-child(2) > form > input.button.purple").click()
    # driver.find_element_by_xpath("/html/body/div[4]/div[2]/form/input[5]").click()
    # except:
    #     print("Could not process: {}".format(row[2]))
    #     time.sleep(5)


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
    settings = configparser.ConfigParser()
    settings.read(settings_files)
    # settings.get('userinfo','user')
    # downloadDir =  settings.get('ascom','downloadDir')
    url = settings.get("ascom", "unitecontext")
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
    driver.get(url + settings.get("ascom", "userUrl"))
    # check_user(driver, user, hospitals=hospitalDict)
    # check_user(driver, user, cleardevice=True)

    readCsv = open(inputFile)
    csvFile = csv.reader(readCsv)

    for i, row in enumerate(csvFile):
        # print(row[2])
        if not i == 0:
            check_user(driver, row, hospitals=hospitalDict, hospitalaccess=["All"])

    # if driver.find_element_by_class_name('pagebanner').text:
    #     print(driver.find_element_by_class_name('pagebanner').text)
    # driver.get_screenshot_as_file("capture.png")

    # driver.close()
    # driver.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
