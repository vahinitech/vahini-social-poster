from app.services.base import BaseSocialService


class FacebookService(BaseSocialService):
    platform = "facebook"
    display_name = "Facebook Pages"
    scope = "pages_manage_posts pages_read_engagement"
    default_authorize_url = "https://www.facebook.com/v19.0/dialog/oauth"
    default_token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    default_api_base_url = "https://graph.facebook.com/v19.0/me/feed"
