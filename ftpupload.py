
# # ###########################################################################
# # Script:       ftpupload.py
# # Author:       Bradley Glenn Jones
# # Date:         January 13, 2016
# # Purpose:      Copy manhole and sewerline files for upload
# # Changes:      Added ftp upload
# # Inputs:       Sewerline and manhole feature classes
# # Outputs:      Sewerline and manhole shapefiles uploaded to ftp
# # ###########################################################################

import arcpy
import os
import datetime
import time
import ftplib

from arcpy import env

env.workspace = r"C:\PATH\TO\SDE\CONNECTION\FILE.SDE"
env.overwriteOutput = True
source = env.workspace

# Define function for sending email.
def send_email(user, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("172.21.1.147")
        server.sendmail(FROM, TO, message)
        server.close()
        log.write(str(time.asctime()) + ": Successfully sent email.\n")
    except:
        log.write(str(time.asctime()) + ": Failed to send email.\n")

# Variables
manhole = "SDE.SEWERMAN.MANHOLES_VIEW"
sewerlines = "SDE.SEWERMAN.SEWERS_VIEW"

# Create a text file for logging
log = open(r"\\path\to\script\log.txt", "a")
log.write("***************************************************************************************************\n")

# Create the directory for the data to be uploaded
newDirectory = r"\\path\to\new\directory" + str(datetime.date.today())
os.makedirs(newDirectory)
log.write(str(time.asctime()) + ": New upload directory created.\n")

# Copy the feature classes to the new directory
mhShape = arcpy.FeatureClassToFeatureClass_conversion(manhole, newDirectory, "Manholes")
log.write(str(time.asctime()) + ": Manhole feature class copied to new directory.\n")

arcpy.DeleteField_management(mhShape, "X_COORD; Y_COORD")
log.write(str(time.asctime()) + ": X_COORD and Y_COORD fields deleted from manhole shapefile.\n")

arcpy.FeatureClassToFeatureClass_conversion(sewerlines, newDirectory, "SewerLines")
log.write(str(time.asctime()) + ": SewerLine feature class copied to new directory.\n")

# Upload data to ftp
try:
    root = (r"\\path\to\new\directory" + str(datetime.date.today()) + "\\")
    fileNames = os.listdir(root)
    log.write(str(time.asctime()) + ": " + str(fileNames))

    connection = ftplib.FTP("ftp.someftp.org", "unsername", "password")

    welcomeMsg = connection.getwelcome()
    log.write(str(time.asctime()) + ": " + str(welcomeMsg) + "\n")

    workDir1 = connection.cwd("/path/direcotry")
    log.write(str(time.asctime()) + ": " + str(workDir1) + "- /path/directory \n")

    newDirectory = connection.mkd("orgname" + str(datetime.date.today()))
    log.write(str(time.asctime()) + ": New directory created- " + str(newDirectory) + "\n")

    workDir2 = connection.cwd(newDirectory)
    log.write(str(time.asctime()) + ": " + str(workDir2) + " " + str(newDirectory) + "\n")

    # for loop
    for fName in fileNames:
        filePath = open(os.path.join(root, fName), "rb")
        log.write(str(time.asctime()) + ": " + str(filePath) + "\n")
        upload = connection.storbinary("STOR " + fName, filePath)
        log.write(str(time.asctime()) + ": " + str(upload) + " " + str(fName) + "\n")

    disconnect = connection.quit()
    log.write(str(time.asctime()) + ": " + str(disconnect) + "\n")
    # Send email to notify of script completion.
    successSubj = "FTP Script completed"
    successContent = "ftp upload script completed successfully."
    successPitcher = "email@domain.com"
    successCatchers = "another.email@domain.com"
    send_email(successPitcher, successCatchers, successSubj, successContent)
    log.close()

except Exception, e:
    log.write(str(time.asctime()) + ": " + str(e) + "\n")
    # Send email to notify of script failure.
    subj = "FTP Script Failure"
    content = "ftp upload script failed to complete: " + str(e)
    pitcher = "email@domain.com"
    catchers = "another.email@domain.com"
    send_email(pitcher, catchers, subj, content)
    log.close()

log.close()


