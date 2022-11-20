import pandas as pd
import numpy as np
import sqlite3 
import json
import time
import math
import requests
import shutil
import tarfile
import gzip
import os
import tempfile
import copy
from datetime import datetime
import io
import smtplib
import pendulum
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
# from email.message import Message
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from pathlib import Path


loginUri = "https://AscomServer/phpgui/login.php"
backupUri = "https://AscomServer/cgi-bin/admin/getbackup"
payload = {"username": "", "password": ""}

timestamp = pendulum.now('America/New_York')
filename = "{}_unite_communication_server-1.5.0-backup".format(timestamp.strftime("%Y%m%d%H%M%S"))
downloadDir = "/download/src/"

compliancecsv = '/download/export/AscomComplianceReport_{}.csv'.format(timestamp.strftime("%Y%m%d%H%M%S"))
exportcsv  = '/download/export/AscomMasterExport_{}.csv'.format(timestamp.strftime("%Y%m%d%H%M%S"))
sender_email = "From Display Name <from@email.address>"
receiver_email = "to@email.address"
smtpserver = 'smtp-server'
suffix = {
    "gzip_suffix" : ".gzip",
    "tar_suffix" : ".tar"
}

days = 7
applist = []
configList = []
output = []
paramDf = None
settingsDf = None
envFile = '/download/env/env.json'

apps = {
    "Setup":9789406192110951353,
    # "Phone": [9064338438475630123, 0],
    "Clock": 801385939761217464,
    "PTT": 7564195215672340879,
    "Browser": 7255832417732727760,
    "Personal security": 642520829192444339,
    "Settings": 6298294726772882576,
    "My Services": 5723203182465076767,
    "Search": 5710978759458982735,
    "Music": 4870472282655128632, 
    "Calculator": 4564190426170815308,
    "Unite Context": 2574888104202849261,
    "Gallery": 17845401502286784743,
    "Calendar": 17612716204027717987,
    "Settings": 17479598783108620629,
    "Voice Dialer": 17479563495707360577,
    "Email": 17042426002025490876,
    "Myco Launcher": 15007109137499193373,
    "Camera": 14119271812612341795,
    "Contacts": 12804620013844685252,
    "Sound Recorder": 10836854091630595316,
    "Downloads": 10394030973875740092,
    }

configs = {
    "ntp": "com.ascom.settingssyncmgr/settings/ntp_address",
    "pbx": "com.ascom.phonesip/default/pbx",
    "pbx_secondary": "com.ascom.phonesip/default/pbx_secondary",
    "cm.address": "com.ascom.uniteservice/unite/cm.address",
    "logout_when docked": "com.ascom.uniteservice/unite/logout_user_when_docked",
    "wifi_freq_band": "com.ascom.settingssyncmgr/network/wifi_freq_band",
    "admin_password": "com.android.settings/settings/admin_password",
    "time_zone": "com.ascom.settingssyncmgr/settings/time_zone",
    "80211N":"com.ascom.settingssyncmgr/network/wifi_80211n_enabled"
}
columns = [
    "Phone",
    "Setup",
    "Clock",
    "PTT",
    "Browser",
    "Personal security",
    "Settings",
    "My Services",
    "Search",
    "Music",
    "Calculator",
    "Unite Context",
    "Gallery",
    "Calendar",
    "Settings",
    "Voice Dialer",
    "Email",
    "Myco Launcher",
    "Camera",
    "Contacts",
    "Sound Recorder",
    "Downloads",
    "ntp",
    "pbx",
    "pbx_secondary",
    "cm.address",
    "logout_when docked",
    "wifi_freq_band",
    "admin_password",
    "time_zone",
    "FirmwareVersion",
    "SerialNumber",
    "IPAddress",
]

apps_dict = {
    "Setup": 1,
    "Clock": 1,
    "PTT": 0,
    "Browser": 0,
    "Personal security": 0,
    "Settings": 1,
    "My Services": 0,
    "Search": 0,
    "Music": 0,
    "Calculator": 1,
    "Unite Context": 0,
    "Gallery": 0,
    "Calendar": 0,
    "Voice Dialer": 0,
    "Email": 0,
    "Myco Launcher": 0,
    "Camera": 0,
    "Contacts": 0,
    "Sound Recorder": 0,
    "Downloads": 0,
}

settings_dict = {
    "FirmwareVersion":'14.3.0',
    "ntp": "172.26.60.80",
    "pbx": "172.26.60.183",
    "pbx_secondary": "172.26.60.184",
    "cm.address": "172.26.60.115",
    "logout_when docked": 1,
    "wifi_freq_band": None,
    "admin_password": "bWhzYWRtaW4h",
    "time_zone": "America/New_York",
    "80211N": 0
}
current_epoch = time.mktime(datetime.now().timetuple())


def downloadfile(downloadDir, filename, suffix):
    local_filename = Path(downloadDir, filename).with_suffix(suffix["gzip_suffix"])
    # print("DownloadFile: {}".format(local_filename))
    # print(loginUri)
    with tempfile.TemporaryDirectory() as tmpdir:
        with requests.Session() as session:
            post = session.post(loginUri, data=payload, verify=False)
            with session.get(backupUri, verify=False, stream=True) as r:
                with open(Path(tmpdir,filename).with_suffix(suffix["gzip_suffix"]), "wb") as f:
                    shutil.copyfileobj(r.raw, f)

                with gzip.open(Path(tmpdir,filename).with_suffix(suffix["gzip_suffix"]), 'rb') as gz:
                    content = gz.read()

                    with open(Path(tmpdir,filename).with_suffix(suffix["tar_suffix"]), 'wb') as f:
                        f.write(content)

                    tar = tarfile.open(Path(tmpdir,filename).with_suffix(suffix["tar_suffix"]), mode='r')
                    def is_within_directory(directory, target):
                        
                        abs_directory = os.path.abspath(directory)
                        abs_target = os.path.abspath(target)
                    
                        prefix = os.path.commonprefix([abs_directory, abs_target])
                        
                        return prefix == abs_directory
                    
                    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                    
                        for member in tar.getmembers():
                            member_path = os.path.join(path, member.name)
                            if not is_within_directory(path, member_path):
                                raise Exception("Attempted Path Traversal in Tar File")
                    
                        tar.extractall(path, members, numeric_owner=numeric_owner) 
                        
                    
                    safe_extract(tar, path=Path(downloadDir,filename))
          
        requests.session().close()
        return filename

def getPhones(applist, configList, timestamp, exportcsv, compliancecsv, database):
    
    print(database)
    query = "Select CurrentCallNo, tDevices.Description, tPortables.UnitId, tDevices.FirmwareVersion, SerialNumber, IPAddress, LoginTime, tListParameters.Key, tListParameters.Value, ListIndex, tPortables.DeviceType FROM tDevices INNER JOIN tPortables ON tPortables.UnitID = tDevices.UnitID INNER JOIN tListParameters ON tListParameters.PortableId = tPortables.Id WHERE tListParameters.Value = 0 OR tListParameters.Value = 1;"
    settingsQuery = "Select Key, Value, tPortables.CallNo FROM tParameters227 INNER JOIN tPortables ON tPortables.Id = tParameters227.PortableId"

    conn = sqlite3.connect(database)

    global paramDf
    global settingsDf

    paramDf = pd.read_sql_query(query, conn)
    settingsDf = pd.read_sql_query(settingsQuery, conn)

    phones = np.sort(paramDf.CurrentCallNo.unique())
    # phones = phones[500:600]
    print("Number of phones: {}".format(len(phones)))
    for p in phones:
        applist.append(apps)
        configList.append(configs)

    r = list(map(lambda x, apps, configs: processPhone(x, apps, configs), phones, applist, configList))
    
    tdf = pd.DataFrame.from_dict(r)

    tdf["Settings_Compliance"] = "Yes"
    tdf["Network_Compliance"] = "Yes"
    tdf['80211N_Compliance'] = "Yes"
    tdf['Firmware_Compliance'] = "Yes"

    for index, row in tdf.iterrows():
        # print(row)
        if row['Description'].lower().startswith("test"):
            # print("starts with test")
            pass
        else:
            # print(row['Phone'])
            for k,v in apps_dict.items():
                if str(row[k]) == str(v):
                    pass
                else:
                    tdf.at[index, "Settings_Compliance"] = "No"

            # Settings
            for k,v in settings_dict.items():
                if k == "wifi_freq_band":
                    if row['Description'].lower().startswith("matchstring1") or row['Description'].lower().startswith("matchstring2") or row['Description'].lower().startswith("matchstring3") or row['Description'].lower().startswith('matchstring4'):
                        if str(row[k]) == "1":
                            pass
                        elif str(row[k]) != "1":
                            # print("not equal 1")
                            tdf.at[index, "Network_Compliance"] = "No"

                    elif str(row[k]) != "2":
                        tdf.at[index, "Network_Compliance"] = "No"

                elif k == "80211N":
                    if str(row[k]) == str(v):
                        pass
                    else:
                        tdf.at[index, "80211N_Compliance"] = "No"

                elif k == "FirmwareVersion":
                    if str(row[k]) == str(v):
                        pass
                    else:
                        tdf.at[index, "Firmware_Compliance"] = "No"
                        
                else:
                    if str(row[k]) == str(v):
                        pass
                    else:
                        tdf.at[index, "Settings_Compliance"] = "No"
                        
    daysDf = tdf[(tdf['DaysLastSeen'] <= days)]

    daysDf['Facility'] = daysDf['Description'].str.split(" ").str[0]
    freqDf = daysDf.groupby('Facility')['Facility'].count()
    print(freqDf)

    comDf = daysDf.loc[(daysDf['Settings_Compliance'] == "No") | (daysDf['Network_Compliance'] == "No") | (daysDf['80211N_Compliance'] == "No") | (daysDf['Firmware_Compliance'] == "No")]

    comDf['wifi_freq_band'] = comDf['wifi_freq_band'].apply({'1':"5 GHz", '2': "2.4 GHz"}.get)
    comDf['80211N'] = comDf['80211N'].apply({'0':"Disabled", '1': "Enabled"}.get)
    
    comDf['80211N'].replace(to_replace=[None], value="Enabled", inplace=True)
    comDf[["Phone","Description","DaysLastSeen","Settings_Compliance","Network_Compliance","80211N_Compliance","Firmware_Compliance","macaddress","SerialNumber","FirmwareVersion","wifi_freq_band","80211N"]].to_csv(compliancecsv, index=False)

    tdf.to_csv(exportcsv, index=False)

    return comDf[["Phone","Description","DaysLastSeen","Network_Compliance","wifi_freq_band","80211N_Compliance","80211N","Firmware_Compliance","FirmwareVersion","Settings_Compliance","macaddress","SerialNumber"]], freqDf


def processPhone(phone, apps, configs):
    # print(phone)
    settings = {}
    
    settings["Phone"] = phone
    fields = {"UnitID": "macaddress", "SerialNumber":"SerialNumber", "LoginTime":"LoginTime", "FirmwareVersion":"FirmwareVersion", "Description":"Description"
    }
    for(k,v) in fields.items():
        results = paramDf.query("CurrentCallNo == '{}'".format(phone))
        settings[v] = results[k].iloc[0]

    settings['DaysLastSeen'] = math.ceil((current_epoch - settings['LoginTime'])/86400)

    for key, value in apps.items():
        appsQuery = "ListIndex == '{}' & CurrentCallNo == '{}' & Key == 'com.ascom.medicview/apps-list/apps.visibility'".format(value ,phone)
        temp_df = paramDf.query(appsQuery)
        if temp_df.empty:
            pass
        else:   
            settings[key] = temp_df["Value"].values[0]
    
    for key, value in configs.items():
        settingsQuery = "CallNo == '{}' & Key == '{}'".format(phone, value)
        temp_df = settingsDf.query(settingsQuery)
        # print(temp_df)
        if temp_df.empty:
            pass
        else:
            # print("{}, {}".format(key,temp_df["Value"].values[0] ))
            settings[key] = temp_df["Value"].values[0]
        # settingsDict =  {k:getValues(k, v, phone, appsQuery) for (k, v) in apps.items()}
        # settings = { **settings, **settingsDict}
    # print(settings)
    # tdict['macaddress'] = 

    # rdict = { **tdict, **items}
    return settings
    # return rdict 

def sendemail(df, timestamp, days, summaryDf, receiver_email):
    phoneCount = len(df.index)
    print("Non-compliant phones: {}".format(phoneCount))
    str_io = io.StringIO()
    summary_io = io.StringIO()

    pd.DataFrame(summaryDf.rename_axis('Facility'), columns=['Active Phones at Facility']).to_html(buf=summary_io, classes='table table-striped', index=False)
    df.to_html(buf=str_io, classes='table table-striped', index=False)

    html_str = str_io.getvalue()
    summary_html = summary_io.getvalue()
    # print(html_str)

    # msg = MIMEMultipart()
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_email)
    msg['Subject'] = "[REPORT] - Ascom Myco Settings Compliance Report from {}".format(timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    # message = '<style>table { border-collapse: collapse; border-spacing: 0; width: 100%; border: 1px solid #ddd; } th, td { text-align: left; padding: 16px; } tr:nth-child(even) { background-color: #f2f2f2; }</style> '
    message = "<p>Ascom Myco Settings Compliance Report from {}</p><p>Total non-compliant phones seen in the last {} days: {}</p><p>Remediation guide:<ul><li>Firmware: Upgrade/downgrade to appropriate version</li><li>Settings: Apply 2-MHS_Baseline templates</li><li>802.11N: Apply appropriate network template to phone</li><li>Network: Apply appropriate network template to phone (Please make sure to select the appropriate Wifi band for your site!)</li><li>Blank description: Update the device description in Device Manager</li></ul></p><p>Note: Network compliance is determined based on the description.  Please make sure new/replacement devices have the correct descriptions</p>".format(timestamp.strftime("%Y-%m-%d %H:%M:%S"), days, phoneCount)
    summarymsg = "<p>Total Number of active phones in the last 7 days:</p>"
    message = message + html_str# + summarymsg + summary_html
    # print(message) 

    msg.set_content(message, subtype='html')
    # msg.attach(MIMEText(message, 'html'))
    # msg.add_attachment(compliancecsv, filename='AscomComplianceReport_{}.csv'.format(timestamp.strftime("%Y%m%d%H%M%S")))

    try:
        smtpObj = smtplib.SMTP(smtpserver)
        smtpObj.sendmail(sender_email, receiver_email, msg.as_string())         
        print("Successfully sent email")
    except Exception as e:
        print("Error: unable to send email")    
        print(e)
        # return e


def main():
    with open(envFile, "r") as read_file:
        configData = json.load(read_file)

    receiver_email = configData['receiver_email']
    downloadFile = downloadfile(downloadDir=downloadDir, filename=filename, suffix=suffix)
    print(downloadFile)
    database = "{}{}/databases/EliseSite.db.securebackup".format(downloadDir,downloadFile)
    print("Database: {}".format(database))
    df,summaryDf = getPhones(applist=applist, configList=configList, timestamp=timestamp, exportcsv=exportcsv, compliancecsv=compliancecsv, database=database)
    if not df.empty:

        e = sendemail(df=df, timestamp=timestamp, days=days, summaryDf=summaryDf, receiver_email=receiver_email)

if __name__ == "__main__":
    main()
