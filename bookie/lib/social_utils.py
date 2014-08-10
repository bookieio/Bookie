
from BeautifulSoup import BeautifulSoup
import requests
from tweepy import OAuthHandler
from tweepy import API


def create_twitter_userapi(consumer_key, consumer_secret,
                           oauth_token, oauth_verifier):
    """Creates twitter user api object from oauth credentials """
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_request_token(oauth_token, oauth_verifier)
    access_token = auth.get_access_token(oauth_verifier)
    api = API(auth)
    return api, access_token


def create_twitter_OAuthHandler(consumer_key, consumer_secret):
    """Return Twitter link to get OAuth permission for Bookie """
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url()
    return auth_url


def get_url_title(url):
    """Return title of webpage """
    try:
        webpage = requests.get(url)
        parsed_html = BeautifulSoup(webpage.content)
        return webpage.url, parsed_html.title.string
    except:
        return url, ''
