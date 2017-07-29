import urllib;
import time;
import smtplib;
import traceback;
from datetime import datetime;
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText;


def isUP(url):
    try:
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
    emsg['From'] = "shiva.sunar@aksitservices.co.in";
    emsg['To'] = "shiva.sunar@aksitservices.co.in";
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
        server = smtplib.SMTP('smtp.mail.yahoo.com', 25);
        print "Starting TLS Session to Mail Server...";
        server.starttls()
        print "Logging User to Mail Server..."
        server.login(user="shiva.sunar@aksitservices.co.in",
                     password="Tm9maGNobWFhQDc=".decode('base64'));
        print "Sending Email...";
        server.sendmail(from_addr="shiva.sunar@aksitservices.co.in",
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
        sendEmail("yourself@aksitservices.co.in", message);
    else:
        # if all site are UP send OK Mail to your senior.
        sendEmail("yourboss@aksitservices.co.in", message);
    return;


def main():
    message = "";
    while True:
        # checks if the network is up or down by checking google.
        if (isUP("https://www.google.com")):
            print "Network is UP...";
            message = "";
            message += messageFor("http://aksitservices.co.in") + "\n";
            message += messageFor("https://www.akashmemorial.org") + "\n";
            message += messageFor("http://www.akashsaxena.com") + "\n";
            sendMessage(message);
            break;
        else:
            print "Network is Down...Will Try After Some Time...";
            time.sleep(5);

    print message;
    return;


if __name__ == "__main__":
    main();
