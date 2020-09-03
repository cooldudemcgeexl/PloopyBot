import os
import random
import tweepy
import logging
import time
from datetime import datetime
from textwrap import wrap
from dotenv import load_dotenv

logging.basicConfig(
    handlers=[logging.FileHandler('botlog.log', 'a', 'utf-8')],
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] - %(message)s')
logger = logging.getLogger()

load_dotenv()

class ReplyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        bot = api.me()
        if status.user.id != bot.id:
            try:
                api.update_status(status = "ZOO-WEE MAMA!",in_reply_to_status_id = status.id, auto_populate_reply_metadata = True)
                logger.info("Replied to user @%s" % status.user.screen_name)
            except:
                logger.error("Could not send reply", exc_info = True)

    def on_error(self, status_code):
        logger.error("Returned error code %d" % status_code)


def create_api():
    API_KEY = os.getenv("API_KEY")
    API_KEY_SECRET = os.getenv("API_KEY_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(API_KEY,API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify = True)

    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info= True)
        raise e
    logger.info("API Created")
    return api

def get_random_passage():
    global passageList
    if len(passageList) == 0:
        passageList = pull_passage_list()

    randline = random.randint(0,len(passageList)-1)
    passageText = passageList.pop(randline)
    # Removing quotes, comma, and newline. These will always occupy the same positions in the string.
    passageText = passageText[1:-3]
    if len(passageText) > 280:
        lines = wrap(passageText,270)
        passageText = lines
        logger.info("Returned multipart message. Parts: %d" % len(passageText))
        return passageText
    else:
        logger.info("Returned message of length %d" % len(passageText))
        return passageText

def pull_passage_list():
    inputFile = open(os.getenv("INPUT_FILE"),'r', encoding = 'utf-8')
    passageList = inputFile.readlines()
    inputFile.close()
    return passageList


def main():

    # Setting up listener for replying
    replyListener = ReplyStreamListener()
    replyStream = tweepy.Stream(auth = api.auth,listener = replyListener)
    replyStream.filter(follow=[os.getenv("BOT_ID")], is_async = True)
    
    # Setting min and max wait times as defined in .env
    MIN_TIME = int(os.getenv("MIN_TIME"))
    MAX_TIME = int(os.getenv("MAX_TIME"))
    random.seed()

    while True:
        # Probably going to change this to an async implementation in the future
        # Sticking with synchronous + sleep as this bot only has one function atm
        try:
            newStatus = get_random_passage()
            if type(newStatus) is list:
                tweetNumber = 1
                totalTweets = len(newStatus)
                for statusPart in newStatus:
                    partialTweet = "%s (%d/%d)" % (statusPart, tweetNumber, totalTweets)
                    api.update_status(status=partialTweet)
                    logger.info("Sent tweet: %s" % partialTweet)
                    tweetNumber += 1
            else:
                api.update_status(status=newStatus)
                logger.info("Sent tweet: %s" % newStatus)
            waitTime = random.randint(MIN_TIME,MAX_TIME)
            logger.info("Waiting for %d seconds..." % waitTime)
            time.sleep(waitTime)
        except:
            logger.error("Invalid message chosen", exc_info = True)


# Moved passage list here due to reliance on globals
# Will update to better implementation
passageList = pull_passage_list()
api = create_api()

if __name__ == "__main__":
    main()