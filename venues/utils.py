from django.conf import settings 
import requests
from urllib.parse import urlencode 

DOMAIN_URI_PREFIX = "theresoapp.page.link"
ANDROID_PACKAGE_NAME = "com.tracery.Reso"
IOS_BUNDLE_ID = "app.tracery.RetailReso"

def create_dynamic_link(link_base, link_paramters, title, description, image_url):
    firebase_key = settings.FIREBASE_API_KEY 
    paramters = {
        "dynamicLinkInfo": {
            "domainUriPrefix": DOMAIN_URI_PREFIX,
            "link": f"{link_base}?{urlencode(link_paramters)}",
            "androidInfo": {
                "androidPackageName": ANDROID_PACKAGE_NAME
            },
            "iosInfo": {
                "iosBundleId": IOS_BUNDLE_ID,
                "iosAppStoreId": "1518156504"
            },
            "socialMetaTagInfo": {
                "socialTitle": title,
                "socialDescription": description,
                "socialImageLink": image_url
            }
        }
    }
    request = requests.post(f"https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key={firebase_key}", json=paramters)
    response = dict(request.json())
    return response["shortLink"]
    