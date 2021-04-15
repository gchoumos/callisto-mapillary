from settings import *
from pprint import pprint

import json
import requests

# Let's keep data to dictionaries so that we avoid making multiple calls to the Mapillary API.
USERS = {}
SEQUENCES = {}


#
# Handle common error status codes of requests to the Mapillary API
#
def handleErrorStatusCodes(status_code):
    if status_code == 504:
        print("Request to the Mapillary API timed out ...")
    else:
        print("Request to the Mapillary API was unsuccessful with status_code: {0}".format(status_code))


#
# Get Mapillary user from username
#
# Arguments
# ---------
#   username - The username of the Mapillary user we want to search for
#
# Returns
# -------
#   0 - Success
#   1 - Error
#
# TODO
# ----
#   Handle cases when no results are returned and modify the dependent functions accordingly
#
def getMapillaryUserFromUsername(username):
    if ',' in username:
        print("List of usernames given as input. Will retrieve the first one only.")
        username = username.split(',')[0]
    # If we already have the user information, we don't have to make a new call
    if username in USERS:
        print("Details of user {0} already available. No need for an api call.")
        return 0
    # Issue a get request to search for the user.
    user = requests.get('{0}/{1}?client_id={2}&usernames={3}'.format(
        SETTINGS['base_api_url'],
        SETTINGS['users_api_url'],
        SETTINGS['client_id'],
        username
    ))

    if user.status_code != 200:
        handleErrorStatusCodes(user.status_code)
        return 1

    # add user details to the USERS dictionary
    USERS[username] = user.json()[0]
    # initialise SEQUENCES for user
    SEQUENCES[username] = {}


#
# Get User Key from username
#
# Arguments
# ---------
#    username - The username of the Mapillary user for which we want to get the user key
#
# Returns
# -------
#    The user key - if successful
#    1            - if unsuccessful
#
def getUserKey(username):
    if ',' in username:
        print("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]
    if username in USERS:
        print("User details for {0} already exist. Fetching key.".format(username))
        return USERS[username]['key']
    else:
        print("User details for {0} not available. Issuing a Mapillary API call ...".format(username))
        fetch_user = getMapillaryUserFromUsername(username)
        if fetch_user == 0:
            return USERS[username]['key']
        else:
            return 1


#
# Get user sequences
# ------------------
# Will add the user sequences on the SEQUENCES dictionary
#
# Arguments
# ---------
#    username - The username of the Mapillary user for which we want to get the sequences
#    s_format - The format of the response. Can be either 'json' (default) or 'gpx'. Note
#               that the json version includes a lot more information than the gpx which
#               only includes coordinates of the sequence. For more details see the mapillary
#               documentation.
#               When s_format is 'gpx', the response format is actually xml-like
#
# Returns
# -------
#    0 - Success
#    1 - Error
#
def getUserSequences(username,s_format='json'):
    if ',' in username:
        print("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]
    if s_format not in ['json','gpx']:
        print("Format provided is not a valid one - Returning ...")
        return 1
    # If user doesn't exist in the USERNAMES, we have to actuallly fetch that user details
    if username not in USERS:
        print("User {0} details don't exist. Fetching ...".format(username))
        if getMapillaryUserFromUsername(username) == 1:
            return 1
    if username in SEQUENCES and s_format in SEQUENCES[username]:
        print("Sequences in {0} format already exist for {1}".format(s_format,username))
        return 0
    # Issue a request to fetch the user sequences in the specified format
    if s_format == 'gpx':
        r_headers = {"Accept": "application/gpx+xml"}
    else:
        # We don't have to specify anything in particular for the json format
        r_headers = {}

    seqs = requests.get('{0}/{1}?userkeys={2}&client_id={3}&per_page=1000'.format(
        SETTINGS['base_api_url'],
        SETTINGS['sequences_api_url'],
        USERS[username]['key'],
        SETTINGS['client_id']),
        headers=r_headers
    )

    # Errors in sequences requests are unfortunately not uncommon (eg. timeouts)
    if seqs.status_code != 200:
        handleErrorStatusCodes(seqs.status_code)
        return 1

    # Add the retrieved sequences to the dictionary to make them available for processing
    if s_format == 'json':
        SEQUENCES[username][s_format] = seqs.json()
    elif s_format == 'gpx':
        SEQUENCES[username][s_format] = seqs.text
    return 0


#
# Save sequences to file
# ----------------------
# Will save the sequences of a user to a file.
# The file will in the format provided as an argument and it can be any of the following:
# - json (default)
# - gpx
#
# The filename will be of the format
#   <username>_sequences.<format>
# where <username> is the mapillary username and <format> is the format provided.
#
# Arguments
# ---------
#    username - The username of the Mapillary user for which we want to save the sequences to a file
#    s_format - The format of the output file. Can be either 'json' (default) or 'gpx'. Note
#               that the json version includes a lot more information than the gpx which
#               only includes coordinates of the sequence. For more details see the mapillary
#               documentation.
#               When s_format is 'gpx', the response format is actually xml-like
#
# Returns
# -------
#    0 - Success
#    1 - Error
#
def saveSequencesToFile(username,s_format='json'):
    if ',' in username:
        print("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]

    # Call the getUserSequences function to make sure that the sequences are available
    # in the SEQUENCES dictionary. If they are not, the relevant calls to the Mapillary
    # API will be triggered automaticaly.
    resp = getUserSequences(username, s_format=s_format)
    if resp == 1:
        print("There was an error during the retrieval of the User Sequences. Exiting ...")

    if s_format == 'json':
        with open('{0}_sequences.json'.format(username), 'w') as outfile:
            json.dump(SEQUENCES[username]['json'], outfile)
    elif s_format == 'gpx':
        with open('{0}_sequences.gpx'.format(username), 'w') as outfile:
            json.dump(SEQUENCES[username]['gpx'], outfile)
    else:
        print("Unsupported File format")



# user search test
username = 'gchoumos'
getMapillaryUserFromUsername(username)
print("Result for user {0}:".format(username))
pprint(USERS[username])

# user key test
test_user_key = getUserKey(username)
print("user key: {0}".format(test_user_key))

# sequences test
getUserSequences(username='gchoumos',s_format='gpx')
print(SEQUENCES)

# sequences to (json) file test
saveSequencesToFile('gchoumos',s_format='json')
saveSequencesToFile('gchoumos',s_format='gpx')
