from applescript import AppleScript

from photoscript import PhotosLibrary

photos = PhotosLibrary()
photos.activate()
print(f"frontmost: {photos.frontmost}")
print(f"name: {photos.name}")
print(f"version: {photos.version}")

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

album = photos.album("People")
if album:
    print(album.id, album.name)
else:
    print("Could not find album")

album = photos.album(id_="8245D1B5-1B26-4858-B16E-279591641EB4/L0/040")
if album:
    print(album.id, album.name)
else:
    print("Could not find album")

album = photos.album(id_="8245D1B5-1B26-4858-B16E-279591641EB4")
if album:
    print(album.id, album.name)
else:
    print("Could not find album")


album = photos.album("FOO")
if album:
    print(album.id, album.name)
else:
    print("Could not find album")

try:
    album = photos.album(id_ = "FOO")
except ValueError:
    print("Invalid album id")

albums = photos.albums()
for a in albums:
    print(a.id, a.name, a.parent_id)


photos.quit()