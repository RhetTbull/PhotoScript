""" Test data for Catalina/Photos 5 """

TEST_LIBRARY = "Test-PhotoScript-10.15.7.photoslibrary"
TEST_LIBRARY_OPEN = "Test-PhotoScript-10.15.7-Single-Photo.photoslibrary"

ALBUM_1_NAME = "San Juan Capistrano"
ALBUM_1_UUID = "01F18AB8-B0D7-4414-96A8-28D94AFE86BF/L0/040"
ALBUM_1_UUID_OSXPHOTOS = "01F18AB8-B0D7-4414-96A8-28D94AFE86BF"
ALBUM_1_PATH_STR = "Travel/San Juan Capistrano"
ALBUM_1_PATH_STR_COLON = "Travel:San Juan Capistrano"
ALBUM_1_PHOTO_UUIDS = [
    "EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001",
    "F8EFA39F-7D26-4DC2-82FE-CC9357F19F00/L0/001",
]
ALBUM_1_PHOTO_EXPORT_FILENAMES = ["IMG_2768.jpeg", "IMG_2774.jpeg"]
ALBUM_1_REMOVE_UUIDS = ["EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001"]
ALBUM_1_POST_REMOVE_UUIDS = ["F8EFA39F-7D26-4DC2-82FE-CC9357F19F00/L0/001"]

EMPTY_ALBUM_NAME = "Empty Album"

SELECTION_UUIDS = [
    "3A71DE26-EDEF-41D3-86C1-E8328DFC9FA0/L0/001",
    "B6DB996D-8A0A-4983-AFBD-D206B7D38A23/L0/001",
]
ALBUM_NAMES_ALL = ["Empty Album", "Farmers Market", "San Juan Capistrano"]
ALBUM_NAMES_TOP = ["Empty Album", "Farmers Market"]
FOLDER_NAMES_ALL = ["Travel", "Folder1", "SubFolder1"]
FOLDER_NAMES_TOP = ["Travel", "Folder1"]

FOLDER_1_UUID = "1FB9BF4B-3CF5-45DE-B4E7-C92047341196/L0/020"
FOLDER_1_UUID_OSXPHOTOS = "1FB9BF4B-3CF5-45DE-B4E7-C92047341196"
FOLDER_1_NAME = "Folder1"
FOLDER_1_LEN = 1
FOLDER_1_SUBFOLDERS = ["SubFolder1"]
FOLDER_2_UUID = "9BC83BEA-7598-4846-BBD7-AB14BE771825/L0/020"
FOLDER_2_NAME = "SubFolder1"
FOLDER_2_PATH_STR = "Folder1/SubFolder1"
FOLDER_2_PATH_STR_COLON = "Folder1:SubFolder1"
FOLDER_2_PATH = ["Folder1"]
FOLDER_2_LEN = 0
FOLDER_3_UUID = "3205FEEF-B22D-43D6-8D31-9A4D112B67E3/L0/020"
FOLDER_3_NAME = "Travel"
FOLDER_3_LEN = 1
FOLDER_3_ALBUMS = ["San Juan Capistrano"]

PHOTO_ADD_UUID = "3A71DE26-EDEF-41D3-86C1-E8328DFC9FA0/L0/001"
PHOTOS_FAVORITES = ["IMG_2510.JPG", "IMG_2768.JPG"]
PHOTOS_FAVORITES_SET = ["IMG_2242.JPG", "IMG_2510.JPG"]
PHOTO_FAVORITES_SET_UUID = "1CD1B172-C94B-4093-A303-EE24FE7EEF60/L0/001"
PHOTO_FAVORITES_UNSET_UUID = "EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001"

NUM_PHOTOS = 5  # total number of photos in test library

PHOTOS_FILENAMES = [
    "IMG_2242.JPG",
    "IMG_2510.JPG",
    "IMG_2768.JPG",
    "IMG_2774.JPG",
    "IMG_0096.jpeg",
]
PHOTOS_UUID = [
    "B6DB996D-8A0A-4983-AFBD-D206B7D38A23/L0/001",
    "EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001",
]
PHOTOS_UUID_FILENAMES = ["IMG_2510.JPG", "IMG_2768.JPG"]

PHOTO_EXPORT_UUID = "B6DB996D-8A0A-4983-AFBD-D206B7D38A23/L0/001"
PHOTO_EXPORT_FILENAME = ["IMG_2510.jpeg"]
PHOTO_EXPORT_FILENAME_ORIGINAL = ["IMG_2510.jpeg"]
PHOTO_EXPORT_2_FILENAMES = ["IMG_2510.jpeg", "IMG_2510 (1).jpeg"]
PHOTO_EXPORT_2_FILENAMES_ORIGINAL = ["IMG_2510.jpeg", "IMG_2510 (1).jpeg"]

PHOTOS_PLANTS = ["IMG_2242.JPG"]
FOLDER_UUID = "3205FEEF-B22D-43D6-8D31-9A4D112B67E3/L0/020"  # Travel
FOLDER_NAME = "Travel"

IMPORT_PATHS = ["tests/test_images/IMG_2608.JPG"]
IMPORT_PHOTOS = ["IMG_2608.JPG"]

FIND_FILES = [
    "IMG_2242.JPG",
    "IMG_2510.JPG",
    "IMG_2608.JPG",
    "IMG_2768.JPG",
    "IMG_2774.JPG",
]

PHOTOS_DICT = [
    {
        "uuid": "F8EFA39F-7D26-4DC2-82FE-CC9357F19F00/L0/001",
        "uuid_osxphotos": "F8EFA39F-7D26-4DC2-82FE-CC9357F19F00",
        "filename": "IMG_2774.JPG",
        "favorite": False,
        "title": "",
        "description": "",
        "keywords": ["travel"],
        "height": 4032,
        "width": 3024,
        "location": (33.50126666999999, -117.66378833000002),
        "date": "2020-08-12 15:43:32",
        "altitude": 29.4,
        "albums": ["San Juan Capistrano"],
    },
    {
        "uuid": "EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001",
        "uuid_osxphotos": "EECD91FE-D716-48F2-A62C-A4D558ACD52E",
        "filename": "IMG_2768.JPG",
        "favorite": True,
        "title": "",
        "description": "",
        "keywords": ["travel"],
        "height": 3024,
        "width": 3024,
        "location": (33.501921669999994, -117.66425333000002),
        "date": "2020-08-12 14:12:15",
        "altitude": 32.9,
        "albums": ["San Juan Capistrano"],
    },
    {
        "uuid": "B6DB996D-8A0A-4983-AFBD-D206B7D38A23/L0/001",
        "uuid_osxphotos": "B6DB996D-8A0A-4983-AFBD-D206B7D38A23",
        "filename": "IMG_2510.JPG",
        "favorite": True,
        "title": "",
        "description": "",
        "keywords": [],
        "height": 3024,
        "width": 4032,
        "location": (33.82677, -118.32748332999999),
        "date": "2020-07-18 12:00:20",
        "altitude": 26.1,
        "albums": ["Farmers Market"],
    },
    {
        "uuid": "1CD1B172-C94B-4093-A303-EE24FE7EEF60/L0/001",
        "uuid_osxphotos": "1CD1B172-C94B-4093-A303-EE24FE7EEF60",
        "filename": "IMG_2242.JPG",
        "favorite": False,
        "title": "Living Wall",
        "description": "Wall of plants at Botanical Garden",
        "keywords": [],
        "height": 3024,
        "width": 3024,
        "location": (33.782425, -118.34803833000001),
        "date": "2020-07-05 10:07:04",
        "altitude": 130.6,
        "albums": [],
    },
    {
        "uuid": "3A71DE26-EDEF-41D3-86C1-E8328DFC9FA0/L0/001",
        "uuid_osxphotos": "3A71DE26-EDEF-41D3-86C1-E8328DFC9FA0",
        "filename": "IMG_0096.jpeg",
        "favorite": False,
        "title": "",
        "description": "",
        "keywords": [],
        "height": 903,
        "width": 701,
        "location": (None, None),
        "date": "2020-09-07 07:27:40",
        "altitude": None,
        "albums": [],
    },
]
