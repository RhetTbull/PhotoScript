""" Provides PhotosLibrary, Photo, Album classes to interact with Photos App """

from applescript import kMissingValue

from .script_loader import run_script


class PhotosLibrary:
    def __init__(self):
        pass

    def activate(self):
        """ activate Photos.app """
        run_script("_activate")

    def quit(self):
        """ quit Photos.app """
        run_script("_quit")

    @property
    def name(self):
        """ name of Photos.app """
        return run_script("_photoslibrary_name")

    @property
    def version(self):
        """ version of Photos.app """
        return run_script("_photoslibrary_version")

    @property
    def frontmost(self):
        """ True if Photos.app is front most app otherwise False """
        return run_script("_photoslibrary_frontmost")

    @property
    def selection(self):
        """ List of Photo objects for currently selected photos or [] if no selection """
        uuids = run_script("_get_selection")
        if isinstance(uuids, list):
            return [Photo(uuid) for uuid in uuids]
        else:
            return []

    @property
    def favorites(self):
        """ Album object for the Favorites album """
        fav_id = run_script("_photoslib_favorites")
        return Album(fav_id)

    # doesn't seem to be a way to do anything with the recently deleted album except count items
    # @property
    # def recently_deleted(self):
    #     """ Album object for the Recently Deleted album """
    #     del_id = run_script("_photoslib_recently_deleted")
    #     return Album(del_id)

    def photos(self, search=None, uuid=None):
        """ List of Photo objects for items in the library
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

    def import_photos(self, photo_paths, album=None, skip_duplicate_check=False):
        """ import photos

            Args:
                photos: list of file paths to import
                album: optional, Album object for album to import into
                skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False
        """
        if album is not None:
            run_script("_import_to_album", photo_paths, album.id, skip_duplicate_check)
        else:
            run_script("_import", photo_paths, skip_duplicate_check)

    def album_names(self, top_level=False):
        """ List of album names in the Photos library

            Args:
                top_level: if True, returns only top-level albums otherwise also returns albums in sub-folders; default is False
        """
        return run_script("_album_names", top_level)

    def folder_names(self, top_level=False):
        """ List of folder names in the Photos library
        
            Args:
                top_level: if True, returns only top-level folders otherwise also returns sub-folders; default is False
        """
        return run_script("_folder_names", top_level)

    def album(self, *name, uuid=None):
        """ Album instance by name or id

            Args:
                name: name of album
                uuid: id of album
            
            Returns:
                Album object or None if album could not be found

            Raises: ValueError if both name and id passed. 
            Must pass only name or id but not both.
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
        """ list of Album objects for all albums """
        album_ids = run_script("_album_ids", top_level)
        return [Album(uuid) for uuid in album_ids]

    def create_album(self, name):
        """ creates a top level album

            Returns:
                Album object for newly created album
        """
        album_id = run_script("_create_album", name)
        return Album(album_id)

    def delete_album(self, album):
        """ deletes album (but does not delete photos in the album)

        Args:
            album: an Album object for album to delete
        """
        return run_script("_photoslib_delete_album", album.id)


class Album:
    def __init__(self, uuid):
        valuuidalbum = run_script("_album_exists", uuid)
        if valuuidalbum:
            self.id = uuid
        else:
            raise ValueError(f"Invalid album id: {uuid}")

    @property
    def uuid(self):
        """ UUID of Album """
        return self.id

    @property
    def name(self):
        """ name of album """
        name = run_script("_album_name", self.id)
        return name if name != kMissingValue else None

    @property
    def title(self):
        """ title of album (alias for Album.name) """
        return self.name

    @property
    def parent_id(self):
        """ parent container id """
        return run_script("_album_parent", self.id)

    @property
    def photos(self):
        """ list of Photo objects for photos contained in album """
        photo_ids = run_script("_album_photos", self.id)
        return [Photo(uuid) for uuid in photo_ids]

    def __len__(self):
        return run_script("_album_len", self.id)

    def add(self, photos):
        """ add photos from the library to album

        Args:
            photos: list of Photo objects to add to album
        """
        uuids = [p.id for p in photos]
        return run_script("_album_add", self.id, uuids)

    def import_photos(self, photo_paths, skip_duplicate_check=False):
        """ import photos

            Args:
                photos: list of file paths to import
                skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False
        """
        library = PhotosLibrary()
        library.import_photos(
            photo_paths, album=self, skip_duplicate_check=skip_duplicate_check
        )

    def export(self, path, original=True, edited=True, timeout=120):
        """ Export photos in album to path 

            Args:
                path: path to export to
                original: if True exports original photo
                edited: if True, exports edited version, if one exists
                timeout: number of seconds to timeout waiting for Photos to respond
            
            Returns:
                list of names of exported photos
        """
        photos = self.photos
        return [
            run_script("_photo_export", p.id, path, original, edited, timeout)
            for p in photos
        ]


class Photo:
    def __init__(self, uuid):
        valid = run_script("_photo_exists", uuid)
        if valid:
            self.id = uuid
        else:
            raise ValueError(f"Invalid photo id: {uuid}")

    @property
    def uuid(self):
        """ UUID of Photo """
        return self.id

    @property
    def name(self):
        """ name of photo """
        name = run_script("_photo_name", self.id)
        return name if name != kMissingValue else None

    @property
    def title(self):
        """ title of photo (alias for name) """
        return self.name

    @property
    def description(self):
        """ description of photo """
        descr = run_script("_photo_description", self.id)
        return descr if descr != kMissingValue else None

    @property
    def keywords(self):
        """ list of keywords for photo """
        keywords = run_script("_photo_keywords", self.id)
        if not isinstance(keywords, list):
            keywords = [keywords] if keywords != kMissingValue else []
        return keywords

    @property
    def date(self):
        """ date of photo as timezone-naive datetime.datetime object """
        return run_script("_photo_date", self.id)

    @property
    def filename(self):
        """ filename of photo """
        return run_script("_photo_filename", self.id)

    def export(self, path, original=True, edited=True, timeout=120):
        """ Export photo

            Args:
                path: path to export to
                original: if True exports original photo
                edited: if True, exports edited version, if one exists
                timeout: number of seconds to timeout waiting for Photos to respond
            
            Returns:
                name of exported photo
        """
        return run_script("_photo_export", self.id, path, original, edited, timeout)

    def duplicate(self):
        """ duplicates the photo and returns Photo object for the duplicate """
        dup_id = run_script("_photo_duplicate", self.id)
        return Photo(dup_id)
