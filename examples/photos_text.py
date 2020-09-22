""" Extract text from images in Photos.app using tesseract and 
    update Photo description with extracted text """

import datetime
import pathlib

import osxphotos
import pytesseract
import tinydb
from PIL import Image

import photoscript

photosdb = osxphotos.PhotosDB()
library = pathlib.Path(photosdb.library_path)
db_name = f"{library.parent}/.{library.stem}.photos_text_db"

print(f"Processing Photos library '{library}'")

print(f"Loading photos_text database {db_name}")
db = tinydb.TinyDB(db_name)
query = tinydb.Query()

photoapp = photoscript.PhotosLibrary()
count = 0
text_count = 0
for photo in photosdb.photos():
    count += 1
    if db.search(query.uuid == photo.uuid):
        print(
            f"Skipping already processed photo {photo.original_filename}, {photo.uuid}"
        )
        continue
    if not photo.path:
        print(f"Skipping missing photo {photo.original_filename}, {photo.uuid}")
        db.insert(
            {
                "uuid": photo.uuid,
                "date": datetime.datetime.now().isoformat(),
                "text": None,
                "previous_text": photo.description,
                "missing": True,
            }
        )
        continue

    print(f"Looking for text in photo {photo.original_filename}, {photo.uuid}")
    try:
        text = pytesseract.image_to_string(Image.open(photo.path)).strip()
        text = " ".join(text.split())
    except:
        text = None
    if text:
        text_count += 1
        print(f"Found text in photo: {text}")
        photo2 = photoscript.Photo(photo.uuid)
        descr = photo2.description
        new_descr = descr + " " + text if descr else text
        photo2.description = new_descr
        print(f"Updated description to: {new_descr}")
        db.insert(
            {
                "uuid": photo.uuid,
                "date": datetime.datetime.now().isoformat(),
                "text": text,
                "previous_text": descr,
                "missing": False,
            }
        )


print("Done")
if count:
    print(f"Processed {count} photos, updated text in {text_count}")
else:
    print(f"No photos to process")
