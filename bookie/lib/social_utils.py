
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


def create_github_OAuthHandler(github_client_id):
    """Return Github link to get OAuth permission for Bookie"""
    auth_url = 'https://github.com/login/oauth/authorize'
    return '%s?client_id=%s' % (auth_url, github_client_id)


def get_github_access_token(github_client_id, github_client_secret, code):
    """Return access token of github user"""
    params = {'client_id': github_client_id,
              'client_secret': github_client_secret,
              'code': code}
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}
    url = 'https://github.com/login/oauth/access_token'
    res = requests.post(url, headers=headers, params=params)
    data = res.json()
    try:
        return data['access_token']
    except:
        raise KeyError("The code passed is incorrect or expired")


def get_github_user_data(access_token):
    """Return details of authenticated user to save in database"""
    params = {'access_token': access_token}
    url = 'https://api.github.com/user'
    res = requests.get(url, params=params)
    user_data = res.json()
    return user_data
