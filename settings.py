
# Setting dict with the details required to access the Mapillary API through the
# application that has been registered. The client id should be taken from the
# corresponding application details page (https://www.mapillary.com/dashboard/developers).
#
# If you are not sure what this is, please read the Mapillary documentation:
# https://www.mapillary.com/developer/api-documentation/
#
# Once your application has been created, you can either replace the value in this dictionary
# or create a "redacted_settings.py" file and overwrite it there, if you plan to publish the code
# and you don't want to expose your application's client id.
#
SETTINGS = {
    'base_api_url': 'https://a.mapillary.com/v3',
    'users_api_url': 'users',
    'sequences_api_url': 'sequences',
    'client_id': 'ReplaceWithYourApplicationClientID',
    'image_base_url': 'https://images.mapillary.com',
}

# Try to import the redacted settings, if they exist
try:
    from redacted_settings import *
except ImportError:
    print("No valid redacted settings found.")