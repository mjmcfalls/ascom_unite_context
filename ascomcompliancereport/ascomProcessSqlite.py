import pandas as pd
import numpy as np
import sqlite3
import time
import math
from datetime import datetime
import io
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

start = time.time()

days = 7
fileTimestamp = time
compliancecsv = 'download/complianceReport_{}.csv'.format(fileTimestamp.strftime("%Y%m%d%H%M%S"))
sender_email = "from@email.address"
receiver_email = "to@email.address"
smtpserver = 'smtp-server'

applist = []
configList = []
output = []
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

def processPhone(phone, apps, configs):
    print(phone)
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

def getItem(phone, field):
    results = df.query("CurrentCallNo == @phone")
    # print(results[field].iloc[0])
    return results[field].iloc[0]
  
def getValues(k, v, phone, query):
    value = str(v)
    # print(value)
    temp_df = df.query(query)
    if temp_df.empty:
        # print("Phone: {}; App: {}; value: {}".format(phone, k, temp_df["Value"].values))
        return None
    else:   
       # print("Phone: {}; App: {}; value: {}".format(phone, k, temp_df["Value"].values[0]))
        return temp_df["Value"].values[0]



query = "Select CurrentCallNo, tDevices.Description, tPortables.UnitId, tDevices.FirmwareVersion, SerialNumber, IPAddress, LoginTime, tListParameters.Key, tListParameters.Value, ListIndex, tPortables.DeviceType FROM tDevices INNER JOIN tPortables ON tPortables.UnitID = tDevices.UnitID INNER JOIN tListParameters ON tListParameters.PortableId = tPortables.Id WHERE tListParameters.Value = 0 OR tListParameters.Value = 1;"
settingsQuery = "Select Key, Value, tPortables.CallNo FROM tParameters227 INNER JOIN tPortables ON tPortables.Id = tParameters227.PortableId"

conn = sqlite3.connect("/app/download/src/20200302125321_unite_communication_server-1.5.0-backup/databases/EliseSite.db.securebackup")

paramDf = pd.read_sql_query(query, conn)
settingsDf = pd.read_sql_query(settingsQuery, conn)

phones = np.sort(paramDf.CurrentCallNo.unique())
# phones = phones[1:10]
print("Number of phones: {}".format(len(phones)))
for p in phones:
    applist.append(apps)
    configList.append(configs)
    # output.append(processPhone(p, apps, configs))
r = list(map(lambda x, apps, configs: processPhone(x, apps, configs), phones, applist, configList))

tdf = pd.DataFrame.from_dict(r)

tdf["Settings_Compliance"] = True
tdf["Network_Compliance"] = True
tdf['80211N_Compliance'] = True
tdf['Firmware_Compliance'] = True

# print(tdf.head())
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
                tdf.at[index, "Settings_Compliance"] = False

        # Settings
        for k,v in settings_dict.items():
            if k == "wifi_freq_band":
                if row['Description'].lower().startswith("mhs") or row['Description'].lower().startswith("mm") or row['Description'].lower().startswith("mcd"):
                    if str(row[k]) == "1":
                        pass
                    elif str(row[k]) != "1":
                        # print("not equal 1")
                        tdf.at[index, "Network_Compliance"] = False

                elif str(row[k]) != "2":
                    tdf.at[index, "Network_Compliance"] = False

            elif k == "80211N":
                if str(row[k]) == str(v):
                    pass
                else:
                    tdf.at[index, "80211N_Compliance"] = False

            elif k == "FirmwareVersion":
                if str(row[k]) == str(v):
                    pass
                else:
                    tdf.at[index, "Firmware_Compliance"] = False
                    
            else:
                if str(row[k]) == str(v):
                    pass
                else:
                    tdf.at[index, "Settings_Compliance"] = False
                    
daysDf = tdf[(tdf['DaysLastSeen'] <= days)]
comDf = daysDf.loc[(daysDf['Settings_Compliance'] == False) | (daysDf['Network_Compliance'] == False) | (daysDf['80211N_Compliance'] == False) | (daysDf['Firmware_Compliance'] == False)]

comDf['wifi_freq_band'] = comDf['wifi_freq_band'].apply({'1':"5 GHz", '2': "2.4 GHz"}.get)
comDf['80211N'] = comDf['80211N'].apply({'0':"Disabled", '1': "Enabled"}.get)
# comDf['80211N'].fillna("Enabled")
comDf['80211N'].replace(to_replace=[None], value="Enabled", inplace=True)
comDf[["Phone","Description","DaysLastSeen","Settings_Compliance","Network_Compliance","80211N_Compliance","Firmware_Compliance","macaddress","SerialNumber","FirmwareVersion","wifi_freq_band","80211N"]].to_csv(compliancecsv, index=False)


tdf.to_csv('download/export_{}.csv'.format(fileTimestamp), index=False)

# temp = comDf[["Phone","Description","DaysLastSeen","macaddress","SerialNumber","FirmwareVersion","wifi_freq_band","80211N","Settings_Compliance","Network_Compliance","80211N_Compliance","Firmware_Compliance"]]
# print(temp['80211N'])

# Send email
str_io = io.StringIO()

comDf[["Phone","Description","DaysLastSeen","Settings_Compliance","Network_Compliance","80211N_Compliance","Firmware_Compliance","macaddress","SerialNumber","FirmwareVersion","wifi_freq_band","80211N"]].to_html(buf=str_io, classes='table table-striped', index=False)

html_str = str_io.getvalue()
# print(html_str)

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "[REPORT] - Ascom Myco Settings Compliance Report from {}".format(fileTimestamp.strftime("%Y-%m-%d %H:%M:%S"))

# message = '<style>table { border-collapse: collapse; border-spacing: 0; width: 100%; border: 1px solid #ddd; } th, td { text-align: left; padding: 16px; } tr:nth-child(even) { background-color: #f2f2f2; }</style> '
message = "<p>Ascom Myco Settings Compliance Report from {}</p>".format(fileTimestamp.strftime("%Y-%m-%d %H:%M:%S"))
message = message + html_str
# print(message)

msg.attach(MIMEText(message, 'html'))

# Attach csv
ctype, encoding = mimetypes.guess_type(compliancecsv)
if ctype is None or encoding is not None:
    ctype = "application/octet-stream"

maintype, subtype = ctype.split("/", 1)

if maintype == "text":
    print('text')
    fp = open(compliancecsv)
    # Note: we should handle calculating the charset
    attachment = MIMEText(fp.read(), _subtype=subtype)
    fp.close()
elif maintype == "image":
    print('image')
    fp = open(compliancecsv, "rb")
    attachment = MIMEImage(fp.read(), _subtype=subtype)
    fp.close()
elif maintype == "audio":
    print('audio')
    fp = open(compliancecsv, "rb")
    attachment = MIMEAudio(fp.read(), _subtype=subtype)
    fp.close()
else:
    print('else')
    fp = open(compliancecsv, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
attachment.add_header("Content-Disposition", "attachment", filename=compliancecsv.split('/')[1])
msg.attach(attachment)

try:
    smtpObj = smtplib.SMTP(smtpserver)
    smtpObj.sendmail(sender_email, receiver_email, msg.as_string())         
    print("Successfully sent email")
except Exception as e:
    print("Error: unable to send email")    
    print(e)
    

end = time.time()
print("Time: {}".format(end - start))


