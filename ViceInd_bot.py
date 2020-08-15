import tweepy
import logging
import os
import time

logger = logging.getLogger()

def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        print(api.verify_credentials())
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    print("API created")
    return api

def follow_followers(api):
    logger.info("Retrieving and following followers")
    followcount=0
    followlimit=30
    for follower in tweepy.Cursor(api.followers).items():
        #print(vars(follower))
        if not follower.following and not follower.follow_request_sent:
            logger.info(f"Following {follower.name}")
            follower.follow()
            followcount+=1
            if(followcount==followlimit):
                return

def retweet_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        logger.info(f"Retweeting {tweet.user.name}")
        if not tweet.retweeted:
            # Retweet, since we have not retweeted it yet
            try:
                tweet.favorite()
                tweet.retweet()
            except Exception as e:
                logger.error("Error on fav and retweet", exc_info=True)

        if not tweet.user.following:
            tweet.user.follow()

    return new_since_id            

def like_replies(api, since_id):
    new_since_id = since_id

    for tweet in tweepy.Cursor(api.search, q='to:{}'.format("@IndVice"),
            since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        #if tweet.in_reply_to_status_id is not None:
        #    continue
        logger.info(f"Liking {tweet.user.name}")
        if tweet.favorited==True:
            continue
        try:
            tweet.favorite()
        except Exception as e:
            logger.error("Error on fav replies", exc_info=True)
            continue
        if not tweet.user.following:
            tweet.user.follow()


    return new_since_id


if __name__=="__main__":
    api = create_api()
    rt_since_id= 1
    repl_since_id = 1
    with open("Gold_ViceInd_tweets.txt") as f:
        for line in f:
            print(line)
            repl_since_id = like_replies(api,repl_since_id)
            rt_since_id = retweet_mentions(api,rt_since_id)
            follow_followers(api)
            api.update_status(line)
            time.sleep(86400)

            





