from __future__ import annotations

from app.services.facebook import FacebookService
from app.services.instagram import InstagramService
from app.services.linkedin import LinkedInService
from app.services.twitter import TwitterService


def get_service_map() -> dict[str, object]:
    return {
        "linkedin": LinkedInService(),
        "twitter": TwitterService(),
        "facebook": FacebookService(),
        "instagram": InstagramService(),
    }


PLATFORM_LABELS = {
    "linkedin": "LinkedIn company page",
    "twitter": "X / Twitter",
    "facebook": "Facebook Pages",
    "instagram": "Instagram Business",
}
