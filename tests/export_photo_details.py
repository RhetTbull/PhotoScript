""" Use osxphotos to export details to build PHOTOS_DICT for tests """

import osxphotos

photosdb = osxphotos.PhotosDB()
for p in photosdb.photos():
    description = f'"{p.description}"' if p.description is not None else None
    title = f'"{p.title}"' if p.title is not None else None
    print(
        f'{{"uuid": "{p.uuid}/L0/001", "uuid_osxphotos": "{p.uuid}", '
        f'"filename": "{p.original_filename}", "favorite": {p.favorite}, '
        f'"title": {title}, "description": {description}, ' 
        f'"keywords": {p.keywords}, "height": {p.height}, "width": {p.width}, '
        f'"location": {p.location}, "date": "{p.date}" }},'
    )

