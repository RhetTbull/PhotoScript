""" PhotosLibrary, Photo, Album classes """

from .script_loader import run_script


class PhotosLibrary:
    def __init__(self):
        pass

    def activate(self):
        """ activate Photos.app """
        run_script("_activate")

    def quit(self):
        """ quit Photos """
        run_script("_quit")

    @property
    def name(self):
        """ name of Photos app """
        return run_script("_photoslibrary_name")

    @property
    def version(self):
        """ version of Photos app """
        return run_script("_photoslibrary_version")

    @property
    def frontmost(self):
        """ returns True if Photos app is frontmost app otherwise False """
        return run_script("_photoslibrary_frontmost")

    def photos(self, search=None, uuid=None):
        """ Return list of Photo objects for items in the library
            Note: for a large library, calling photos() may run a *very* long time (minutes)

            Args:
                search: optional text string to search for (returns matching items)
                uuid: list of UUIDs to get
                you may pass search or uuid but not both
        
            Returns:
                List of Photo objects or [] if no photos found
            
            Raises: ValueError if both search and uuid are passed
        """
        if search is not None and uuid:
            raise ValueError("Cannot pass both search and uuid")

        if search is None and not uuid:
            # return all photos
            photo_ids = run_script("_photoslibrary_get_all_photos")
        elif search is not None:
            # search for text
            photo_ids = run_script("_photoslibrary_search_photos", search)
        else:
            # search by uuid
            photo_ids = uuid

        return [Photo(uuid) for uuid in photo_ids]

    def import_photos(self, photos, album=None, skip_duplicate_check=False):
        """ import photos

            Args:
                photos: list of file paths to import
                album: optional, name of album to import into (album must exist in Photos)
                skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False
        """
        if album is not None:
            run_script("_import_to_album", photos, album, skip_duplicate_check)
        else:
            run_script("_import", photos, skip_duplicate_check)

    def album_names(self, top_level=False):
        """ Return list of album names in the Photos library 
            Args:
                top_level: if True, returns only top-level albums otherwise also returns albums in sub-folders; default is False
        """
        return run_script("_album_names", top_level)

    def folder_names(self, top_level=False):
        """ Return list of folder names in the Photos library
        
            Args:
                top_level: if True, returns only top-level folders otherwise also returns sub-folders; default is False
        """
        return run_script("_folder_names", top_level)

    def album(self, *name, uuid=None):
        """ Return Album instance by name or id

            Args:
                name: name of album
                uuid: id of album
                Must pass only name or id but not both
            
            Returns:
                Album object or None if album could not be found

            Raises: ValueError if both name and id passed
        """
        if (not name and uuid is None) or (name and uuid is not None):
            raise ValueError("Must pass only name or uuid but not both")

        if name:
            uuid = run_script("_album_by_name", name[0])
            if uuid != 0:
                return Album(uuid)
            else:
                return None
        elif uuid:
            return Album(uuid)
        else:
            raise ValueError("Invalid name or uuid")

    def albums(self, top_level=False):
        """ return list of Album objects for all albums """
        album_ids = run_script("_album_ids", top_level)
        return [Album(uuid) for uuid in album_ids]

    def create_album(self, name):
        """ creates a top level album

            Returns:
                Album object for newly created album
        """
        album_id = run_script("_create_album", name)
        return Album(album_id)

class Album:
    def __init__(self, uuid):
        valuuidalbum = run_script("_album_exists", uuid)
        if valuuidalbum:
            self.id = self.uuid = uuid
        else:
            raise ValueError(f"Invalid album id: {uuid}")

    @property
    def name(self):
        return run_script("_album_name", self.id)

    @property
    def title(self):
        return self.name

    @property
    def parent_id(self):
        """ return parent container id """
        return run_script("_album_parent", self.id)

    @property
    def photos(self):
        """ return list of Photo objects for photos contained in album """
        photo_ids = run_script("_album_photos", self.id)
        return [Photo(uuid) for uuid in photo_ids]

    def __len__(self):
        return run_script("_album_len", self.id)


class Photo:
    def __init__(self, uuid):
        valid = run_script("_photo_exists", uuid)
        if valid:
            self.id = self.uuid = uuid
        else:
            raise ValueError(f"Invalid photo id: {uuid}")

    @property
    def name(self):
        return run_script("_photo_name", self.id)

    @property
    def title(self):
        return self.name

    @property
    def description(self):
        return run_script("_photo_description", self.id)

    @property
    def keywords(self):
        return run_script("_photo_keywords", self.id)

    @property
    def date(self):
        return run_script("_photo_date", self.id)
