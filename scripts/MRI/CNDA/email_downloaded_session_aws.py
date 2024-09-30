import sys
import os
from email.mime.text import MIMEText

USER=os.getlogin()

CNDA_ses=sys.argv[1]

f = open(f"./CNDA_downloads/.email_creds")

email_address = f.readline().strip()
email_password = f.readline().strip()

f.close()

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.

# Create a text/plain message
#msg = EmailMessage()
if os.path.isdir(CNDA_ses):
    body = f"""
        <h2>
        A new MRI session has been successfully downloaded to the lab server.
        </h2>

        <a href="file:///Z:\{'/'.join(CNDA_ses.split('/')[4:])}">{CNDA_ses}</a>
        
        <p>
        Please confirm its status and organization are correct.
        </p>

    """

else:
    body = f"""
        <h2>
        An MRI session failed to download properly to the lab server.
        </h2>

        <h1>
        Please investigate.
        </h1>

        <p>
        The automated download pipeline attempted to download the session to this path:
        </p>

        <h2>
        {CNDA_ses}
        </h2>

        <p>
        Actions could include checking the status of the session on CNDA, whether it has any sessions marked as usable, whether the correct CNDA session label is entered in the CARE Data Tracker, ensuring there is enough available space on DynoSparky ZFS, etc.
        </p>
    
    """

msg = MIMEText(body, 'html')

# me == the sender's email address
# you == the recipient's email address
if os.path.isdir(CNDA_ses):
    msg['Subject'] = f'A Session Has Been Downloaded Successfully from CNDA: {CNDA_ses}'
else:
    msg['Subject'] = f'Error: A Session Has Failed to Download from CNDA: {CNDA_ses}'

msg['From'] = email_address
msg['To'] = "dennys@wustl.edu,lcbd@wustl.edu"

# Send the message
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(email_address, email_password)
    smtp.send_message(msg)