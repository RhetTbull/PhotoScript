from applescript import AppleScript

from photoscript import Photos

photos = Photos()
# photos.activate()
# photos.import_photos(["/Users/rhet/Downloads/cx5.jpg"])
# photos.import_photos(["/Users/rhet/Downloads/cx5.jpg"], skip_duplicate_check=True)
# photos.import_photos(["/Users/rhet/Downloads/cx5.jpg"], album = "FooBar", skip_duplicate_check=True)
print("top level albums/folders")
albums = photos.album_names(top_level=True)
print(f"albums = {albums}")
folders = photos.folder_names(top_level=True)
print(f"folders = {folders}")

print("all albums/folders")
albums = photos.album_names()
print(f"albums = {albums}")
folders = photos.folder_names()
print(f"folders = {folders}")
