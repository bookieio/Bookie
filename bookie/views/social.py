"""Oauth Urls rendering"""
from datetime import datetime
import logging
import tweepy
from pyramid.view import view_config

from bookie.lib.social_utils import (
    create_twitter_userapi,
    create_twitter_OAuthHandler)
from bookie.models.social import (
    SocialMgr,
    TwitterConnection)

LOG = logging.getLogger(__name__)


@view_config(route_name="twitter_connect",
             renderer="/social/social_connect.mako")
def twitter_connect(request):
    """function to get users twitter oauth information"""

    # Twitter Application details are imported from ini file
    settings = request.registry.settings
    twitter_consumer_key = settings.get('twitter_consumer_key', False)
    twitter_consumer_secret = settings.get('twitter_consumer_secret', False)

    oauth_token = request.params.get('oauth_token', None)
    oauth_verifier = request.params.get('oauth_verifier', None)
    denied = request.params.get('denied', None)
    if denied:
        LOG.error('Twitter connection denied')
        return {
            'result': 'Connection Denied! Try connecting again.',
            'retry_link': True
        }
    elif oauth_token and oauth_verifier:
        # First make sure these credentials do not exist for another user.
        found = TwitterConnection.query.filter(
            TwitterConnection.access_secret == unicode(oauth_token),
            TwitterConnection.access_secret == unicode(oauth_verifier)).first()
        if found:
            return {
                'result': 'Invalid credentials, another user has claimed them'
            }

        # If url contains OAUTH credentials, after making sure that same
        # credentials are not provide by any other user they are saved to
        # twitterconnection table
        try:
            api, access_token = create_twitter_userapi(
                twitter_consumer_key, twitter_consumer_secret,
                oauth_token, oauth_verifier)
            twitter_user = api.me()
        except (tweepy.TweepError, IOError):
            LOG.\
                error('Twitter connection denied tweepy IOError')
            return dict(result="""Twitter has returned an\
             error. Try connecting again.""")

        connections = TwitterConnection.query.filter(
            TwitterConnection.uid == unicode(twitter_user.id)).all()
        if connections and connections[0].username == request.user.username:
            # If any other user has provided the same credentials message is
            # shown
            return dict(result="""Another user (%s) has already connected\
             with those Twitter credentials.""" % (request.user.username))

        credentials = {
            'is_active': True,
            'last_connection': datetime.now(),
            'uid': unicode(twitter_user.id),
            'access_key': access_token.key,
            'access_secret': access_token.secret,
            'twitter_username': twitter_user.screen_name,
            'refresh_date': datetime.now()}

        SocialMgr.store_twitter_connection(request.user.username, credentials)
        return dict(result='Successfully Done')
    else:
        # If url doesnt contain OAUTH credentials the user is redirected
        # to twitter link to give permission to Bookie twitter application
        auth_url = create_twitter_OAuthHandler(
            twitter_consumer_key, twitter_consumer_secret)
        return {'url': auth_url}
