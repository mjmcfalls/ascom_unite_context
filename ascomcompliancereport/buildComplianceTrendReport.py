import pandas as pd
import numpy as np
import logging
import os
import glob
import json
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

# filesDir = "src/prodData/"
filesDir = "/download/export/"
# testReport = "/app/src/prodData/AscomComplianceReport_20200720060002.csv"

envFile = "/download/env/env.json"
timestamp = pendulum.now("America/New_York")


def findNewestMasterList(filePath):
    # masterPhoneList = "src/prodData/AscomMasterExport_20200720060002.csv"
    logging.debug("FilePath: {}".format(filePath))
    logging.debug("{}AscomMasterExport_*.csv".format(filePath))
    list_of_files = glob.glob("{}AscomMasterExport_*.csv".format(filePath))
    # logging.debug(list_of_files)
    latest_file = max(list_of_files, key=os.path.getctime)
    logging.info("Latest Master Export - {}".format(latest_file))
    return latest_file


def buildTrendReport(filesDir, dfMaster, headers):
    # read through files and pull headers.
    # Get files
    complianceFiles = [
        f for f in glob.glob("{}AscomComplianceReport_*.csv".format(filesDir))
    ]
    # Build headers for dfMaster
    [headers.append(f.split("_")[1].split(".")[0][:8]) for f in complianceFiles]
    dfMaster = dfMaster.reindex(columns=headers)
    # logging.debug(headers)
    # logging.debug(complianceFiles)
    # logging.debug(dfMaster)

    # Loop through files
    for f in complianceFiles:
        logging.info("Processing: {}".format(f))
        dfReport = pd.read_csv(filepath_or_buffer=f)
        dateCol = f.split("_")[1].split(".")[0][:8]
        # loop through report and update master if phone is in list
        for row in dfReport.itertuples():
            dfMaster.loc[dfMaster["Phone"] == row.Phone, [dateCol]] = True
            # logging.debug(dfMaster.loc[dfMaster['Phone'] == row.Phone, [dateCol]] )

    dfMaster.dropna(axis=0, how="all", subset=headers[1:], inplace=True)
    return dfMaster


def sendemail(filename, timestamp, sender_email, receiver_email, smtpserver, message, subject):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = ",".join(receiver_email)
    msg["Subject"] = subject
    logging.debug("Recipients: {}".format(receiver_email))
    logging.debug(message)
    msg.set_content(message, subtype='html')

    ctype, encoding = mimetypes.guess_type(filename)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so use a generic bag-of-bits type.
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    attachmentName = filename.split("/")[-1]
    logging.debug("attachment name: {}".format(attachmentName))
    with open(filename, 'rb') as fp:
        msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=attachmentName)

    try:
        # logging.info(msg)
        smtpObj = smtplib.SMTP(smtpserver)
        # smtpObj.sendmail(sender_email, receiver_email, msg.as_string())
        smtpObj.send_message(msg=msg, from_addr=sender_email, to_addrs=receiver_email)
        logging.info("Successfully sent email")
    except Exception as e:
        logging.info("Error: unable to send email")
        logging.info(e)
        # return e


def main():
    # Open env file
    with open(envFile, "r") as read_file:
        configData = json.load(read_file)

    # Set base headers for later.
    headers = ["Phone"]
    csvName = "{}AscomComplianceTrends_{}.csv".format(filesDir,timestamp.strftime("%Y%m%d%H%M%S"))
    subject = "[REPORT] - Ascom Myco Compliance Trend Report from {}".format(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    logging.debug("Main Functions")

    masterExport = findNewestMasterList(filePath=filesDir)
    messagebody = configData["trendmsg"].replace("DATE", timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    # Build dfMaster from master sfile
    dfMaster = pd.read_csv(filepath_or_buffer=masterExport)
    dfMaster = dfMaster[["Phone"]]
    dfMaster.dropna(subset=["Phone"], inplace=True)
    dfMaster["Phone"] = dfMaster["Phone"].astype(int)

    dfReturned = buildTrendReport(filesDir=filesDir, dfMaster=dfMaster, headers=headers)
    dfReturned.to_csv(csvName, index=False)
    sendemail(
        filename=csvName,
        timestamp=timestamp,
        sender_email=configData["sender_email"],
        receiver_email=configData["trend_receiver_email"],
        smtpserver=configData["smtpserver"],
        message=messagebody,
        subject=subject
    )



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
