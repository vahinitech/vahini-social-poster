from app.services.base import BaseSocialService


class TwitterService(BaseSocialService):
    platform = "twitter"
    display_name = "X / Twitter"
    scope = "tweet.read tweet.write users.read offline.access"
    default_authorize_url = "https://twitter.com/i/oauth2/authorize"
    default_token_url = "https://api.x.com/2/oauth2/token"
    default_api_base_url = "https://api.x.com/2/tweets"
