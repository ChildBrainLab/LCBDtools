import sys
import os
from email.mime.text import MIMEText

USER=os.getlogin()

CNDA_ses=sys.argv[1]

credf = open(f"/home/usr/{USER}/.email_creds", 'r')

email_address = credf.readline().strip()
email_password = credf.readline().strip()

credf.close()

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.

# Create a text/plain message
#msg = EmailMessage()
body = f"""

    <h1>
    A new MRI session has been uploaded to the CNDA database under the CARE study, PID NP1166.
    </h1>

    <h2>
    Please follow this link or paste into your web browser:
    </h2>

    <a href="cnda.wustl.edu/REST/projects/NP1166/experiments/{CNDA_ses}?format=html">
    cnda.wustl.edu/REST/projects/NP1166/experiments/{CNDA_ses}?format=html
    </a>

    <p>
    Then, click the 'Edit' button on the right-hand toolbar, and mark the 'usability' of each scan, according to the notes in the Data Tracker. You can view a preview of MPRAGE structural scans by clicking the 'details' icon to the left of the scan acquisition number. 
    </p>

    <h2>
    Pay close attention! There should only be one 'usable' scan of each type. I.e. there should not be 2 MPRAGES marked usable in one session.
    </h2>

    <p>
    If, for some reason, a visit was collected over the course of 2 sessions (i.e. MPRAGE in one session, and BOLD run in a session 1 day later), paste both of them into the 'CNDA LAbel' column of the Data Tracker, separated by a single comma.
    </p>

    <p>
    Once any usability attributes have been marked, submit the changes in CNDA, and then paste this CNDA session label into the appropriate sheet and row of the CARE Data Tracker:
    </p>

    <h2>
    {CNDA_ses}
    </h2>

    <p>
    A confirmation email will be sent once the data has been downloaded to the lab server.
    </p>
    
    """

msg = MIMEText(body, 'html')

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = f'A Session Has Been Uploaded to CNDA: {CNDA_ses}'
msg['From'] = email_address
msg['To'] = "claytons@wustl.edu,lcbd@wustl.edu"

# Send the message
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(email_address, email_password)
    smtp.send_message(msg)


