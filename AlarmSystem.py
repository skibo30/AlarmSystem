#AlarmSystem.py

#!/usr/bin/env python

import time
import datetime
import RPi.GPIO as GPIO
import sqlite3
import tweepy
import sys
import smtplib

# Importing Mail modules
from email.mime.text import MIMEText
gmail_pwd = ""

# Consumer keys and access tokens, used for OAuth
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

FrontIsOpen = False
BackIsOpen = False

# Create def for sending email
def sendEmail (message):
        EmailTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        EmailMessage = "\r\n".join([
        "Subject: %s at %s"%(message,EmailTime),
        "",
        "%s at %s"%(message,EmailTime),
        ""
        ])
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()
        server.login(gmail_acct,gmail_pwd)
        server.sendmail(sender,receiver,EmailMessage)
        server.quit()

# handle the door events
def buttonEventHandlerFront (pin):
        global FrontIsOpen
        if GPIO.input(pin):
                if not(FrontIsOpen):
                        tweet_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        tweet_txt = "Front Opened - " + tweet_txt
                        api.update_status(tweet_txt)
                        databaseInsert('Front','Open')
                        print "Front Door Opened - Do you live in a barn?\n"
                        GPIO.output(18,True)  # Red On
                        GPIO.output(25,False) # Green Off
                        FrontIsOpen = True
                        print "FrontIsOpen-FrontOpened"
                        print FrontIsOpen
                        sendEmail("Front Door has been opened")
        else:
                if FrontIsOpen:
                        tweet_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        tweet_txt = "Front Closed - " + tweet_txt
                        api.update_status(tweet_txt)
                        databaseInsert('Front','Close')
                        print "Front Door Closed!\n"
                        GPIO.output(25,True)  # Green On
                        GPIO.output(18,False) # Red Off
                        FrontIsOpen = False
                        print "FrontIsOpen-FrontClosed"
                        print FrontIsOpen
                        sendEmail("Front Door has been closed")

# Back door is a test button and is reverse short circuit logic
def buttonEventHandlerBack (pin):
        global BackIsOpen
        if GPIO.input(pin):
                if BackIsOpen:
                        tweet_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        tweet_txt = "Test Button Released - " + tweet_txt
                        api.update_status(tweet_txt)
                        databaseInsert('TestButton','Close')
                        print "Back Door Closed!\n"
                        GPIO.output(25,True)  # Green On
                        GPIO.output(18,False) # Red Off
                        BackIsOpen = False
                        print "BackIsOpen-BackClosed"
                        print BackIsOpen
                        sendEmail("Test Button has been pushed")
        else:
                if not(BackIsOpen):
                        tweet_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        tweet_txt = "Test Button Pushed - " + tweet_txt
                        api.update_status(tweet_txt)
                        databaseInsert('TestButton','Open')
                        print "Back Door Opened - Do you live in a barn?\n"
                        GPIO.output(18,True)  # Red On
                        GPIO.output(25,False) # Green Off
                        BackIsOpen = True
                        print "BackIsOpen-BackOpened"
                        print BackIsOpen
                        sendEmail("Test Button has been released")

# handle the SQLite inserts
def databaseInsert (door,status):
        conn=sqlite3.connect('/home/pi/Code/Prod/AlarmSystem.db')
        curs=conn.cursor()

        if door == 'Front':
                if status == 'Open':
#                       print "Front Door Open database insert"
                        curs.execute("INSERT INTO alarm VALUES(null,'Front','Open',(?))",(datetime.datetime.now().$
                else:
#                       print "Front Door Close database insert"
                        curs.execute("INSERT INTO alarm VALUES(null,'Front','Closed',(?))",(datetime.datetime.now($
        else:
                if status == 'Open':
#                       print "Back Door Open database insert"
#                       curs.execute("INSERT INTO alarm VALUES(null,'Back','Open',(?))",(datetime.datetime.now().s$
                else:
#                       print "Back Door Close database insert"
#                       curs.execute("INSERT INTO alarm VALUES(null,'Back','Closed',(?))",(datetime.datetime.now()$
        conn.commit()
        conn.close()

# main function
def main():
        global BackIsOpen
        global FrontIsOpen

        tweet_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tweet_txt = "App Started - " + tweet_txt
        api.update_status(tweet_txt)

        sendEmail("App has been started")

        print "BackIsOpen"
        print BackIsOpen
        print "FrontIsOpen"
        print FrontIsOpen

        # tell the GPIO module that we want to use
        # the chip's pin numbering scheme
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(18,GPIO.OUT) # Red LED
        GPIO.setup(22,GPIO.IN)  # Back Door
        GPIO.setup(23,GPIO.IN)  # Front Door
        GPIO.setup(24,GPIO.OUT) # Status (Yellow) LED
        GPIO.setup(25,GPIO.OUT) # Green LED

        GPIO.add_event_detect(23,GPIO.BOTH) # Checks for Front Door opening/closing
        GPIO.add_event_callback(23,buttonEventHandlerFront)
        GPIO.add_event_detect(22,GPIO.BOTH) # Checks for Back Door opening/closing
        GPIO.add_event_callback(22,buttonEventHandlerBack)

        # turn off Red LED, turn on Green and Yellow LEDs (assuming doors are shut at execution)
        GPIO.output(18,False)
        GPIO.output(25,True)
        GPIO.output(24,True)

        # make the yellow LED flash
        while True:
                GPIO.output(24,True)
                time.sleep(0.1)
                GPIO.output(24,False)
                time.sleep(0.1)

        GPIO.cleanup()

if __name__=="__main__":
        try:
                main()
        except KeyboardInterrupt:
                tweet_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tweet_txt = "Keyboard Exit - " + tweet_txt
                api.update_status(tweet_txt)
                print "Keyboard Exit"
                GPIO.cleanup()
