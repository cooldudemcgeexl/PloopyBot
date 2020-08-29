import os
import random
import tweepy
import logging
import time
from textwrap import wrap
from dotenv import load_dotenv

logger = logging.getLogger()
load_dotenv()

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
        lines = wrap(passageText,280)
        passageText = random.choice(lines)
    logger.info("Returned message: %s" % passageText)
    return passageText

def pull_passage_list():
    inputFile = open(os.getenv("INPUT_FILE"),'r', encoding = 'utf-8')
    passageList = inputFile.readlines()
    inputFile.close()
    return passageList

def main():
    api = create_api()
   # passageList = pull_passage_list()
    random.seed()
    while True:
        # Probably going to change this to an async implementation in the future
        # Sticking with synchronous + sleep as this bot only has one function atm
        try:
            api.update_status(get_random_passage())
            waitTime = random.randint(2000,40000)
            print("Waiting for %d seconds..." % waitTime)
            logger.info("Waiting for %d seconds..." % waitTime)
            time.sleep(waitTime)
        except:
            logger.error("Invalid message chosen")


# Moved passage list here due to reliance on globals
# Will update to better implementation
passageList = pull_passage_list()

if __name__ == "__main__":
    main()