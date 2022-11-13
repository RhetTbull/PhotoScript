""" Provides PhotosLibrary, Photo, Album classes to interact with Photos App """

import datetime
import glob
import os
import pathlib
import random
import string
import tempfile
from subprocess import run

from applescript import AppleScript, kMissingValue

from photoscript.utils import ditto, findfiles

from .script_loader import run_script

""" In Catalina / Photos 5+, UUIDs in AppleScript have suffix that doesn't 
    appear in actual database value.  These need to be dropped to be compatible
    with osxphotos """
UUID_SUFFIX_PHOTO = "/L0/001"
UUID_SUFFIX_ALBUM = "/L0/040"
UUID_SUFFIX_FOLDER = "/L0/020"


class AppleScriptError(Exception):
    def __init__(self, *message):
        super().__init__(*message)


class PhotosLibrary:
    def __init__(self):
        """create new PhotosLibrary object and launch Photos"""
        run_script("photosLibraryWaitForPhotos", 300)
        self._version = str(run_script("photosLibraryVersion"))

    def activate(self):
        """activate Photos.app"""
        run_script("photosLibraryActivate")

    def quit(self):
        """quit Photos.app"""
        run_script("photosLibraryQuit")

    def open(self, library_path, delay=10):
        """open a library and wait for delay for user to acknowledge in Photos"""
        # Note: Unlike the other AppleScript scripts, this one is not included in photoscript.applescript
        # because, for reasons I cannot explain, it fails to run if included there
        if not pathlib.Path(library_path).is_dir():
            raise ValueError(f"{library_path} does not appear to be a Photos library")
        self.activate()
        script = AppleScript(
            f"""
            set tries to 0
            repeat while tries < 5
                try
                    tell application "Photos"
                        activate
                        delay 3 
                        open POSIX file "{library_path}"
                        delay {delay}
                    end tell
                    set tries to 5
                on error
                    set tries to tries + 1
                end try
            end repeat
        """
        )
        script.run()

    @property
    def running(self):
        """True if Photos is running, otherwise False"""
        return run_script("photosLibraryIsRunning")

    def hide(self):
        """Tell Photos to hide its window"""
        run_script("photosLibraryHide")

    @property
    def hidden(self):
        """True if Photos is hidden (or not running), False if Photos is visible"""
        return run_script("photosLibraryIsHidden")

    @property
    def name(self):
        """name of Photos.app"""
        return run_script("photosLibraryName")

    @property
    def version(self):
        """version of Photos.app as str"""
        return self._version

    @property
    def frontmost(self):
        """True if Photos.app is front most app otherwise False"""
        return run_script("photosLibraryIsFrontMost")

    @property
    def selection(self):
        """List of Photo objects for currently selected photos or [] if no selection"""
        uuids = run_script("photosLibraryGetSelection")
        return [Photo(uuid) for uuid in uuids]

    @property
    def favorites(self):
        """Album object for the Favorites album"""
        fav_id = run_script("photosLibraryFavorites")
        return Album(fav_id)

    # doesn't seem to be a way to do anything with the recently deleted album except count items
    # @property
    # def recently_deleted(self):
    #     """ Album object for the Recently Deleted album """
    #     del_id = run_script("photosLibraryRecentlyDeleted")
    #     return Album(del_id)

    def photos(self, search=None, uuid=None, range_=None):
        """Returns a generator that yields Photo objects for media items in the library.

        Args:
            search: optional text string to search for (returns matching items)
            uuid: optional list of UUIDs to get
            range\_: optional list of [start, stop] sequence of photos to get

        Returns:
            Generator that yields Photo objects

        Raises:
            ValueError if more than one of search, uuid, range\_ passed or invalid range\_
            TypeError if list not passed for range\_

        Note: photos() returns a generator instead of a list because retrieving all the photos
        from a large Photos library can take a very long time--on my system, the rate is about 1
        per second; this is limited by the Photos AppleScript interface and I've not found
        anyway to speed it up.  Using a generator allows you process photos individually rather
        than waiting, possibly hours, for Photos to return the results.

        range\_ works like python's range function.  Thus range\_=[0,4] will return
        Photos 0, 1, 2, 3; range\_=[10] returns the first 10 photos in the library;
        range\_ start must be in range 0 to len(PhotosLibrary())-1,
        stop in range 1 to len(PhotosLibrary()).  You may be able to optimize the speed by which
        photos are return by chunking up requests in batches of photos using range\_,
        e.g. request 10 photos at a time.
        """

        if len([x for x in [search, uuid, range_] if x]) > 1:
            raise ValueError("Cannot pass more than one of search, uuid, range_")

        if not any([search, uuid, range_]):
            return self._iterphotos()

        if search is not None:
            # search for text
            photo_ids = run_script("photosLibrarySearchPhotos", search)
        elif uuid:
            # search by uuid
            photo_ids = uuid
        else:
            # search by range
            if not isinstance(range_, list):
                raise TypeError("range_ must be a list")

            if not (1 <= len(range_) <= 2):
                raise ValueError("invalid range, must be list of len 1 or 2")

            if len(range_) == 1:
                start = 0
                stop = range_[0]
            else:
                start, stop = range_

            if start > stop:
                raise ValueError("start range must be <= stop range")

            count = len(self)
            if not ((0 <= start <= count - 1) and (1 <= stop <= count)):
                raise ValueError(
                    f"invalid range: valid range is start: 0 to {count-1}, stop: 1 to {count}"
                )

            photo_ids = run_script("photosLibraryGetPhotoByRange", start + 1, stop)

        if photo_ids:
            return self._iterphotos(uuids=photo_ids)
        else:
            return []

    def _iterphotos(self, uuids=None):
        if uuids:
            for uuid in uuids:
                yield Photo(uuid)
        else:
            # return all photos via generator
            count = len(self)
            for x in range(1, count + 1):
                # AppleScript list indexes start at 1
                photo_id = run_script("photosLibraryGetPhotoByRange", x, x)[0]
                yield Photo(photo_id)

    def import_photos(self, photo_paths, album=None, skip_duplicate_check=False):
        """import photos

        Args:
            photo_paths: list of file paths to import as str or pathlib.Path
            album: optional, Album object for album to import into
            skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False.

        Returns:
            list of Photo objects for imported photos

        NOTE: If you attempt to import a duplicate photo and skip_duplicate_check != True,
            Photos will block with drop-down sheet until the user clicks "Cancel, Import, or Don't Import."
        """
        # stringify paths in case pathlib.Path paths are passed
        photo_paths = [str(photo_path) for photo_path in photo_paths]
        if album is not None:
            photo_ids = run_script(
                "photosLibraryImportToAlbum",
                photo_paths,
                album.id,
                skip_duplicate_check,
            )
        else:
            photo_ids = run_script(
                "photosLibraryImport", photo_paths, skip_duplicate_check
            )

        return [Photo(photo) for photo in photo_ids]

    def album_names(self, top_level=False):
        """List of album names in the Photos library

        Args:
            top_level: if True, returns only top-level albums otherwise also returns albums in sub-folders; default is False
        """
        return run_script("photosLibraryAlbumNames", top_level)

    def folder_names(self, top_level=False):
        """List of folder names in the Photos library

        Args:
            top_level: if True, returns only top-level folders otherwise also returns sub-folders; default is False
        """
        return run_script("photosLibraryFolderNames", top_level)

    def album(self, *name, uuid=None, top_level=False):
        """Album instance by name or id

        Args:
            name: name of album
            uuid: id of album
            top_level: if True, searches only top level albums; default = False

        Returns:
            Album object or None if album could not be found

        Raises:
            ValueError if both name and id passed or neither passed.

        Must pass only name or id but not both.
        If more than one album with same name, returns the first one found.
        """
        if (not name and uuid is None) or (name and uuid is not None):
            raise ValueError("Must pass only name or uuid but not both")

        if name:
            uuid = run_script("albumByName", name[0], top_level)
            if uuid != 0:
                return Album(uuid)
            else:
                return None
        else:
            return Album(uuid)

    def albums(self, top_level=False):
        """list of Album objects for all albums"""
        album_ids = run_script("photosLibraryAlbumIDs", top_level)
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
            album_id = run_script("photosLibraryCreateAlbum", name)
        else:
            album_id = run_script("photosLibraryCreateAlbumAtFolder", name, folder.id)

        if album_id != 0:
            return Album(album_id)
        else:
            raise AppleScriptError(f"Could not create album {name}")

    def delete_album(self, album):
        """deletes album (but does not delete photos in the album)

        Args:
            album: an Album object for album to delete
        """
        return run_script("photosLibraryDeleteAlbum", album.id)

    def folder(self, *name, uuid=None, top_level=True):
        """Folder instance by name or uuid

        Args:
            name: name of folder
            uuid: id of folder
            top_level: if True, only searches top level folders by name; default is True

        Returns:
            Folder object or None if folder could not be found

        Raises:
            ValueError if both name and id passed or neither passed.

        Must pass only name or id but not both.
        If more than one folder with same name, returns first one found.
        """
        if (not name and uuid is None) or (name and uuid is not None):
            raise ValueError("Must pass only name or uuid but not both")

        if name:
            uuid = run_script("folderByName", name[0], top_level)
            if uuid != 0:
                return Folder(uuid)
            else:
                return None
        else:
            return Folder(uuid)

    def folder_by_path(self, folder_path):
        """Return folder in the library by path

        Args:
            folder_path: list of folder names in descending path order, e.g. ["Folder", "SubFolder1", "SubFolder2"]

        Returns:
            Folder object for folder at folder_path or None if not found
        """
        folder_id = run_script("folderByPath", folder_path)
        if folder_id != 0:
            return Folder(folder_id)
        else:
            return None

    def folders(self, top_level=True):
        """list of Folder objects for all folders"""
        folder_ids = run_script("photosLibraryFolderIDs", top_level)
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
            folder_id = run_script("photosLibraryCreateFolder", name)
        else:
            folder_id = run_script("photosLibraryCreateFolderAtFolder", name, folder.id)

        if folder_id != 0:
            return Folder(folder_id)
        else:
            raise AppleScriptError(f"Could not create folder {name}")

    def make_folders(self, folder_path):
        """Recursively makes folders and subfolders.  Works similar to os.makedirs_.
        If any component of folder_path already exists, does not raise error.

        .. _os.makedirs: https://docs.python.org/3/library/os.html#os.makedirs

        Args:
            folder_path: list of folder names in descending path order, e.g. ["Folder", "SubFolder1", "SubFolder2"]

        Returns:
            Folder object for the final sub folder

        Raises:
            ValueError if folder_path is empty
            TypeError if folder_path is not a list
        """
        if not isinstance(folder_path, list):
            raise TypeError("list expected for folder_path")
        if not folder_path:
            raise ValueError("no values in folder_path")

        folder = self.folder(folder_path[0], top_level=True)
        if folder is None:
            folder = self.create_folder(folder_path[0])
        for subfolder_name in folder_path[1:]:
            subfolder = folder.folder(subfolder_name)
            if subfolder is None:
                subfolder = folder.create_folder(subfolder_name)
            folder = subfolder
        return folder

    def make_album_folders(self, album_name, folder_path):
        """Make album in a folder path.  If either the album or any component of the
           folder path doesn't exist, it will be created.  If album or folder path
           does exist, no duplicate is created.  Folder path is created recursively
           if needed.

        Args:
            album_name: name of album to create.  If album already exists, returns existing album.
            folder_path: list of folder names in descending path order, e.g. ["Folder", "SubFolder1", "SubFolder2"].

        Returns:
            Album object.

        Raises:
            ValueError if folder_path is empty or album_name is None.
            TypeError if folder_path is not a list.
        """
        if album_name is None or not len(album_name):
            raise ValueError("album_name must not be None")
        if not isinstance(folder_path, list):
            raise TypeError("list expected for folder_path")
        if not folder_path:
            raise ValueError("no values in folder_path")

        folder = self.make_folders(folder_path)
        album = folder.album(album_name)
        if album is None:
            album = folder.create_album(album_name)
        return album

    def delete_folder(self, folder):
        """Deletes folder

        Args:
            folder: a Folder object for folder to delete
        """
        return run_script("photosLibraryDeleteFolder", folder.id)

    def __len__(self):
        return run_script("photosLibraryCount")

    def _temp_album_name(self):
        """get a temporary album name that doesn't clash with album in the library"""
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

    def _export_photo(
        self,
        photo,
        export_path,
        original=False,
        overwrite=False,
        timeout=120,
        reveal_in_finder=False,
    ):
        """Export photo to export_path

        Args:
            photo: Photo object to export
            export_path: path to export to
            original: if True, export original image, otherwise export current image; default = False
            overwrite: if True, export will overwrite a file of same name as photo in export_path; default = False
            timeout: number of seconds to wait for Photos to complete export before timing out; default = 120
            reveal_in_finder: if True, will open Finder with exported items selected when done; default = False

        Returns:
            List of full paths of exported photos.  There may be more than one photo exported due
            to live images and burst images.

        Raises:
            ValueError if export_path is not a valid directory

        Note: Photos always exports as high-quality JPEG unless original=True.
        If original=True, will export all burst images for burst photos and
        live movie for live photos.  If original=False, only the primary image from a
        burst set will be exported for burst photos and the live movie component of a
        live image will not be exported, only the JPEG component.
        """

        dest = pathlib.Path(export_path)
        if not dest.is_dir():
            raise ValueError(f"export_path {export_path} must be a directory")

        edited = not original

        tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_")

        # export original
        filename = run_script(
            "photoExport", photo.id, tmpdir.name, original, edited, timeout
        )

        exported_paths = []
        if filename is not None:
            # need to find actual filename as sometimes Photos renames JPG to jpeg on export
            # may be more than one file exported (e.g. if Live Photo, Photos exports both .jpeg and .mov)
            # TemporaryDirectory will cleanup on return
            files = glob.glob(os.path.join(tmpdir.name, "*"))
            seen_files = {}
            for fname in files:
                path = pathlib.Path(fname)
                dest_new = dest / path.name
                if not overwrite:
                    # ensure there are no name collisions on export
                    try:
                        dest_update = seen_files[path.stem]
                    except KeyError:
                        count = 1
                        dest_files = findfiles(
                            f"{dest_new.stem}*", str(dest_new.parent)
                        )
                        dest_files = [pathlib.Path(f).stem.lower() for f in dest_files]
                        dest_update = dest_new.stem
                        while dest_update.lower() in dest_files:
                            dest_update = f"{dest_new.stem} ({count})"
                            count += 1
                        seen_files[path.stem] = dest_update
                    dest_new = dest_new.parent / f"{dest_update}{dest_new.suffix}"
                ditto(str(path), str(dest_new))
                exported_paths.append(str(dest_new))
            if reveal_in_finder:
                run_script("revealInFinder", exported_paths)
        return exported_paths


class Album:
    def __init__(self, uuid):
        id_ = uuid
        # check to see if we need to add UUID suffix
        if float(PhotosLibrary().version) >= 5.0:
            if len(uuid.split("/")) == 1:
                # osxphotos style UUID without the suffix
                id_ = f"{uuid}{UUID_SUFFIX_ALBUM}"
            else:
                uuid = uuid.split("/")[0]

        valuuidalbum = run_script("albumExists", id_)
        if valuuidalbum:
            self.id = id_
            self._uuid = uuid
        else:
            raise ValueError(f"Invalid album id: {uuid}")

    @property
    def uuid(self):
        """UUID of Album (read only)"""
        return self._uuid

    @property
    def name(self):
        """name of album (read/write)"""
        name = run_script("albumName", self.id)
        return name if name != kMissingValue else ""

    @name.setter
    def name(self, name):
        """set name of album"""
        name = "" if name is None else name
        return run_script("albumSetName", self.id, name)

    @property
    def title(self):
        """title of album (alias for Album.name)"""
        return self.name

    @title.setter
    def title(self, title):
        """set title of album (alias for name)"""
        name = "" if title is None else title
        return run_script("albumSetName", self.id, name)

    @property
    def parent_id(self):
        """parent container id"""
        return run_script("albumParent", self.id)

    # TODO: if no parent should return a "My Albums" object that contains all top-level folders/albums
    @property
    def parent(self):
        """Return parent Folder object"""
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

        return run_script("albumGetPath", self.id, delim)

    def photos(self):
        """list of Photo objects for photos contained in album"""
        photo_ids = run_script("albumPhotes", self.id)
        return [Photo(uuid) for uuid in photo_ids]

    def add(self, photos):
        """add photos from the library to album

        Args:
            photos: list of Photo objects to add to album

        Returns:
            list of Photo objects for added photos
        """
        uuids = [p.id for p in photos]
        added_ids = run_script("albumAdd", self.id, uuids)
        return [Photo(uuid) for uuid in added_ids]

    def import_photos(self, photo_paths, skip_duplicate_check=False):
        """import photos

        Args:
            photos: list of file paths to import
            skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False

        Returns:
            list of Photo objects for imported photos
        """
        library = PhotosLibrary()
        return library.import_photos(
            photo_paths, album=self, skip_duplicate_check=skip_duplicate_check
        )

    def export(
        self,
        export_path,
        original=False,
        overwrite=False,
        timeout=120,
        reveal_in_finder=False,
    ):
        """Export photos in album to path

        Args:
            photo: Photo object to export
            export_path: path to export to
            original: if True, export original image, otherwise export current image; default = False
            overwrite: if True, export will overwrite a file of same name as photo in export_path; default = False
            timeout: number of seconds to wait for Photos to complete export (for each photo) before timing out; default = 120
            reveal_in_finder: if True, will open Finder with exported items selected when done; default = False

        Returns:
            List of full paths of exported photos.  There may be more than one photo exported due
            to live images and burst images.

        Raises:
            ValueError if export_path is not a valid directory

        Note: Photos always exports as high-quality JPEG unless original=True.
        If original=True, will export all burst images for burst photos and
        live movie for live photos.  If original=False, only the primary image from a
        burst set will be exported for burst photos and the live movie component of a
        live image will not be exported, only the JPEG component.
        """
        exported_photos = []
        for photo in self.photos():
            exported_photos.extend(
                photo.export(
                    export_path=export_path,
                    original=original,
                    overwrite=overwrite,
                    timeout=timeout,
                )
            )
        if reveal_in_finder and exported_photos:
            run_script("revealInFinder", exported_photos)
        return exported_photos

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
        old_photos = self.photos()
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
        self._uuid = new_album.uuid
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

    def spotlight(self):
        """spotlight the album in Photos"""
        run_script("albumSpotlight", self.id)

    def __len__(self):
        return run_script("albumCount", self.id)


class Folder:
    def __init__(self, uuid):
        id_ = uuid
        # check to see if we need to add UUID suffix
        if float(PhotosLibrary().version) >= 5.0:
            if len(uuid.split("/")) == 1:
                # osxphotos style UUID without the suffix
                id_ = f"{uuid}{UUID_SUFFIX_FOLDER}"
            else:
                uuid = uuid.split("/")[0]

        valid_folder = run_script("folderExists", id_)
        if valid_folder:
            self.id = id_
            self._uuid = uuid
        else:
            raise ValueError(f"Invalid folder id: {uuid}")

    @property
    def uuid(self):
        """UUID of folder"""
        return self._uuid

    @property
    def name(self):
        """name of folder (read/write)"""
        name = run_script("folderName", self.id)
        return name if name != kMissingValue else ""

    @name.setter
    def name(self, name):
        """set name of photo"""
        name = "" if name is None else name
        return run_script("folderSetName", self.id, name)

    @property
    def title(self):
        """title of folder (alias for Folder.name)"""
        return self.name

    @title.setter
    def title(self, title):
        """set title of folder (alias for name)"""
        name = "" if title is None else title
        return run_script("folderSetName", self.id, name)

    @property
    def parent_id(self):
        """parent container id"""
        return run_script("folderParent", self.id)

    # TODO: if no parent should return a "My Albums" object that contains all top-level folders/albums?
    @property
    def parent(self):
        """Return parent Folder object"""
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

        return run_script("folderGetPath", self.id, delim)

    def path(self):
        """Return list of Folder objects this folder is contained in.
        path()[0] is the top-level folder this folder is contained in and
        path()[-1] is the immediate parent of this folder.  Returns empty
        list if folder is not contained in another folders.
        """
        folder_path = run_script("folderPathIDs", self.id)
        return [Folder(folder) for folder in folder_path]

    @property
    def albums(self):
        """list of Album objects for albums contained in folder"""
        album_ids = run_script("folderAlbums", self.id)
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
    def subfolders(self):
        """list of Folder objects for immediate sub-folders contained in folder"""
        folder_ids = run_script("folderFolders", self.id)
        return [Folder(uuid) for uuid in folder_ids]

    def folder(self, name):
        """Folder object for first subfolder folder named name.

        Args:
            name: name of folder to to return

        Returns:
            Folder object for first subfolder who's name matches name or None if not found
        """
        for folder in self.subfolders:
            if folder.name == name:
                return folder
        return None

    def create_album(self, name):
        """Creates an album in this folder

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

    def spotlight(self):
        """spotlight the folder in Photos"""
        run_script("folderSpotlight", self.id)

    def __len__(self):
        return run_script("folderCount", self.id)


class Photo:
    def __init__(self, uuid):
        id_ = uuid
        # check to see if we need to add UUID suffix
        if float(PhotosLibrary().version) >= 5.0:
            if len(uuid.split("/")) == 1:
                # osxphotos style UUID without the suffix
                id_ = f"{uuid}{UUID_SUFFIX_PHOTO}"
            else:
                uuid = uuid.split("/")[0]
        valid = run_script("photoExists", uuid)
        if valid:
            self.id = id_
            self._uuid = uuid
        else:
            raise ValueError(f"Invalid photo id: {uuid}")

    @property
    def uuid(self):
        """UUID of Photo"""
        return self._uuid

    @property
    def name(self):
        """name of photo (read/write)"""
        name = run_script("photoName", self.id)
        return name if name not in [kMissingValue, ""] else ""

    @name.setter
    def name(self, name):
        """set name of photo"""
        name = "" if name is None else name
        return run_script("photoSetName", self.id, name)

    @property
    def title(self):
        """title of photo (alias for name)"""
        return self.name

    @title.setter
    def title(self, title):
        """set title of photo (alias for name)"""
        name = "" if title is None else title
        return run_script("photoSetName", self.id, name)

    @property
    def description(self):
        """description of photo"""
        descr = run_script("photoDescription", self.id)
        return descr if descr != kMissingValue else ""

    @description.setter
    def description(self, descr):
        """set description of photo"""
        descr = "" if descr is None else descr
        return run_script("photoSetDescription", self.id, descr)

    @property
    def keywords(self):
        """list of keywords for photo"""
        keywords = run_script("photoKeywords", self.id)
        if not isinstance(keywords, list):
            keywords = [keywords] if keywords != kMissingValue else []
        return keywords

    @keywords.setter
    def keywords(self, keywords):
        """set keywords to list"""
        keywords = [] if keywords is None else keywords
        return run_script("photoSetKeywords", self.id, keywords)

    @property
    def favorite(self):
        """return favorite status (boolean)"""
        return run_script("photoFavorite", self.id)

    @favorite.setter
    def favorite(self, favorite):
        """set favorite status (boolean)"""
        favorite = bool(favorite)
        return run_script("photoSetFavorite", self.id, favorite)

    @property
    def height(self):
        """height of photo in pixels"""
        return run_script("photoHeight", self.id)

    @property
    def width(self):
        """width of photo in pixels"""
        return run_script("photoWidth", self.id)

    @property
    def altitude(self):
        """GPS altitude of photo in meters"""
        altitude = run_script("photoAltitude", self.id)
        return altitude if altitude != kMissingValue else None

    @property
    def location(self):
        """The GPS latitude and longitude, in a tuple of 2 numbers or None.
        Latitude in range -90.0 to 90.0, longitude in range -180.0 to 180.0.
        """
        location = run_script("photoLocation", self.id)
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

        return run_script("photoSetLocation", self.id, location)

    @property
    def date(self):
        """date of photo as timezone-naive datetime.datetime object"""
        return run_script("photoDate", self.id)

    @date.setter
    def date(self, date):
        """Set date of photo as timezone-naive datetime.datetime object

        Args:
            date: timezone-naive datetime.datetime object
        """
        return run_script("photoSetDate", self.id, date)

    @property
    def filename(self):
        """filename of photo"""
        return run_script("photoFilename", self.id)

    @property
    def albums(self):
        """list of Album objects for albums photo is contained in"""
        albums = run_script("photoAlbums", self.id)
        return [Album(album) for album in albums]

    def export(
        self,
        export_path,
        original=False,
        overwrite=False,
        timeout=120,
        reveal_in_finder=False,
    ):
        """Export photo

        Args:
            photo: Photo object to export
            export_path: path to export to
            original: if True, export original image, otherwise export current image; default = False
            overwrite: if True, export will overwrite a file of same name as photo in export_path; default = False
            timeout: number of seconds to wait for Photos to complete export before timing out; default = 120
            reveal_in_finder: if True, will open Finder with exported items selected when done; default = False

        Returns:
            List of full paths of exported photos.  There may be more than one photo exported due
            to live images and burst images.

        Raises:
            ValueError if export_path is not a valid directory

        Note: Photos always exports as high-quality JPEG unless original=True.
        If original=True, will export all burst images for burst photos and
        live movie for live photos.  If original=False, only the primary image from a
        burst set will be exported for burst photos and the live movie component of a
        live image will not be exported, only the JPEG component.
        """
        return PhotosLibrary()._export_photo(
            self,
            export_path=export_path,
            original=original,
            overwrite=overwrite,
            timeout=timeout,
            reveal_in_finder=reveal_in_finder,
        )

    def duplicate(self):
        """duplicates the photo and returns Photo object for the duplicate"""
        dup_id = run_script("photoDuplicate", self.id)
        return Photo(dup_id)

    def spotlight(self):
        """spotlight the photo in Photos"""
        run_script("photoSpotlight", self.id)
