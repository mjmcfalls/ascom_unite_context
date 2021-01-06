import pandas as pd
import time
import csv
import re
import logging
import sys
import getopt
import requests
import configparser
from datetime import datetime
import pytz
from pytz import timezone
import io

loginUri = "https://server-fqdn:8443/heartbeat/Login.action"
payload = {"j_username": None, "j_password": None}
settings_files = "bot_config.ini"
eastern = timezone('US/Eastern')

urls = [         
        # Text message content Format: 04%2F20%2F2020 
        # Target STARTDATE/ENDDATE
        "https://server-fqdn:8443/heartbeat/SimpleReports.action?viewReport=Search&reportId=118&paramValuesMap[%27$CHAT_TYPE$%27]=&__fp=Lg5crTyWSeEKVNLpdQGrAmJg0JBGNDeFK19i-Da2YPA%3D&paramValuesMap[%27$END_DATE$%27]=ENDDATE&paramValuesMap[%27$SENDROLE$%27]=&paramValuesMap[%27$START_DATE$%27]=STARTDATE&selectedCategory.categoryId=1&paramValuesMap[%27$GROUP_CHAT_NAME$%27]=&_sourcePage=R4lO9tJXC4azrpX1MNCgrN5oZOL_g8yydldbleEYhwzriyQ27UmbPCx6XzzvNPOV&d-8003912-e=2&selectedHospitalId=0&paramValuesMap[%27$RECROLE$%27]=&paramValuesMap[%27$RECUSER$%27]=&6578706f7274=1&paramValuesMap[%27$SENDUSER$%27]="
    ]
def main(argv):
    urlDate = datetime.now(tz=eastern)
    furlDate = urlDate.strftime("%m&%d&%Y")
    print('EST Time =', datetime.now(tz=eastern))

    settings = configparser.ConfigParser()
    settings.read(settings_files)
    userinfo = settings._sections["userinfo"]
    payload['j_username'] = userinfo['user']
    payload['j_password'] = userinfo['password']

    with requests.Session() as session:
            post = session.post(loginUri, data=payload, verify=False)
            # print(post.headers)
            dateUrl = re.sub("STARTDATE", furlDate, re.sub("ENDATE", furlDate, urls[0]))
            # print(dateUrl)
            ffile = session.get(dateUrl, verify=False, stream=False)
            print(ffile.text)
            # print(io.StringIO(ffile.text))
            c=pd.read_csv(io.StringIO(ffile.text), sep = "\t")
            print(c)
    requests.session().close()


if __name__ == "__main__":
    main(sys.argv[1:])
