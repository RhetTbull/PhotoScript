""" Photos class """

from .script_loader import run_script

class Photos:
    def __init__(self):
        pass

    def activate(self):
        """ activate Photos.app """
        run_script("activate")

    def import_photos(self, photos, album=None, skip_duplicate_check=False):
        """ import photos

            Args:
                photos: list of file paths to import
                album: optional, name of album to import into (album must exist in Photos)
                skip_duplicate_check: if True, Photos will not check for duplicates on import, default is False
        """
        if album is not None:
            run_script("import_to_album", photos, album, skip_duplicate_check)
        else:
            run_script("import", photos, skip_duplicate_check)

    def album_names(self, top_level = False):
        """ Return list of album names in the Photos library 
            Args:
                top_level: if True, returns only top-level albums otherwise also returns albums in sub-folders; default is False
        """
        return run_script("album_names", top_level)

    def folder_names(self, top_level = False):
        """ Return list of folder names in the Photos library
        
            Args:
                top_level: if True, returns only top-level folders otherwise also returns sub-folders; default is False
        """
        return run_script("folder_names", top_level)

    def album(self, *name, id_=None):
        """ Return Album instance by name or id

            Args:
                name: name of album
                id_: id of album
                Must pass only name or id but not both
            
            Returns:
                Album object or None if album could not be found

            Raises: ValueError if both name and id passed
        """
        if (not name and id_ is None) or (name and id_ is not None):
            raise ValueError("Must pass only name or id but not both")

        if name:
            id_ = run_script("album_by_name",name)
            if id_ != 0:
                return Album(id_)
            else:
                return None
        elif id_:
            return Album(id_)
        else:
            raise ValueError("Invalid name or id_")


class Album:
    def __init__(self, id_):
        self.id = id_

    def name(self):
        run_script("album_name",self.id)
