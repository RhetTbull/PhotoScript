""" Provides PhotosLibrary, Photo, Album classes to interact with Photos App """

import datetime
import random
import string

from applescript import kMissingValue

from .script_loader import run_script


class AppleScriptError(Exception):
    def __init__(self, *message):
        super().__init__(*message)


class PhotosLibrary:
    def __init__(self):
        """ create new PhotosLibrary object and launch Photos """
        run_script("_photoslibrary_waitforphotos", 300)

    def activate(self):
        """ activate Photos.app """
        run_script("_photoslibrary_activate")

    def quit(self):
        """ quit Photos.app """
        run_script("_photoslibrary_quit")

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
        uuids = run_script("_photoslibrary_get_selection")
        if isinstance(uuids, list):
            return [Photo(uuid) for uuid in uuids]
        else:
            return []

    @property
    def favorites(self):
        """ Album object for the Favorites album """
        fav_id = run_script("_photoslibrary_favorites")
        return Album(fav_id)

    # doesn't seem to be a way to do anything with the recently deleted album except count items
    # @property
    # def recently_deleted(self):
    #     """ Album object for the Recently Deleted album """
    #     del_id = run_script("_photoslibrary_recently_deleted")
    #     return Album(del_id)

    def photos(self, search=None, uuid=None):
        """List of Photo objects for items in the library
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
        """import photos

        Args:
            photos: list of file paths to import
            album: optional, Album object for album to import into
            skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False
        """
        if album is not None:
            run_script(
                "_photoslibrary_import_to_album",
                photo_paths,
                album.id,
                skip_duplicate_check,
            )
        else:
            run_script("_photoslibrary_import", photo_paths, skip_duplicate_check)

    def album_names(self, top_level=False):
        """List of album names in the Photos library

        Args:
            top_level: if True, returns only top-level albums otherwise also returns albums in sub-folders; default is False
        """
        return run_script("_photoslibrary_album_names", top_level)

    def folder_names(self, top_level=False):
        """List of folder names in the Photos library

        Args:
            top_level: if True, returns only top-level folders otherwise also returns sub-folders; default is False
        """
        return run_script("_photoslibrary_folder_names", top_level)

    def album(self, *name, uuid=None, top_level=False):
        """Album instance by name or id

        Args:
            name: name of album
            uuid: id of album
            top_level: if True, searches only top level albums; default = False

        Returns:
            Album object or None if album could not be found

        Raises: ValueError if both name and id passed.
        Must pass only name or id but not both.
        If more than one album with same name, returns the first one found.
        """
        if (not name and uuid is None) or (name and uuid is not None):
            raise ValueError("Must pass only name or uuid but not both")

        if name:
            uuid = run_script("_album_by_name", name[0], top_level)
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
        album_ids = run_script("_photoslibrary_album_ids", top_level)
        return [Album(uuid) for uuid in album_ids]

    def create_album(self, name, folder=None):
        """creates an album

        Args:
            name: name of new album
            folder: Folder object in which to create new album.
                    If None, creates top-level album.  Default is None.

        Returns:
            Album object for newly created album

        Raises:
            AppleScriptError if error creating the album
        """
        if folder is None:
            album_id = run_script("_photoslibrary_create_album", name)
        else:
            album_id = run_script(
                "_photoslibrary_create_album_at_folder", name, folder.id
            )

        if album_id != 0:
            return Album(album_id)
        else:
            raise AppleScriptError(f"Could not create album {name}")

    def delete_album(self, album):
        """deletes album (but does not delete photos in the album)

        Args:
            album: an Album object for album to delete
        """
        return run_script("_photoslibrary_delete_album", album.id)

    def folder(self, *name, uuid=None, top_level=True):
        """Folder instance by name or uuid

        Args:
            name: name of folder
            uuid: id of folder
            top_level: if True, only searches top level folders by name; default is True

        Returns:
            Folder object or None if folder could not be found

        Raises: ValueError if both name and id passed.
        Must pass only name or id but not both.
        If more than one folder with same name, returns first one found.
        """
        if (not name and uuid is None) or (name and uuid is not None):
            raise ValueError("Must pass only name or uuid but not both")

        if name:
            uuid = run_script("_folder_by_name", name[0], top_level)
            if uuid != 0:
                return Folder(uuid)
            else:
                return None
        elif uuid:
            return Folder(uuid)
        else:
            raise ValueError("Invalid name or uuid")

    def folder_by_path(self, folder_path):
        """ Return folder in the library by path

        Args:
            folder_path: list of folder names, e.g. ["Folder", "SubFolder1", "SubFolder2"]

        Returns: 
            Folder object for folder at folder_path or None if not found
        """
        folder_id = run_script("_folder_by_path", folder_path)
        if folder_id != 0:
            return Folder(folder_id)
        else:
            return None

    def folders(self, top_level=True):
        """ list of Folder objects for all folders """
        folder_ids = run_script("_photoslibrary_folder_ids", top_level)
        return [Folder(uuid) for uuid in folder_ids]

    def create_folder(self, name, folder=None):
        """creates a folder

        Args:
            name: name of new folder
            folder: Folder object in which to create the new folder.
                    If None, creates top-level folder. Default is None.

        Returns:
            Folder object for newly created folder

        Raises:
            AppleScriptError if folder cannot be created
        """
        if folder is None:
            folder_id = run_script("_photoslibrary_create_folder", name)
        else:
            folder_id = run_script(
                "_photoslibrary_create_folder_at_folder", name, folder.id
            )

        if folder_id != 0:
            return Folder(folder_id)
        else:
            raise AppleScriptError(f"Could not create folder {name}")

    def delete_folder(self, folder):
        """deletes folder (Not yet implemented)

        Args:
            folder: a Folder object for folder to delete
        """
        raise NotImplementedError("delete_folder not yet implemented")
        # return run_script("_photoslibrary_delete_folder", folder.id)

    def __len__(self):
        return run_script("_photoslibrary_count")

    def _temp_album_name(self):
        """ get a temporary album name that doesn't clash with album in the library """
        temp_name = self._temp_name()
        while self.album(temp_name) is not None:
            temp_name = self._temp_name()
        return temp_name

    def _temp_name(self):
        ds = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = "".join(
            random.choice(string.ascii_lowercase + string.ascii_uppercase)
            for i in range(10)
        )
        return f"photoscript_{ds}_{random_str}"


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

    @name.setter
    def name(self, name):
        """ set name of photo """
        name = "" if name is None else name
        return run_script("_album_set_name", self.id, name)

    @property
    def title(self):
        """ title of album (alias for Album.name) """
        return self.name

    @title.setter
    def title(self, title):
        """ set title of album (alias for name) """
        name = "" if title is None else title
        return run_script("_album_set_name", self.id, name)

    @property
    def parent_id(self):
        """ parent container id """
        return run_script("_album_parent", self.id)

    # TODO: if no parent should return a "My Albums" object that contains all top-level folders/albums
    @property
    def parent(self):
        """ Return parent Folder object """
        parent_id = self.parent_id
        if parent_id != 0:
            return Folder(parent_id)
        else:
            return None

    def path_str(self, delim="/"):
        """Return internal library path to album as string.
            e.g. "Folder/SubFolder/AlbumName"

        Args:
            delim: character to use as delimiter between path elements; default is "/"

        Raises:
            ValueError if delim is not a single character
        """
        if len(delim) > 1:
            raise ValueError("delim must be single character")

        return run_script("_album_get_path", self.id, delim)

    @property
    def photos(self):
        """ list of Photo objects for photos contained in album """
        photo_ids = run_script("_album_photos", self.id)
        return [Photo(uuid) for uuid in photo_ids]

    def __len__(self):
        return run_script("_album_len", self.id)

    def add(self, photos):
        """add photos from the library to album

        Args:
            photos: list of Photo objects to add to album
        """
        uuids = [p.id for p in photos]
        return run_script("_album_add", self.id, uuids)

    def import_photos(self, photo_paths, skip_duplicate_check=False):
        """import photos

        Args:
            photos: list of file paths to import
            skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False
        """
        library = PhotosLibrary()
        library.import_photos(
            photo_paths, album=self, skip_duplicate_check=skip_duplicate_check
        )

    def export(self, path, original=True, edited=True, timeout=120):
        """Export photos in album to path

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

    # TODO: new album created at top level -- need to create new album at some path as old album
    def remove_by_id(self, photo_ids):
        """Remove photos from album.
            Note: Photos does not provide a way to remove photos from an album via AppleScript.
            This method actually creates a new Album with the same name as the original album and
            copies all photos from original album with exception of those to remove to the new album
            then deletes the old album.

        Args:
            photo_ids: list of photo ids to remove

        Returns:
            new Album object for the new album with photos removed.
        """
        photoslib = PhotosLibrary()
        new_album = photoslib.create_album(
            photoslib._temp_album_name(), folder=self.parent
        )
        old_photos = self.photos
        new_photo_uuids = [
            photo.id for photo in old_photos if photo.id not in photo_ids
        ]
        new_photos = [Photo(uuid) for uuid in new_photo_uuids]
        if new_photos:
            new_album.add(new_photos)
        name = self.name
        photoslib.delete_album(self)
        new_album.name = name
        self.id = new_album.id
        return new_album

    def remove(self, photos):
        """Remove photos from album.
            Note: Photos does not provide a way to remove photos from an album via AppleScript.
            This method actually creates a new Album with the same name as the original album and
            copies all photos from original album with exception of those to remove to the new album
            then deletes the old album.

        Args:
            photos: list of Photo objects to remove

        Returns:
            new Album object for the new album with photos removed.
        """
        photo_uuids = [photo.id for photo in photos]
        return self.remove_by_id(photo_uuids)


class Folder:
    def __init__(self, uuid):
        valid_folder = run_script("_folder_exists", uuid)
        if valid_folder:
            self.id = uuid
        else:
            raise ValueError(f"Invalid folder id: {uuid}")

    @property
    def uuid(self):
        """ UUID of folder"""
        return self.id

    @property
    def name(self):
        """ name of folder """
        name = run_script("_folder_name", self.id)
        return name if name != kMissingValue else None

    @name.setter
    def name(self, name):
        """ set name of photo """
        name = "" if name is None else name
        return run_script("_folder_set_name", self.id, name)

    @property
    def title(self):
        """ title of folder (alias for Folder.name) """
        return self.name

    @title.setter
    def title(self, title):
        """ set title of folder (alias for name) """
        name = "" if title is None else title
        return run_script("_folder_set_name", self.id, name)

    @property
    def parent_id(self):
        """ parent container id """
        return run_script("_folder_parent", self.id)

    # TODO: if no parent should return a "My Albums" object that contains all top-level folders/albums
    @property
    def parent(self):
        """ Return parent Folder object """
        parent_id = self.parent_id
        if parent_id != 0:
            return Folder(parent_id)
        else:
            return None

    def path_str(self, delim="/"):
        """Return internal library path to folder as string.
            e.g. "Folder/SubFolder"

        Args:
            delim: character to use as delimiter between path elements; default is "/"

        Raises:
            ValueError if delim is not a single character
        """
        if len(delim) > 1:
            raise ValueError("delim must be single character")

        return run_script("_folder_get_path", self.id, delim)

    def path(self):
        """Return list of Folder objects this folder is contained in.
        path()[0] is the top-level folder this folder is contained in and
        path()[-1] is the immediate parent of this folder.  Returns empty
        list if folder is not contained in another folders.
        """
        folder_path = run_script("_folder_path_ids", self.id)
        return [Folder(folder) for folder in folder_path]

    @property
    def albums(self):
        """ list of Album objects for albums contained in folder """
        album_ids = run_script("_folder_albums", self.id)
        return [Album(uuid) for uuid in album_ids]

    def album(self, name):
        """Return Album object contained in this folder for album named name
        or None if no matching album
        """
        for album in self.albums:
            if album.name == name:
                return album
        return None

    @property
    def folders(self):
        """ list of Folder objects for folders contained in folder """
        folder_ids = run_script("_folder_folders", self.id)
        return [Folder(uuid) for uuid in folder_ids]

    def folder(self, name):
        """Return Folder object for subfolder folder named name
        or None if no matching subfolder
        """
        for folder in self.folders:
            if folder.name == name:
                return folder
        return None

    def create_album(self, name):
        """creates an album in this folder

        Args:
            name: name of new album

        Returns:
            Album object for newly created album
        """
        return PhotosLibrary().create_album(name, folder=self)

    def create_folder(self, name):
        """creates a folder in this folder

        Returns:
            Folder object for newly created folder
        """
        return PhotosLibrary().create_folder(name, folder=self)

    def __len__(self):
        return run_script("_folder_len", self.id)


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

    @name.setter
    def name(self, name):
        """ set name of photo """
        name = "" if name is None else name
        return run_script("_photo_set_name", self.id, name)

    @property
    def title(self):
        """ title of photo (alias for name) """
        return self.name

    @title.setter
    def title(self, title):
        """ set title of photo (alias for name) """
        name = "" if title is None else title
        return run_script("_photo_set_name", self.id, name)

    @property
    def description(self):
        """ description of photo """
        descr = run_script("_photo_description", self.id)
        return descr if descr != kMissingValue else None

    @description.setter
    def description(self, descr):
        """ set description of photo """
        descr = "" if descr is None else descr
        return run_script("_photo_set_description", self.id, descr)

    @property
    def keywords(self):
        """ list of keywords for photo """
        keywords = run_script("_photo_keywords", self.id)
        if not isinstance(keywords, list):
            keywords = [keywords] if keywords != kMissingValue else []
        return keywords

    @keywords.setter
    def keywords(self, keywords):
        """ set keywords to list """
        if not isinstance(keywords, list):
            keywords = [keywords] if keywords is not None else []
        return run_script("_photo_set_keywords", self.id, keywords)

    @property
    def favorite(self):
        """ return favorite status (boolean) """
        return run_script("_photo_favorite", self.id)

    @favorite.setter
    def favorite(self, favorite):
        """ set favorite status (boolean) """
        favorite = True if favorite else False
        return run_script("_photo_set_favorite", self.id, favorite)

    @property
    def height(self):
        """ height of photo in pixels """
        return run_script("_photo_height", self.id)

    @property
    def width(self):
        """ width of photo in pixels """
        return run_script("_photo_width", self.id)

    @property
    def altitude(self):
        """ GPS altitude of photo in meters """
        return run_script("_photo_altitude", self.id)

    @property
    def location(self):
        """The GPS latitude and longitude, in a tuple of 2 numbers or None.
        Latitude in range -90.0 to 90.0, longitude in range -180.0 to 180.0.
        """
        location = run_script("_photo_location", self.id)
        location[0] = None if location[0] == kMissingValue else location[0]
        location[1] = None if location[1] == kMissingValue else location[1]
        return tuple(location)

    @location.setter
    def location(self, location):
        """Set GPS latitude and longitude, in a tuple of 2 numbers or None.
        Latitude in range -90.0 to 90.0, longitude in range -180.0 to 180.0.
        """

        if not isinstance(location, tuple) and location is not None:
            raise ValueError("location must be a tuple of (latitude, longitude)")

        location = (None, None) if location is None else location

        if location[0] is not None and not -90.0 <= location[0] <= 90.0:
            raise ValueError("latitude must be in range -90.0 to 90.0")

        if location[1] is not None and not -180.0 <= location[1] <= 180.0:
            raise ValueError("longitude must be in range -180.0 to 180.0")

        location = (
            kMissingValue if location[0] is None else location[0],
            kMissingValue if location[1] is None else location[1],
        )

        return run_script("_photo_set_location", self.id, location)

    @property
    def date(self):
        """ date of photo as timezone-naive datetime.datetime object """
        return run_script("_photo_date", self.id)

    @property
    def filename(self):
        """ filename of photo """
        return run_script("_photo_filename", self.id)

    def export(self, path, original=True, edited=True, timeout=120):
        """Export photo

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
