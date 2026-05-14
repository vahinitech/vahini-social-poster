from app.services.base import BaseSocialService


class InstagramService(BaseSocialService):
    platform = "instagram"
    display_name = "Instagram Business"
    scope = "instagram_basic instagram_content_publish pages_show_list"
    default_authorize_url = "https://www.facebook.com/v19.0/dialog/oauth"
    default_token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    default_api_base_url = "https://graph.facebook.com/v19.0/me/media"
