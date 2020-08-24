-- TODO: Variable names are not very consistent throughout this

-- Naming scheme is _classname_methodname

---------- PhotoLibrary ----------
on _photoslibrary_activate()
	(* activate Photos app *)
	tell application "Photos"
		activate
	end tell
end _photoslibrary_activate

on _photoslibrary_quit()
	(* quit Photos app *)
	tell application "Photos"
		quit
	end tell
end _photoslibrary_quit

on _photoslibrary_name()
	(* name of application *)
	tell application "Photos"
		return name
	end tell
end _photoslibrary_name

on _photoslibrary_version()
	(* Photos version *)
	tell application "Photos"
		return version
	end tell
end _photoslibrary_version

on _photoslibrary_frontmost()
	(* returns true if front most app, otherwise false *)
	tell application "Photos"
		return frontmost
	end tell
end _photoslibrary_frontmost

on _photoslibrary_get_all_photos()
	(* return all photos in the library *)
	set ids to {}
	tell application "Photos"
		repeat with _item in every media item
			copy id of _item to end of ids
		end repeat
	end tell
	return ids
end _photoslibrary_get_all_photos

on _photoslibrary_search_photos(search_str)
	(* search for photos by text string *)
	set ids to {}
	tell application "Photos"
		set _items to search for search_str
		repeat with _item in _items
			copy id of _item to end of ids
		end repeat
	end tell
	return ids
end _photoslibrary_search_photos

on _photoslibrary_import(filenames, skip_duplicate_check)
	(* import files
	   Args:
	       filenames: list of files in POSIX format to import
		skip_duplicate_check: boolean, if True, skips checking for duplicates
	*)
	set file_list to {}
	repeat with f in filenames
		set fname to POSIX file f
		copy fname to the end of file_list
	end repeat
	tell application "Photos"
		import file_list skip check duplicates skip_duplicate_check
	end tell
end _photoslibrary_import

on _photoslibrary_import_to_album(filenames, album_, skip_duplicate_check)
	(* import files into album 
	   Args:
	       filenames: list of files in POSIX format to import
	       album_name: name of album to import to
		skip_duplicate_check: boolean, if True, skips checking for duplicates
	*)
	set file_list to {}
	repeat with f in filenames
		set fname to POSIX file f
		copy fname to the end of file_list
	end repeat
	tell application "Photos"
		import file_list into album id (album_) skip check duplicates skip_duplicate_check
	end tell
end _photoslibrary_import_to_album

on _photoslibrary_album_names(top_level)
	(* return list of album names found in Photos *)
	if top_level then
		
		tell application "Photos"
			return name of every album
		end tell
	else
		set albums_folders to _photoslibrary_get_album_folder_names()
		return album_names of albums_folders
	end if
end _photoslibrary_album_names

on _photoslibrary_folder_names(top_level)
	(* return list of folder names found in Photos *)
	if top_level then
		tell application "Photos"
			return name of every folder
		end tell
	else
		set albums_folders to _photoslibrary_get_album_folder_names()
		return folder_names of albums_folders
	end if
	
end _photoslibrary_folder_names

on _photoslibrary_get_albums_folders()
	(* return record containing album names and folder names in the library
	
	    Returns: {album_names:list of album names, folder_names:list of folder names}
	*)
	# see https://discussions.apple.com/docs/DOC-250002459
	tell application "Photos"
		set allfolders to {}
		set allalbums to the albums --  collect all albums
		set level to 0 -- nesting level of folders
		
		set nextlevelFolders to the folders
		set currentLevelFolders to {}
		
		repeat while (nextlevelFolders is not {})
			set currentLevelFolders to nextlevelFolders
			set nextlevelFolders to {}
			repeat with fi in currentLevelFolders
				tell fi
					set ffolders to its folders
					set falbums to its albums
					set nextlevelFolders to ffolders & nextlevelFolders
					set allalbums to falbums & allalbums
				end tell
			end repeat
			set allfolders to currentLevelFolders & allfolders
			
			set level to level + 1
		end repeat
	end tell
	
	set albums_folders to {_albums:allalbums, _folders:allfolders}
	return albums_folders
end _photoslibrary_get_albums_folders

on _photoslibrary_get_album_folder_names()
	(* return names of albums and folders *)
	set albums_folders to _photoslibrary_get_albums_folders()
	set allalbums to _albums of albums_folders
	set allfolders to _folders of albums_folders
	set allalbumnames to {}
	set allfoldernames to {}
	tell application "Photos"
		
		repeat with _album in allalbums
			set theName to name of _album
			copy theName to end of allalbumnames
		end repeat
		repeat with _folder in allfolders
			set theName to name of _folder
			copy theName to end of allfoldernames
		end repeat
	end tell
	set album_folder_names to {album_names:allalbumnames, folder_names:allfoldernames}
	return album_folder_names
end _photoslibrary_get_album_folder_names

on _photoslibrary_album_ids(top_level)
	(* return list of album ids found in Photos 
	  Args:
	      top_level: boolean; if true returns only top-level albums otherwise all albums
	*)
	if top_level then
		tell application "Photos"
			return id of every album
		end tell
	else
		set albums_folders to _photoslibrary_get_albums_folders()
		set _albums to _albums of albums_folders
		set _ids to {}
		repeat with _a in _albums
			copy id of _a to end of _ids
		end repeat
		return _ids
	end if
end _photoslibrary_album_ids

on _photoslibrary_create_album(albumName)
	(*  creates album named albumName
	     does not check for duplicate album
           Returns:
		    UUID of newly created album 
	*)
	tell application "Photos"
		set theAlbum to make new album named albumName
		set theID to ((id of theAlbum) as text)
		return theID
	end tell
end _photoslibrary_create_album

on _photoslibrary_get_selection()
	(* return ids of selected items *)
	set item_ids_ to {}
	tell application "Photos"
		set items_ to selection
		repeat with item_ in items_
			copy id of item_ to end of item_ids_
		end repeat
	end tell
	return item_ids_
end _photoslibrary_get_selection

on _photoslibrary_favorites()
	(* return favorites album *)
	tell application "Photos"
		return id of favorites album
	end tell
end _photoslibrary_favorites

on _photoslibrary_recently_deleted()
	(* return recently deleted album *)
	tell application "Photos"
		return id of recently deleted album
	end tell
end _photoslibrary_recently_deleted

on _photoslibrary_delete_album(id_)
	(* delete album with id_ *)
	tell application "Photos"
		set album_ to album id (id_)
		delete album_
	end tell
end _photoslibrary_delete_album

---------- Album ----------

on _album_name(_id)
	(* return name of album with id _id *)
	tell application "Photos"
		return name of album id (_id)
	end tell
end _album_name

on _album_by_name(_name)
	(* return album id of album named _name or 0 if no album found with _name
	    if more than one album named _name, returns the first one found 
	*)
	set albums_folders to _photoslibrary_get_albums_folders()
	set _albums to _albums of albums_folders
	repeat with _a in _albums
		if name of _a = _name then
			return id of _a
		end if
	end repeat
	return 0
end _album_by_name

on _album_exists(_id)
	(* return true if album with _id exists otherwise false *)
	tell application "Photos"
		try
			set _exist to album id (_id)
		on error
			return false
		end try
		
		return true
	end tell
end _album_exists

on _album_parent(_id)
	(* returns parent folder id of album or 0 if no parent *)
	try
		tell application "Photos"
			return id of parent of album id (_id)
		end tell
	on error
		return 0
	end try
end _album_parent

on _album_photos(id_)
	(* return list of ids for media items in album _id *)
	set ids to {}
	tell application "Photos"
		set _album to album id (id_)
		set _items to media items of _album
		repeat with _item in _items
			copy id of _item to end of ids
		end repeat
	end tell
	return ids
end _album_photos

on _album_len(id_)
	(* return count of items in albums *)
	tell application "Photos"
		return count of media items in album id (id_)
	end tell
end _album_len

on _album_add(id_, items_)
	(* add media items to album
	    Args:
		id_: id of album
	       items_: list of media item ids
	*)
	tell application "Photos"
		set media_list_ to {}
		repeat with item_ in items_
			copy media item id (item_) to end of media_list_
		end repeat
		set album_ to album id (id_)
		add media_list_ to album_
	end tell
end _album_add

---------- Photo ----------
on _photo_exists(_id)
	(* return true if media item with _id exists otherwise false *)
	tell application "Photos"
		try
			set _exist to media item id (_id)
		on error
			return false
		end try
		
		return true
	end tell
end _photo_exists

on _photo_name(_id)
	(* name or title of photo *)
	tell application "Photos"
		return name of media item id (_id)
	end tell
end _photo_name

on _photo_set_name(_id, _title)
	(* set name or title of photo *)
	tell application "Photos"
		set name of media item id (_id) to _title
	end tell
end _photo_set_name

on _photo_description(_id)
	(* description of photo *)
	tell application "Photos"
		return description of media item id (_id)
	end tell
end _photo_description

on _photo_set_description(_id, _descr)
	(* set description of photo *)
	tell application "Photos"
		set description of media item id (_id) to _descr
	end tell
end _photo_set_description

on _photo_keywords(_id)
	(* keywords of photo *)
	tell application "Photos"
		return keywords of media item id (_id)
	end tell
end _photo_keywords

on _photo_set_keywords(id_, keyword_list)
	(* set keywords of photo *)
	tell application "Photos"
		set keywords of media item id (id_) to keyword_list
	end tell
end _photo_set_keywords

on _photo_favorite(id_)
	(* return favorite status of photo *)
	tell application "Photos"
		return favorite of media item id (id_)
	end tell
end _photo_favorite

on _photo_set_favorite(id_, favorite_)
	tell application "Photos"
		set favorite of media item id (id_) to favorite_
	end tell
end _photo_set_favorite

on _photo_date(_id)
	(* date of photo *)
	tell application "Photos"
		return date of media item id (_id)
	end tell
end _photo_date

on _photo_height(id_)
	(* height of photo in pixels *)
	tell application "Photos"
		return height of media item id (id_)
	end tell
end _photo_height

on _photo_width(id_)
	(* width of photo in pixels *)
	tell application "Photos"
		return width of media item id (id_)
	end tell
end _photo_width

on _photo_altitude(id_)
	(* GPS altitude of photo in meters *)
	tell application "Photos"
		return altitude of media item id (id_)
	end tell
end _photo_altitude

on _photo_location(id_)
	(* GPS location of photo *)
	tell application "Photos"
		return location of media item id (id_)
	end tell
end _photo_location

on _photo_set_location(id_, location_)
	(* set GPS location of photo *)
	tell application "Photos"
		set location of media item id (id_) to location_
	end tell
end _photo_set_location

on _photo_export(theUUID, thePath, original, edited, theTimeOut)
	(* export photo
	   Args:
	      theUUID: id of the photo to export
		  thePath: path to export to as POSIX path string
		  original: boolean, if true, exports original photo
		  edited: boolean, if true, exports edited photo
		  theTimeOut: how long to wait in case Photos timesout
	*)
	tell application "Photos"
		set thePath to thePath
		set theItem to media item id theUUID
		set theFilename to filename of theItem
		set itemList to {theItem}
		
		if original then
			with timeout of theTimeOut seconds
				export itemList to POSIX file thePath with using originals
			end timeout
		end if
		
		if edited then
			with timeout of theTimeOut seconds
				export itemList to POSIX file thePath
			end timeout
		end if
		
		return theFilename
	end tell
	
end _photo_export

on _photo_filename(id_)
	(* original filename of the photo *)
	tell application "Photos"
		return filename of media item id (id_)
	end tell
end _photo_filename

on _photo_duplicate(id_)
	tell application "Photos"
		set _new_photo to duplicate media item id (id_)
		return id of _new_photo
	end tell
end _photo_duplicate

--------- Test ----------


--------- Code from Photos Utilities ---------
-- see: http://photosautomation.com/scripting/script-library.html 
(*
on _get_album_path(id_, path_delimiter_)
	waitForPhotos(300)
	tell application "Photos"
		set album_ to album id (id_)
	end tell
	return deriveInyternalLibraryPathToAlbumOrFolder(album_, false, path_delimiter_)
end _get_album_path

on deriveInyternalLibraryPathToAlbumOrFolder(targetObject, appendItemID, pathItemDelimiter)
	waitForPhotos(300)
	tell application "Photos"
		if not (exists targetObject) then
			error "The indicated item does not exist."
		end if
		if class of targetObject is album then
			set targetObjectName to the name of targetObject
		else if class of targetObject is folder then
			set targetObjectName to the name of targetObject
		else
			error "The indicated item must be a folder or album."
		end if
		if appendItemID is true then
			set targetObjectID to the id of targetObject
			set pathToObject to targetObjectName & space & "(" & targetObjectID & ")"
		else
			set pathToObject to targetObjectName
		end if
		repeat
			try
				if class of parent of targetObject is folder then
					set folderName to the name of parent of targetObject
					set pathToObject to folderName & pathItemDelimiter & pathToObject
					set thisID to id of parent of targetObject
					set targetObject to folder id thisID
				else if class of parent of targetObject is album then
					set albumName to the name of parent of targetObject
					set pathToObject to albumName & pathItemDelimiter & pathToObject
					set thisID to id of parent of targetObject
					set targetObject to album id thisID
				end if
			on error
				return pathToObject
			end try
		end repeat
	end tell
end deriveInyternalLibraryPathToAlbumOrFolder


on waitForPhotos(timeoutDurationInSeconds)
	if running of application "Photos" is false then
		tell application "Photos" to launch
		tell current application
			set currentTimeInSeconds to (time of (current date))
			repeat until (time of (current date)) is greater than (currentTimeInSeconds + timeoutDurationInSeconds)
				try
					tell application "Photos"
						set mediaItemCount to (count of media items)
					end tell
					if mediaItemCount is not 0 then
						return true
					else
						delay 1
					end if
				end try
			end repeat
		end tell
		error number -128
	end if
	return true
end waitForPhotos
*)

