import re 
import tweepy 
import keys
import string
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
from tweepy import OAuthHandler 
  
class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. Using Pythong library SentimentIntensityAnalyzer from NLTK for sentiment method 
    '''
    def __init__(self): 
        # keys and tokens from the Twitter Dev Console 
        consumer_key = keys.consumer_key
        consumer_secret = keys.consumer_secret
        access_token = keys.access_token
        access_token_secret = keys.access_token_secret
  
        # attempt authentication 
        try: 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 
  
    def remove_html(self, text):
        soup = BeautifulSoup(text, 'lxml')
        return soup.get_text()

    def remove_punctuation(self, text):
        return "".join([c for c in text if c not in string.punctuation])

    def remove_stopwords(self, text):
        words = [w for w in text if w not in stopwords.words('english')]
        return words
    
    def word_lemmatizer(self, text):
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in text]

    def word_stemmer(self, text):
        stemmer = PorterStemmer()
        return " ".join([stemmer.stem(i) for i in text])

    def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        #TODO: Clean @usernames and links
        cleanTweet = self.remove_html(tweet)
        cleanTweet = [self.remove_punctuation(word) for word in cleanTweet.split(" ")]
        cleanTweet = self.remove_stopwords(cleanTweet)
        cleanTweet = self.word_lemmatizer(cleanTweet)

        return "".join(self.word_stemmer(cleanTweet) + " ")
  
    def get_tweet_sentiment(self, tweet): 
        ''' 
        Utility function to classify sentiment of passed tweet 
        using SentimentIntensityAnalyzer's sentiment method 
        ''' 
        sia = SentimentIntensityAnalyzer()
        analysis = sia.polarity_scores(self.clean_tweet(tweet))
        # set sentiment 
        if analysis["compound"] > .0: 
            return 'positive'
        
        else: 
            return 'negative'
  
    def get_tweets(self, query, count = 100): 
        # empty list to store parsed tweets 
        tweets = [] 
  
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count, lang = 'en') 
  
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 
  
                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 
  
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
  
            # return parsed tweets 
            return tweets 
  
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 
  
def main(): 
    # creating object of TwitterClient Class 
    api = TwitterClient() 
    # calling function to get tweets 
    tweets = api.get_tweets(query = 'happy', count = 200) 
  
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    # percentage of positive tweets 
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
    # percentage of negative tweets 
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    # percentage of neutral tweets 
    print("Neutral tweets percentage: {} % ".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))) 
  
    # printing first 5 positive tweets 
    print("\n\nPositive tweets:") 
    for tweet in ptweets[:10]: 
        print(tweet['text']) 
  
    # printing first 5 negative tweets 
    print("\n\nNegative tweets:") 
    for tweet in ntweets[:10]: 
        print(tweet['text']) 
  
if __name__ == "__main__": 
    # calling main function 
    main() 