from settings import *
from pprint import pprint

import json
import requests
import logging
import pdb
import os

# Let's keep data to dictionaries so that we avoid making multiple calls to the Mapillary API.
USERS = {}
SEQUENCES = {}

# Initialise logging details
logging.basicConfig(
    filename='output.log',
    format='%(asctime)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S',
    level=logging.INFO
)

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
        logging.info("List of usernames given as input. Will retrieve the first one only.")
        username = username.split(',')[0]
    # If we already have the user information, we don't have to make a new call
    if username in USERS:
        logging.info("Details of user {0} already available. No need for an api call.".format(username))
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
        logging.info("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]
    if username in USERS:
        logging.info("User details for {0} already exist. Fetching key.".format(username))
        return USERS[username]['key']
    else:
        logging.info("User details for {0} not available. Issuing a Mapillary API call ...".format(username))
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
def getUserSequences(username,s_format='json',start_date='1990-01-01',end_date='2099-12-31'):
    if ',' in username:
        logging.info("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]
    if s_format not in ['json','gpx']:
        print("Format provided is not a valid one - Returning ...")
        return 1
    # If user doesn't exist in the USERNAMES, we have to actuallly fetch that user details
    if username not in USERS:
        logging.info("User {0} details don't exist. Fetching ...".format(username))
        if getMapillaryUserFromUsername(username) == 1:
            return 1
    if username in SEQUENCES and s_format in SEQUENCES[username]:
        logging.info("Sequences in {0} format already exist for {1}".format(s_format,username))
        return 0
    # Issue a request to fetch the user sequences in the specified format
    if s_format == 'gpx':
        r_headers = {"Accept": "application/gpx+xml"}
    else:
        # We don't have to specify anything in particular for the json format
        r_headers = {}

    seqs = requests.get('{0}/{1}?userkeys={2}&client_id={3}&per_page=1000&start_time={4}&end_time={5}'.format(
        SETTINGS['base_api_url'],
        SETTINGS['sequences_api_url'],
        USERS[username]['key'],
        SETTINGS['client_id'],
        start_date,
        end_date),
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
        logging.info("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]

    # Call the getUserSequences function to make sure that the sequences are available
    # in the SEQUENCES dictionary. If they are not, the relevant calls to the Mapillary
    # API will be triggered automaticaly.
    resp = getUserSequences(username, s_format=s_format)
    if resp == 1:
        logging.info("There was an error during the retrieval of the User Sequences. Exiting ...")

    if s_format == 'json':
        with open('{0}_sequences.json'.format(username), 'w') as outfile:
            json.dump(SEQUENCES[username]['json'], outfile)
    elif s_format == 'gpx':
        with open('{0}_sequences.gpx'.format(username), 'w') as outfile:
            json.dump(SEQUENCES[username]['gpx'], outfile)
    else:
        print("Unsupported File format")


#
# Merge User Sequences
# --------------------
# This function merges a set of user sequences into one
#
# Arguments
# ---------
# - username: username of the user whose sequences we want to merge
#
# Returns
# -------
# - status_code: 0 for Success / 1 for Failure
# - a dictionary with the merged user sequences
#
def mergeUserSequences(username):
    if ',' in username:
        logging.info("List of usernames given as input. Will use the first one only.")
        username = username.split(',')[0]

    if username not in SEQUENCES:
        logging.info("Sequences of user {0} don't exist. Fetching ...".format(username))
        if getUserSequences(username,s_format='json') == 1:
            return 1, {}

    # initialise an empty "merged" dictionary with only the info we want to initially keep
    merged = {
        'image_keys': [],
        'coordinates': [],
    }

    # Iterate through the sequences and merge them into 1, keeping image keys and coordinates
    # in the correct order.
    # pdb.set_trace()
    i = 1
    for seq in SEQUENCES[username]['json']['features']:
        len_image_keys = len(seq['properties']['coordinateProperties']['image_keys'])
        len_coordinates = len(seq['geometry']['coordinates'])
        if len_image_keys != len_coordinates :
            logging.warning("iter {0}: WARNING: Length of image key list({1}) not equal to the length of coordinate list ({2})"
                .format(i,len_image_keys,len_coordinates))

            #
            #  Fixing a mapillary bug when a sequence only has 1 image_key but 2 identical coordinate pairs
            #
            if len_image_keys == 1 and len_coordinates == 2 \
                and seq['geometry']['coordinates'][0] == seq['geometry']['coordinates'][1]:
                # keep only the first pair
                seq['geometry']['coordinates'] = [seq['geometry']['coordinates'][0]]
            else:
                logging.error("Merging is not possible because of inconsistency between # of images and # of coordinate pairs ...")
                return 1, {}

        merged['image_keys'] += seq['properties']['coordinateProperties']['image_keys']
        merged['coordinates'] += seq['geometry']['coordinates']
        i +=1

    return 0, merged


#
# Download images using image keys
# --------------------------------
# The purpose of this function is to download a set of images that correspond to a set of image keys.
# Will currently work for the publicly available images only.
# The images will be downloaded inside the ./downloaded_images directory which will be created if it
# doesn't already exist
#
# Arguments
# ---------
# - image_keys: keys of the images to download
#
# Returns
# -------
# - status_code: 0 for Success / 1 for Failure
#
def downloadImagesFromImageKeys(image_keys=[]):
    if len(image_keys) == 0:
        logging.info("No image keys provided for download. Returning without any further action.")
        return 0

    # Create the downloaded_images directory if it doesn't already exist
    if not os.path.exists('./downloaded_images'):
        os.makedirs('./downloaded_images')

    for key in image_keys:
        if not os.path.exists('./downloaded_images/{0}_{1}'.format(key,'thumb-320.jpg')):
            image = requests.get('{0}/{1}/{2}'.format(SETTINGS['image_base_url'],key,'thumb-320.jpg'))
            file = open("./downloaded_images/{0}_{1}".format(key,'thumb-320.jpg'),"wb")
            file.write(image.content)
            file.close()
        else:
            logging.info("Image with key {0} already exists".format(key))
