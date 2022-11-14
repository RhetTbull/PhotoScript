(* AppleScript methods used by PhotoScript (https://github.com/RhetTbull/PhotoScript) *)

-- TODO: Variable names are not very consistent throughout this, some use leading _ some trailing_ 
-- Naming scheme is classNameMethodName

---------- Constants ----------

-- max number of times to retry in case of error
-- some AppleScript calls appear to be flaky and don't always execute
-- so retry those up to MAX_RETRY if not succesful
property MAX_RETRY : 5

-- max time in seconds to wait for Photos to respond
property WAIT_FOR_PHOTOS : 300


---------- PhotoLibrary ----------

on photosLibraryWaitForPhotos(timeoutDurationInSeconds)
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
end photosLibraryWaitForPhotos

on photosLibraryIsRunning()
	(* return true if Photos is running, otherwise false *)
	set theApp to "Photos"
	
	if application theApp is running then
		return true
	else
		return false
	end if
end photosLibraryIsRunning

on photosLibraryHide()
	(* tell Photos to hide if it's running; if not running, do nothing  *)
	set theApp to "Photos"
	try
		tell application "System Events"
			set visible of application process theApp to false
		end tell
	end try
end photosLibraryHide

on photosLibraryIsHidden()
	(* return true if hidden or not running, otherwise false *)
	set theApp to "Photos"
	try
		tell application "System Events"
			return not visible of application process theApp
		end tell
	on error
		return true
	end try
end photosLibraryIsHidden

on photosLibraryActivate()
	(* activate Photos app *)
	tell application "Photos"
		activate
	end tell
end photosLibraryActivate

on photosLibraryQuit()
	(* quit Photos app *)
	tell application "Photos"
		quit
	end tell
end photosLibraryQuit

on photosLibraryName()
	(* name of application *)
	tell application "Photos"
		return name
	end tell
end photosLibraryName

on photosLibraryVersion()
	(* Photos version *)
	tell application "Photos"
		return version
	end tell
end photosLibraryVersion

on photosLibraryIsFrontMost()
	(* returns true if front most app, otherwise false *)
	tell application "Photos"
		return frontmost
	end tell
end photosLibraryIsFrontMost

on photosLibraryGetAllPhotos()
	(* return all photos in the library *)
	tell application "Photos"
		set theIDs to id of media items
	end tell
	return theIDs
end photosLibraryGetAllPhotos

on photosLibraryGetPhotoByNumber(photoNumber)
	(* return photo number num_; uses Photos' internal numbering *)
	tell application "Photos"
		return id of media item photoNumber
	end tell
end photosLibraryGetPhotoByNumber

on photosLibraryGetPhotoByRange(startNumber, stopNumber)
	(* return photos in range (inclusive); uses Photos' internal numbering *)
	tell application "Photos"
		return id of media items startNumber thru stopNumber
	end tell
end photosLibraryGetPhotoByRange


on photosLibrarySearchPhotos(searchString)
	(* search for photos by text string *)
	set theIDs to {}
	tell application "Photos"
		set theItems to search for searchString
		repeat with anItem in theItems
			copy id of anItem to end of theIDs
		end repeat
	end tell
	return theIDs
end photosLibrarySearchPhotos

on photosLibraryCount()
	(* return count of photos in the library *)
	tell application "Photos"
		set mediaItemCount to (count of media items)
		return mediaItemCount
	end tell
end photosLibraryCount

on photosLibraryImport(filenames, skipDuplicateCheck)
	(* 	import files
		Args:
			filenames: list of files in POSIX format to import
			skipDuplicateCheck: boolean, if True, skips checking for duplicates
		Returns:
			list of item IDs for imported items
	*)
	set fileList to {}
	repeat with f in filenames
		set fname to POSIX file f
		copy fname to the end of fileList
	end repeat
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set theItems to import fileList skip check duplicates skipDuplicateCheck
		if theItems = missing value then
			return {}
		end if
		set itemList to {}
		repeat with theItem in theItems
			copy id of theItem to end of itemList
		end repeat
		return itemList
	end tell
end photosLibraryImport

on photosLibraryImportToAlbum(filenames, albumID, skipDuplicateCheck)
	(* import files into album 
	   Args:
	       filenames: list of files in POSIX format to import
	       albumID: ID of album to import to
		skipDuplicateCheck: boolean, if True, skips checking for duplicates
	  Returns:
	  	list of item IDs for imported items
	*)
	set fileList to {}
	repeat with f in filenames
		set fname to POSIX file f
		copy fname to the end of fileList
	end repeat
	tell application "Photos"
		set theItems to import fileList into album id (albumID) skip check duplicates skipDuplicateCheck
		if theItems = missing value then
			return {}
		end if
		set itemList to {}
		repeat with theItem in theItems
			copy id of theItem to end of itemList
		end repeat
		return itemList
	end tell
end photosLibraryImportToAlbum

on photosLibraryAlbumNames(topLevel)
	(* return list of album names found in Photos *)
	set albums_folders to photosLibraryGetAlbumFolderNames(topLevel)
	return album_names of albums_folders
end photosLibraryAlbumNames

on photosLibraryFolderNames(topLevel)
	(* return list of folder names found in Photos *)
	set albums_folders to photosLibraryGetAlbumFolderNames(topLevel)
	return folder_names of albums_folders
end photosLibraryFolderNames

on photosLibraryGetAlbumsFolders()
	(* return record containing album names and folder names in the library
	
	    Returns: {album_names:list of album names, folder_names:list of folder names}
	*)
	# see https://discussions.apple.com/docs/DOC-250002459
	tell application "Photos"
		set allFolders to {}
		set allAlbums to the albums --  collect all albums
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
					set allAlbums to falbums & allAlbums
				end tell
			end repeat
			set allFolders to currentLevelFolders & allFolders
			
			set level to level + 1
		end repeat
	end tell
	
	set albums_folders to {_albums:allAlbums, _folders:allFolders}
	return albums_folders
end photosLibraryGetAlbumsFolders


on photosLibraryGetTopLevelAlbumsFolders()
	(* return record containing album names and folder names in the library
	
	    Returns: {album_names:list of album names, folder_names:list of folder names}
	*)
	tell application "Photos"
		set allFolders to the folders
		set allAlbums to the albums
		
		-- On Mojave, this returns all albums and folders so filter only those with no parents
		set allFoldersFiltered to {}
		set allAlbumsFiltered to {}
		repeat with folder_ in allFolders
			try
				set parentID to id of parent of folder_
			on error
				-- no parent
				set top_folder_ to folder id (id of folder_)
				copy top_folder_ to end of allFoldersFiltered
			end try
		end repeat
		
		repeat with album_ in allAlbums
			try
				set parentID to id of parent of album_
			on error
				-- no parent
				set topAlbum to album id (id of album_)
				copy topAlbum to end of allAlbumsFiltered
			end try
		end repeat
	end tell
	
	set albums_folders to {_albums:allAlbumsFiltered, _folders:allFoldersFiltered}
	return albums_folders
end photosLibraryGetTopLevelAlbumsFolders

on photosLibraryGetAlbumFolderNames(topLevel)
	(* return names of albums and folders *)
	if topLevel then
		set albums_folders to photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders to photosLibraryGetAlbumsFolders()
	end if
	set allAlbums to _albums of albums_folders
	set allFolders to _folders of albums_folders
	set allAlbumNames to {}
	set allFolderNames to {}
	tell application "Photos"
		
		repeat with _album in allAlbums
			set theName to name of _album
			copy theName to end of allAlbumNames
		end repeat
		repeat with _folder in allFolders
			set theName to name of _folder
			copy theName to end of allFolderNames
		end repeat
	end tell
	set albumfolderNames to {album_names:allAlbumNames, folder_names:allFolderNames}
	return albumfolderNames
end photosLibraryGetAlbumFolderNames

on photosLibraryAlbumIDs(topLevel)
	(* return list of album ids found in Photos 
	  Args:
	      topLevel: boolean; if true returns only top-level albums otherwise all albums
	*)
	if topLevel then
		tell application "Photos"
			return id of every album
		end tell
	else
		set albums_folders to photosLibraryGetAlbumsFolders()
		set _albums to _albums of albums_folders
		set _ids to {}
		repeat with _a in _albums
			copy id of _a to end of _ids
		end repeat
		return _ids
	end if
end photosLibraryAlbumIDs


on photosLibraryFolderIDs(topLevel)
	(* return list of folder ids found in Photos 
	  Args:
	      topLevel: boolean; if true returns only top-level folders otherwise all folders
	*)
	if topLevel then
		set albums_folders to photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders to photosLibraryGetAlbumsFolders()
	end if
	set _folders to _folders of albums_folders
	set _ids to {}
	repeat with _f in _folders
		copy id of _f to end of _ids
	end repeat
	return _ids
end photosLibraryFolderIDs


on photosLibraryFolderIDLists(topLevel)
	(* return list of folder ids found in Photos as list of ids
	  Args:
	      topLevel: boolean; if true returns only top-level folders otherwise all folders
	*)
	if topLevel then
		set albums_folders to photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders to photosLibraryGetAlbumsFolders()
	end if
	set _folders to _folders of albums_folders
	set _id_list to {}
	repeat with _f in _folders
		set folder_ids_ to {id of _f}
		try
			repeat
				set parentID to id of parent of _f
				copy parentID to end of folder_ids_
				set _f to parent of _f
			end repeat
		on error
			copy folder_ids_ to end of _id_list
		end try
	end repeat
	return _id_list
end photosLibraryFolderIDLists


on photosLibraryCreateAlbum(albumName)
	(*  creates album named albumName
	     does not check for duplicate album
           Returns:
		    UUID of newly created album or 0 if error
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set count_ to 0
		repeat while count_ < MAX_RETRY
			try
				set theAlbum to make new album named albumName
				set theID to ((id of theAlbum) as text)
				return theID
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return 0
	end tell
end photosLibraryCreateAlbum

on photosLibraryCreateAlbumAtFolder(albumName, folder_id_)
	(*  creates album named albumName inside folder folder_id_
	     does not check for duplicate album
           Returns:
		    UUID of newly created album or 0 if error
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set folder_ to folderGetFolderForID(folder_id_)
	tell application "Photos"
		set count_ to 0
		repeat while count_ < MAX_RETRY
			try
				set theAlbum to make new album named albumName at folder_
				set theID to ((id of theAlbum) as text)
				return theID
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return 0
	end tell
end photosLibraryCreateAlbumAtFolder

on photosLibraryGetSelection()
	(* return ids of selected items *)
	set theItemids_ to {}
	tell application "Photos"
		set theItems to selection
		repeat with theItem in theItems
			copy id of theItem to end of theItemids_
		end repeat
	end tell
	return theItemids_
end photosLibraryGetSelection

on photosLibraryFavorites()
	(* return favorites album *)
	tell application "Photos"
		return id of favorites album
	end tell
end photosLibraryFavorites

on photosLibraryRecentlyDeleted()
	(* return recently deleted album *)
	tell application "Photos"
		return id of recently deleted album
	end tell
end photosLibraryRecentlyDeleted

on photosLibraryDeleteAlbum(id_)
	(* delete album with id_ *)
	tell application "Photos"
		set album_ to album id (id_)
		delete album_
	end tell
end photosLibraryDeleteAlbum

on photosLibraryCreateFolder(folderName)
	(*  creates folder named folderName
	     does not check for duplicate folder
           Returns:
		    UUID of newly created folder or 0 if error
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set count_ to 0
		repeat while count_ < MAX_RETRY
			try
				set theFolder to make new folder named folderName
				set theID to ((id of theFolder) as text)
				return theID
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return 0
	end tell
end photosLibraryCreateFolder

on photosLibraryCreateFolderAtFolder(folderName, folder_id_)
	(*  creates folder named folderName inside folder folder_id_
	     does not check for duplicate folder
           Returns:
		    UUID of newly created folder 
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set folder_ to folderGetFolderForID(folder_id_)
	tell application "Photos"
		set count_ to 0
		repeat while count_ < MAX_RETRY
			try
				set theFolder to make new folder named folderName at folder_
				set theID to ((id of theFolder) as text)
				return theID
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return 0
	end tell
end photosLibraryCreateFolderAtFolder

on photosLibraryDeleteFolder(id_)
	(* delete folder with id_ *)
	set folder_ to folderGetFolderForID(id_)
	tell application "Photos"
		delete folder_
	end tell
end photosLibraryDeleteFolder

(*
on photosLibraryDeleteFolder(_id)
	--TODO: doesn't currently work 
	photosLibraryWaitForPhotos(300)
	set _folder_ids to photosLibraryInternalPathIDsToAlbumFolder(folderGetFolderForID(_id))
	tell application "Photos"
		set folder_ to folder id (item 1 of _folder_ids)
		set _folder_ids to rest of _folder_ids
		repeat with _folder_id in _folder_ids
			set folder_ to folderGetFolderForID(_folder_id)
		end repeat
		say (name of folder_ as text)
		delete (folder_)
		
	end tell
end photosLibraryDeleteFolder
*)

on photosLibraryInternalPathToAlbumFolder(targetObject, pathItemDelimiter)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
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
		set pathToObject to targetObjectName
	end tell
	repeat
		try
			set folderName to name of parent of targetObject
			set parentID to id of parent of targetObject
			set pathToObject to folderName & pathItemDelimiter & pathToObject
			set targetObject to folderGetFolderForID(parentID)
		on error
			return pathToObject
		end try
		
	end repeat
end photosLibraryInternalPathToAlbumFolder


on photosLibraryInternalPathIDsToAlbumFolder(targetObject)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
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
		set pathToObject to {}
	end tell
	repeat
		try
			set folderID to id of parent of targetObject
			set parentID to id of parent of targetObject
			copy folderID to beginning of pathToObject
			set targetObject to folderGetFolderForID(parentID)
		on error
			return pathToObject
		end try
		
	end repeat
end photosLibraryInternalPathIDsToAlbumFolder

---------- Album ----------

on albumName(_id)
	(* return name of album with id _id *)
	tell application "Photos"
		return name of album id (_id)
	end tell
end albumName

on albumByName(name_, topLevel)
	(* return album id of album named name_ or 0 if no album found with name_
	    if more than one album named name_, returns the first one found 
	  if topLevel = true, returns only top level albums
	*)
	if topLevel then
		set albums_folders_ to photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders_ to photosLibraryGetAlbumsFolders()
	end if
	set _albums to _albums of albums_folders_
	repeat with _a in _albums
		if name of _a = name_ then
			return id of _a
		end if
	end repeat
	return 0
end albumByName

on albumExists(_id)
	(* return true if album with _id exists otherwise false *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		try
			set _exist to album id (_id)
		on error
			return false
		end try
		
		return true
	end tell
end albumExists

on albumParent(_id)
	(* returns parent folder id of album or 0 if no parent *)
	try
		tell application "Photos"
			return id of parent of album id (_id)
		end tell
	on error
		return 0
	end try
end albumParent

on albumPhotes(id_)
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
end albumPhotes

on albumCount(id_)
	(* return count of items in albums *)
	tell application "Photos"
		return count of media items in album id (id_)
	end tell
end albumCount

on albumAdd(id_, theItems)
	(* add media items to album
	    Args:
		id_: id of album
	       theItems: list of media item ids
		   
	   Returns:
	      list of media item ids added
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		if theItems = {} then
			return {}
		end if
		
		set media_list_ to {}
		repeat with theItem in theItems
			copy media item id (theItem) to end of media_list_
		end repeat
		
		set media_id_list_ to {}
		repeat with theItem in media_list_
			copy id of theItem to end of media_id_list_
		end repeat
		
		set album_ to album id (id_)
		set count_ to 0
		repeat while count_ < MAX_RETRY
			-- add is flaky and sometimes doesn't actually add the photos
			add media_list_ to album_
			
			set added_all_ to true
			set album_photo_ids_ to (id of media items of album_)
			repeat with media_id_ in media_id_list_
				if album_photo_ids_ does not contain media_id_ then
					set added_all_ to false
				end if
			end repeat
			if added_all_ then
				set count_ to MAX_RETRY
			else
				set count_ to count_ + 1
			end if
		end repeat
		
		return media_id_list_
	end tell
end albumAdd

on albumSetName(_id, _title)
	(* set name or title of album *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set name of album id (_id) to _title
			if name of album id (_id) = _title then
				return _title
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end albumSetName

on albumGetPath(id_, path_delimiter_)
	(* return path to album as a string *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set album_ to album id (id_)
	end tell
	try
		set path_ to photosLibraryInternalPathToAlbumFolder(album_, path_delimiter_)
	on error
		set path_ to ""
	end try
	return path_
end albumGetPath

on albumSpotlight(id_)
	(* spotlight album *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		activate
		spotlight album id (id_)
	end tell
end albumSpotlight


---------- Folder ----------

on folderGetFolderForID(_id)
	(* return folder for _id *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set albums_folders to photosLibraryGetAlbumsFolders()
	set _folders to _folders of albums_folders
	tell application "Photos"
		repeat with _folder in _folders
			set _folder_id to id of _folder
			if _folder_id = _id then
				return _folder
			end if
		end repeat
		return missing value
	end tell
end folderGetFolderForID

on folderExists(_id)
	(* return true if folder with _id exists otherwise false *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set versionString to photosLibraryVersion()
	set version_ to stringToNumber(versionString)
	if version_ < 5 then
		tell application "Photos"
			try
				set _exist to folder id (_id)
			on error
				return false
			end try
			
			return true
		end tell
	else
		set _exist to folderGetFolderForID(_id)
		if _exist is not missing value then
			return true
		else
			return false
		end if
	end if
end folderExists

on folderName(_id)
	(* return name of folder with id _id *)
	set folder_ to folderGetFolderForID(_id)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return name of folder_
	end tell
end folderName

on folderSetName(_id, _title)
	(* set name or title of folder *)
	set folder_ to folderGetFolderForID(_id)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set name of folder_ to _title
			if name of folder_ = _title then
				return _title
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end folderSetName

on folderParent(_id)
	(* returns parent folder id of folder or 0 if no parent *)
	try
		set folder_ to folderGetFolderForID(_id)
		photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
		tell application "Photos"
			return id of parent of folder_
		end tell
	on error
		return 0
	end try
end folderParent

on folderAlbums(id_)
	(* return list of ids for albums in folder id_ *)
	set ids to {}
	set _folder to folderGetFolderForID(id_)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set _albums to albums of _folder
		repeat with _album in _albums
			copy id of _album to end of ids
		end repeat
	end tell
	return ids
end folderAlbums

on folderFolders(id_)
	(* return list of ids for folders in folder id_ *)
	set ids to {}
	set _folder to folderGetFolderForID(id_)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set _folders to folders of _folder
		repeat with _f in _folders
			copy id of _f to end of ids
		end repeat
	end tell
	return ids
end folderFolders

on folderCount(id_)
	(* return count of items (albums and folders) in folder id_*)
	set folder_ to folderGetFolderForID(id_)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set _albums_count to (count of albums in folder_)
		set _folders_count to (count of folders in folder_)
		set _len to _albums_count + _folders_count
		return _len
	end tell
end folderCount

on folderByName(name_, topLevel)
	(* return folder id of folder named name_ or 0 if no folder found with name_
	    if more than one folder named name_, returns the first one found 
	  if topLevel = true, returns only top level folder
	*)
	if topLevel then
		set albums_folders_ to the photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders_ to photosLibraryGetAlbumsFolders()
	end if
	set _folders to _folders of albums_folders_
	repeat with _f in _folders
		if name of _f = name_ then
			return id of _f
		end if
	end repeat
	return 0
end folderByName

on folderByPath(folder_path_)
	(* return folder id for folder by path
	Args:
		folder_path_: list of folder names, e.g. {"Folder","SubFolder", "SubSubFolder"}
		
	Returns: 
		folder id or 0 if not found
	*)
	set topLevelfolders to _folders of photosLibraryGetTopLevelAlbumsFolders()
	set folder_ to missing value
	repeat with f_ in topLevelfolders
		if name of f_ = item 1 of folder_path_ then
			set folder_ to f_
		end if
	end repeat
	if folder_ = missing value then
		return 0
	end if
	set folder_path_ to rest of folder_path_
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		try
			repeat with folder_name_ in folder_path_
				set subfolder_ to get folder folder_name_ of folder_
				set subfolder_id_ to id of subfolder_
				set folder_ to folder id (subfolder_id_) of folder_
			end repeat
		on error
			return 0
		end try
	end tell
	return id of folder_
end folderByPath

on folderGetPath(id_, path_delimiter_)
	(* return path to folder as a string *)
	set folder_ to folderGetFolderForID(id_)
	try
		set path_ to photosLibraryInternalPathToAlbumFolder(folder_, path_delimiter_)
	on error
		set path_ to ""
	end try
	return path_
end folderGetPath

on folderPathIDs(id_)
	(* return path to folder as a string *)
	set folder_ to folderGetFolderForID(id_)
	try
		set path_ids_ to photosLibraryInternalPathIDsToAlbumFolder(folder_)
	on error
		set path_ids_ to {}
	end try
	return path_ids_
end folderPathIDs


on folderSpotlight(id_)
	(* spotlight folder *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		activate
		spotlight folder id (id_)
	end tell
end folderSpotlight

---------- Photo ----------
on photoExists(_id)
	(* return true if media item with _id exists otherwise false *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		try
			set _exist to media item id (_id)
		on error
			return false
		end try
		
		return true
	end tell
end photoExists

on photoName(_id)
	(* name or title of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return name of media item id (_id)
	end tell
end photoName

on photoSetName(_id, _title)
	(* set name or title of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set name of media item id (_id) to _title
			if name of media item id (_id) = _title then
				return _title
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end photoSetName

on photoDescription(_id)
	(* description of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return description of media item id (_id)
	end tell
end photoDescription

on photoSetDescription(_id, _descr)
	(* set description of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set description of media item id (_id) to _descr
			if description of media item id (_id) = _descr then
				return _descr
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end photoSetDescription

on photoKeywords(_id)
	(* keywords of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return keywords of media item id (_id)
	end tell
end photoKeywords

on photoSetKeywords(id_, keyword_list)
	(* set keywords of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set keywords of media item id (id_) to keyword_list
			if keywords of media item id (id_) = keyword_list then
				return keyword_list
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end photoSetKeywords

on photoFavorite(id_)
	(* return favorite status of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return favorite of media item id (id_)
	end tell
end photoFavorite

on photoSetFavorite(id_, favorite_)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set favorite of media item id (id_) to favorite_
			if favorite of media item id (id_) = favorite_ then
				return favorite_
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end photoSetFavorite

on photoDate(_id)
	(* date of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return date of media item id (_id)
	end tell
end photoDate

on photoSetDate(id_, date_)
	(* set date of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set date of media item id (id_) to date_
			if date of media item id (id_) = date_ then
				return date_
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end photoSetDate

on photoHeight(id_)
	(* height of photo in pixels *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return height of media item id (id_)
	end tell
end photoHeight

on photoWidth(id_)
	(* width of photo in pixels *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return width of media item id (id_)
	end tell
end photoWidth

on photoAltitude(id_)
	(* GPS altitude of photo in meters *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return altitude of media item id (id_)
	end tell
end photoAltitude

on photoLocation(id_)
	(* GPS location of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return location of media item id (id_)
	end tell
end photoLocation

on photoSetLocation(id_, location_)
	(* set GPS location of photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set count_ to 0
	repeat while count_ < MAX_RETRY
		tell application "Photos"
			set location of media item id (id_) to location_
			if location of media item id (id_) = location_ then
				return location_
			end if
		end tell
		set count_ to count_ + 1
	end repeat
end photoSetLocation

on photoAlbums(id_)
	(* album ids for albums photo id_ is contained in
	    Args:
	   	id_: id of the photo
		
	    Returns: list of album ids containing photo id_
	  *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set _albums_folders to photosLibraryGetAlbumsFolders()
	set _album_ids to {}
	tell application "Photos"
		repeat with _album in _albums of _albums_folders
			if (id of media items of _album) contains id_ then
				copy id of _album to end of _album_ids
			end if
		end repeat
	end tell
	return _album_ids
end photoAlbums

on photoExport(theUUID, thePath, original, edited, theTimeOut)
	(* export photo
	   Args:
	      theUUID: id of the photo to export
		  thePath: path to export to as POSIX path string
		  original: boolean, if true, exports original photo
		  edited: boolean, if true, exports edited photo
		  theTimeOut: how long to wait in case Photos timesout
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
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
	
end photoExport

on photoFilename(id_)
	(* original filename of the photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		return filename of media item id (id_)
	end tell
end photoFilename

on photoDuplicate(id_)
	(* duplicate photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set _new_photo to duplicate media item id (id_)
		return id of _new_photo
	end tell
end photoDuplicate

on photoSpotlight(id_)
	(* spotlight photo *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		activate
		spotlight media item id (id_)
	end tell
end photoSpotlight

---------- Utilities ----------

use framework "Foundation"

on revealInFinder(itemList)
	(* reveal list of POSIX paths in itemList in Finder *)
	if the class of itemList is not list then set itemList to theItemlist as list
	-- reveal items in file viewer
	tell current application's NSWorkspace to set theWorkspace to sharedWorkspace()
	tell theWorkspace to activateFileViewerSelectingURLs:itemList
end revealInFinder

on replaceChars(stringValue, findChars, replaceChars)
	(* replace findChars in stringValue with replaceChars
	
		Args:
			stringValue: a string to search
			findChars: string of one or more characters to find in stringValue
			replaceChars: string of one of more characters to use as replacement for findChars
		
		Returns:
			string with replacements made
		*)
	set oldDelimiters to AppleScript's text item delimiters
	set AppleScript's text item delimiters to the findChars
	set the itemList to every text item of stringValue
	set AppleScript's text item delimiters to the replaceChars
	set newString to the itemList as string
	set AppleScript's text item delimiters to oldDelimiters
	return newString
end replaceChars

on stringToNumber(strValue)
	(* Converts a string representation of real number in form x.y or x,y into a number 
	
	This is required because AppleScript throws in error with " "7.0" as number " 
	in locales that use "," as the decimal separator, expecting "7,0"

	Args:
		strValue: string value to return
	
	Returns:
		number

	*)
	
	try
		return strValue as number
	on error
		-- assume we're in a locale that uses , as decimal separator and try again
		return replaceChars(strValue, ".", ",") as number
	end try
end stringToNumber

--------- Test ----------
(* tell application "Photos"
	set folder_ to folder id ("65E8932D-5746-465A-8B64-EE1FA2EB0B4A/L0/020") of folder id ("216F08FA-5F50-4944-99DA-042C1AEDFAEC/L0/020")
	--set folder_ to folder id ("216F08FA-5F50-4944-99DA-042C1AEDFAEC/L0/020")
end tell *)
--photosLibraryGetAlbumsFolders()
--folderGetFolderForID("211E9B61-1D23-4E75-8CA2-62146A0391E1/L0/020")
--folderExists("211E9B61-1D23-4E75-8CA2-62146A0391E1/L0/020")
