from app.services.base import BaseSocialService


class LinkedInService(BaseSocialService):
    platform = "linkedin"
    display_name = "LinkedIn"
    scope = "openid profile w_member_social"
    default_authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
    default_token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    default_api_base_url = "https://api.linkedin.com/v2/ugcPosts"
