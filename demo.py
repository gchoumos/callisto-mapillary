from callisto_mapillary import *

# user search test
username = 'dandrimont'

getMapillaryUserFromUsername(username)
print("Result for user {0}:".format(username))
pprint(USERS[username])

# user key test
test_user_key = getUserKey(username)
print("user key: {0}".format(test_user_key))

# sequences test
getUserSequences(username=username,s_format='json',start_date='2018-01-01',end_date='2018-12-31')
# print(SEQUENCES)

# sequences to (json) file test
saveSequencesToFile(username,s_format='json')
# saveSequencesToFile(username,s_format='gpx')


# test merging the user sequences
_, merged = mergeUserSequences(username)

# test downloading images
downloadImagesFromImageKeys(merged['image_keys'][:5])
