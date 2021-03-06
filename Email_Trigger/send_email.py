import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import socket
from AwsS3Storage.awsStorageManagement import AwsStorageManagement

class email:
    def __init__(self):
        self.user='Gmail email id'
        self.passwd='Gmail Passwd'
        self.awsObj = AwsStorageManagement()

    def trigger_mail(self,to_addr,cc_addr,msg):
        receivers=to_addr
        receivers.extend(cc_addr)
        msg['To'] = ", ".join(to_addr)
        from_addr='Wafer Detection <waferdetectionalert@gmail.com>'
        msg['From'] = from_addr
        if len(cc_addr)>0:
            msg['Cc'] = ", ".join(cc_addr)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(self.user, self.passwd)
        s.sendmail(from_addr, receivers, msg.as_string())
        s.close()