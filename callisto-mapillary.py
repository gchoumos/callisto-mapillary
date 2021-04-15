from settings import *
from pprint import pprint

import json
import requests

# Let's keep all the users in a dictionary so that we avoid making multiple calls to the
# Mapillary API for the same user.
USERS = {}

#
# Get Mapillary user from username
#
# Arguments
# ---------
#    username - The username of the Mapillary user we want to search for
#
# Returns
# -------
#    Nothing - Only adds the user details on the USERS dictionary, if not already existing
#
def getMapillaryUserFromUsername(username):
    if ',' in username:
        print("List of usernames given as input. Will retrieve the first one only.")
        username = username.split(',')[0]
    # If we already have the user information, we don't have to make a new call
    if username in USERS:
        print("Details of user {0} already available. No need for an api call.")
        return
    # Issue a get request to search for the user.
    user = requests.get('{0}/{1}?client_id={2}&usernames={3}'.format(
        SETTINGS['base_api_url'],
        SETTINGS['users_api_url'],
        SETTINGS['client_id'],
        username))
    # add user details to the USERS dictionary
    USERS[username] = user.json()[0]


#
# Get User Key from username
#
# Arguments
# ---------
#    username - The username of the Mapillary user for which we want to get the user key
#
# Returns
# -------
#    The user key
#
def getUserKey(username):
    if ',' in username:
        print("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]
    if username in USERS:
        print("User details for {0} already exist. Fetching key.".format(username))
    else:
        print("User details for {0} not available. Issuing a Mapillary API call ...".format(username))
        getMapillaryUserFromUsername(username)
    return USERS[username]['key']

username = 'dandrimont'
test_user = getMapillaryUserFromUsername(username)
print("Result for user {0}:".format(username))
pprint(test_user)

test_user_key = getUserKey(username)
print("user key: {0}".format(test_user_key))
