#Sometime system admin have to check if some websites are up or not and mail to their boss...
#This code can automate it.
#Tips: Make an Executable from this code with PyInstaller or whatever software you like 
#And use Task Scheduler in Windows to Schedule this.
import urllib;
import time;
import smtplib;
import traceback;
from datetime import datetime;
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText;


def isUP(url):
    try:
        #Or Add your code, to define what "A Website is UP" means to you...
        return str(urllib.urlopen(url).getcode()) == "200";
    except:
        return False;


def getDateTime():
    return datetime.now().strftime('%Y-%m-%d %H:%M');


def getDate():
    return datetime.now().strftime('%Y-%m-%d');


def messageFor(url):
    if (isUP(url)):
        return url + "\tis UP on " + getDateTime();
    else:
        return url + "\tis DOWN on " + getDateTime();


def sendEmail(emailAddress, message):
    emsg = MIMEMultipart();
    emsg['From'] = "shiva.sunar@aksitservices.co.in"; #Change to your Requirement
    emsg['To'] = "shiva.sunar@aksitservices.co.in";#Change to your Requirement
    emsg['Subject'] = "Website Status of " + getDate();
    emsg['Cc'] = "";
    body = "Dear Sir,\n" \
           "This is website status of " + getDate() + "\n\n" \
           + message + "\n" \
           "Regards,\n" \
           "Shiva Sunar\n" \
           "InfoSec Consultant";
    emsg.attach(MIMEText(body, 'plain'));

    try:
        print "Initiating Email Setup...";
        server = smtplib.SMTP('smtp.mail.yahoo.com', 25);#Change to your Requirement
        print "Starting TLS Session to Mail Server...";
        server.starttls()
        print "Logging User to Mail Server..."
        server.login(user="shiva.sunar@aksitservices.co.in",#Change to your Requirement
                     #I encoded and decoded in base64 that if some person looks at code he don't know password immediately...
                     password="PutYourBase64EncodedPasswordHere".decode('base64'));
        print "Sending Email...";
        server.sendmail(from_addr="shiva.sunar@aksitservices.co.in",#Change to your Requirement
                        to_addrs="shiva.sunar@aksitservices.co.in",  # emailAddress to send
                        msg=emsg.as_string())
        print "Email Sent...";
        print "Closing Mail Server Connection...";
        server.quit();

    except:
        print("Some Error Occured While Sending Mail!!!")
        traceback.print_exc();

    return;


def sendMessage(message):
    if ("DOWN" in message):
        # if there any site is down send mail to yourself to further check
        sendEmail("yourself@aksitservices.co.in", message);#Change to your Requirement
    else:
        # if all site are UP send OK Mail to your senior.
        sendEmail("yourboss@aksitservices.co.in", message);#Change to your Requirement
    return;


def main():
    message = "";
    while True:
        # checks if the network is up or down by checking google.
        if (isUP("https://www.google.com")):
            print "Network is UP...";
            message = "";
            message += messageFor("http://aksitservices.co.in") + "\n";#Change to your Requirement
            message += messageFor("https://www.akashmemorial.org") + "\n";#Change to your Requirement
            message += messageFor("http://www.akashsaxena.com") + "\n";#Change to your Requirement
            sendMessage(message);
            break;
        else:
            print "Network is Down...Will Try After Some Time...";
            time.sleep(5);

    print message;
    return;


if __name__ == "__main__":
    main();
