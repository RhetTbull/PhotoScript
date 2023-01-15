(* AppleScript methods used by PhotoScript (https://github.com/RhetTbull/PhotoScript) *)

-- Naming scheme is classNameMethodName

---------- Imports ----------

use scripting additions
use framework "Foundation"

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
	set albums_folders to _photosLibraryGetAlbumFolderNames(topLevel)
	return album_names of albums_folders
end photosLibraryAlbumNames

on photosLibraryFolderNames(topLevel)
	(* return list of folder names found in Photos *)
	set albums_folders to _photosLibraryGetAlbumFolderNames(topLevel)
	return folder_names of albums_folders
end photosLibraryFolderNames

on _photosLibraryGetAlbumsFolders()
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
end _photosLibraryGetAlbumsFolders

on _walkFoldersLookingForID(theFolderID, theFolder, folderString)
	(* Recursively walk through folders finding the folder that matched folderID 
	
	Args:
		folderID: the folder ID to look for
		theFolder: a Photos folder object representing the current folder
		folderString: the script snippet for the folder
		
	Returns:
		record of {folderString: string, foundID: bool}
		folderString: the matching script snippet
		foundID: true if matching folder found, othwerwise false

	Note:
		This is intended to be called only from photosLibraryGetFolderIDScriptForID
		The initial folderString should be set to ""
	*)
	set originalFolderString to folderString
	tell application "Photos"
		set subFolders to theFolder's folders
		repeat with aFolder in subFolders
			set folderString to "folder id(\"" & (id of aFolder as text) & "\") of " & folderString
			if id of aFolder is equal to theFolderID then
				return {folderString:folderString, foundID:true}
			end if
			return my _walkFoldersLookingForID(theFolderID, aFolder, folderString)
		end repeat
	end tell
	return {folderString:originalFolderString, foundID:false}
end _walkFoldersLookingForID

on photosLibraryGetFolderIDStringForID(theFolderID, topLevel)
	(*	Return AppleScript snippet for folder with ID folderID 
	
		Args:
			folderID: the folder ID to look for
			topLevel: boolean, if True, only search top level folders

		Returns:
			string containing AppleScript snippet for folder with ID folderID
			missing value if not found
	*)
	tell application "Photos"
		set theFolders to folders
		repeat with aFolder in theFolders
			-- on Catalina+ only top-level folders are returned by Photos
			set folderString to "folder id(\"" & (id of aFolder as text) & "\")"
			if id of aFolder is equal to theFolderID then
				return folderString
			end if
			
			if topLevel is false then
				-- my is required due to scope as this is inside a tell block
				-- if my is not used, Photos will look for the function _walkFolders which does not exist in its namespace
				set returnValue to my _walkFoldersLookingForID(theFolderID, aFolder, folderString)
				if foundID of returnValue is true then
					return folderString of returnValue
				end if
			end if
		end repeat
		-- went through all folders with no match
		return missing value
	end tell
	
end photosLibraryGetFolderIDStringForID

on _walkFoldersLookingForName(theFolderName, theFolder, folderString)
	(* Recursively walk through folders finding the folder that matched folderName; returns the first matching folder
	
	Args:
		folderName: the folder name to look for
		theFolder: a Photos folder object representing the current folder
		folderString: the script snippet for the folder
		
	Returns:
		record of {folderString: string, foundID: bool}
		folderString: the matching script snippet
		foundID: true if matching folder found, othwerwise false
		
	Note:
		This is intended to be called only from photosLibraryGetFolderIDStringForName
		The initial folderString should be set to ""
		There may be more than one folder with the same name; this will return the first folder found with a matching name
	*)
	set originalFolderScript to folderString
	tell application "Photos"
		set subFolders to theFolder's folders
		repeat with aFolder in subFolders
			set folderString to "folder id(\"" & (id of aFolder as text) & "\") of " & folderString
			if aFolder's name is equal to theFolderName then
				return {folderString:folderString, foundID:true}
			end if
			return my _walkFoldersLookingForName(theFolderName, aFolder, folderString)
		end repeat
	end tell
	return {folderString:originalFolderScript, foundID:false}
end _walkFoldersLookingForName

on photosLibraryGetFolderIDStringForName(theFolderName, topLevel)
	(* 	Return AppleScript snippet for folder with name folderName 

		Args:
			folderName: the folder name to look for
			topLevel: true if only top level folders should be searched, otherwise false

		Returns:
			string: the AppleScript snippet for the folder
			missing value: if no folder with the given name is found
	*)
	-- TODO: topLevel logic isn't correct for Mojave which will return *all* folders
	-- on Catalina+, only top level folders are returned by Photos
	tell application "Photos"
		set theFolders to folders
		repeat with aFolder in theFolders
			set folderString to "folder id(\"" & (id of aFolder as text) & "\")"
			if aFolder's name is equal to theFolderName then
				return folderString
			end if
			-- my is required due to scope as this is inside a tell block
			-- if my is not used, Photos will look for the function _walkFolders which does not exist in its namespace
			if topLevel is false then
				--recursively walk the folder tree
				set returnValue to my _walkFoldersLookingForName(theFolderName, aFolder, folderString)
				if foundID of returnValue is true then
					return folderString of returnValue
				end if
			end if
		end repeat
		-- went through all folders with no match
		return missing value
	end tell
	
end photosLibraryGetFolderIDStringForName

on _photosLibraryGetTopLevelAlbumsFolders()
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
end _photosLibraryGetTopLevelAlbumsFolders

on _photosLibraryGetAlbumFolderNames(topLevel)
	(* return names of albums and folders *)
	if topLevel then
		set albums_folders to _photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders to _photosLibraryGetAlbumsFolders()
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
end _photosLibraryGetAlbumFolderNames

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
		set albums_folders to _photosLibraryGetAlbumsFolders()
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
		set albums_folders to _photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders to _photosLibraryGetAlbumsFolders()
	end if
	set _folders to _folders of albums_folders
	set _ids to {}
	repeat with _f in _folders
		copy id of _f to end of _ids
	end repeat
	return _ids
end photosLibraryFolderIDs


on _photosLibraryGetTopLevelFolderID(folderName)
	(*	Returns the ID for a top level folder in Photos or missing value if not found 
	
		Args:
			folderName: string of top level folder name to find
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		repeat with theFolder in folders
			if name of theFolder = folderName then
				return id of theFolder
			end if
		end repeat
	end tell
	return missing value
end _photosLibraryGetTopLevelFolderID

on photosLibraryCreateAlbum(albumName)
	(*  creates album named albumName
	     does not check for duplicate album
           Returns:
		    UUID of newly created album or missing value if error
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
		return missing value
	end tell
end photosLibraryCreateAlbum

on photosLibraryCreateAlbumAtFolder(albumName, folderIDString)
	(*  creates album named albumName inside folder folderIDString
		does not check for duplicate album

		Args:
			albumName: string; name of album to create
			folderIDString: string; id of folder to create album in

		Returns:
		    UUID of newly created album or missing value if error
	*)
	set theScript to "
		set count_ to 0
		repeat while count_ < " & MAX_RETRY & "
			try
				set theAlbum to make new album named \"" & albumName & "\" at theFolder
				set theID to ((id of theAlbum) as text)
				return theID
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return missing value
	"
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return _folderRunScript(folderIDString, theScript)
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
	(*  Creates top-level folder named folderName; does not check for duplicate folder

		Args:
			folderName: string; name of folder to create

		Returns:
			folder id string for new folder or missing value if error

	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	tell application "Photos"
		set count_ to 0
		repeat while count_ < MAX_RETRY
			try
				set theFolder to make new folder named folderName
				set theID to (id of theFolder) as text
				return "folder id(\"" & theID & "\")"
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return missing value
	end tell
end photosLibraryCreateFolder

on photosLibraryCreateFolderAtFolder(folderName, folderIDString)
	(*  Creates folder named folderName inside folder folderIDString
		does not check for duplicate folder

		Args:
			folderName: string; name of folder to create
			folderIDString: string; id of folder to create folder in

		Returns:
			folder id string of newly created folder or missing value if error
	*)
	set theScript to "
		set count_ to 0
		repeat while count_ < " & MAX_RETRY & "
			try
				tell theFolder
					set newFolder to make new folder named \"" & folderName & "\" at theFolder
					set theID to (id of newFolder) as text
					return \"folder id(\\\"\" & theID & \"\\\")\"
				end tell
			on error
				set count_ to count_ + 1
			end try
		end repeat
		return missing value
	"
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set newFolderID to _folderRunScript(folderIDString, theScript)
	if newFolderID is equal to missing value then
		return missing value
	end if
	return newFolderID & " of " & folderIDString
end photosLibraryCreateFolderAtFolder

on photosLibraryDeleteFolder(folderIDString)
	(*  Delete folder with id string folderIDString
	
		NOTE: Since Catalina/10.15, does not work for sub folders
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return _folderRunScript(folderIDString, "delete theFolder")
end photosLibraryDeleteFolder

(*
on photosLibraryDeleteFolder(_id)
	--TODO: doesn't currently work 
	set _folder_ids to photosLibraryInternalPathIDsToAlbumFolder(_folderGetFolderForID(_id))
	tell application "Photos"
		set folder_ to folder id (item 1 of _folder_ids)
		set _folder_ids to rest of _folder_ids
		repeat with _folder_id in _folder_ids
			set folder_ to _folderGetFolderForID(_folder_id)
		end repeat
		say (name of folder_ as text)
		delete (folder_)
		
	end tell
end photosLibraryDeleteFolder
*)

on _photosLibraryInternalPathToAlbumFolder(targetObject, pathItemDelimiter)
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
			set targetObject to _folderGetFolderForID(parentID)
		on error
			return pathToObject
		end try
		
	end repeat
end _photosLibraryInternalPathToAlbumFolder



---------- Album ----------

on albumByPath(albumPath)
	(* Returns id of album described by albumPath
	
	Args:
		albumPath: list of folder paths and album name in form {"Folder1", "SubFolder1", "AlbumName"}; 
			if album is top level album then list should take form {"AlbumName"}
	
	Returns:
		id of album or missing value if not found
	*)
	
	set theLen to length of albumPath
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	if theLen = 1 then
		-- album is top level
		tell application "Photos"
			try
				set theAlbum to item 1 of albumPath
				return id of album theAlbum
			on error
				return missing value
			end try
		end tell
	end if
	
	-- album is in a folder
	set theAlbum to item theLen of albumPath
	set folderPath to items 1 thru (theLen - 1) of albumPath
	set folderIDString to folderGetIDStringFromPath(folderPath)
	return _folderGetAlbumID(folderIDString, theAlbum)
end albumByPath

on albumName(theID)
	(* return name of album with id theID *)
	tell application "Photos"
		return name of album id (theID)
	end tell
end albumName

on albumByName(name_, topLevel)
	(* return album id of album named name_ or 0 if no album found with name_
	    if more than one album named name_, returns the first one found 
	  if topLevel = true, returns only top level albums
	*)
	if topLevel then
		set albums_folders_ to _photosLibraryGetTopLevelAlbumsFolders()
	else
		set albums_folders_ to _photosLibraryGetAlbumsFolders()
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
		set path_ to _photosLibraryInternalPathToAlbumFolder(album_, path_delimiter_)
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

on folderGetIDStringFromPath(folderPath)
	(*	Returns script snippet identifying the folder in Photos or missing value if not found
	
		Args:
			folderPath: list of folder paths in form {"Folder1", "SubFolder1", "SubSubFolder1", ...}
	
		Returns: script snippet in form: 
			"folder id(\"E0CD4B6C-CB43-46A6-B8A3-67D1FB4D0F3D/L0/020\") 
				of folder id(\"CB051A4C-2CB7-4B90-B59B-08CC4D0C2823/L0/020\") 
				of folder id(\"88A5F8B8-5B9A-43C7-BB85-3952B81580EB/L0/020\")"
	*)
	set folderCount to count of folderPath
	if folderCount = 1 then
		set folderID to _photosLibraryGetTopLevelFolderID(item 1 of folderPath)
		if folderID is missing value then
			return missing value
		else
			return "folder id(\"" & folderID & "\")"
		end if
	end if
	
	set preamble to "
	on run(folderName)
		tell application \"Photos\"
			set theFolder to "
	
	set postamble to "
		 	repeat with subFolder in folders of theFolder
		 		if name of subFolder as text is equal to folderName as text then
					return id of subFolder
				end if
			end repeat
		end tell
		return missing value
	end run
"
	set folderID to _photosLibraryGetTopLevelFolderID(item 1 of folderPath)
	
	if folderID is missing value then
		return missing value
	end if
	
	set folderString to ("folder id(\"" & folderID as text) & "\")"
	set folderList to items 2 through folderCount of folderPath
	repeat with folderName in folderList
		set theScript to preamble & folderString & postamble
		set subFolderID to run script theScript with parameters {folderName}
		if subFolderID is missing value then
			return missing value
		end if
		set folderString to ("folder id(\"" & subFolderID as text) & "\") of " & folderString
	end repeat
	return folderString
end folderGetIDStringFromPath

on _folderRunScript(folderIDString, theScript)
	(*	Gets a folder identified by folderIDString then runs theScript on this folder
	
		Args:
			folderIDString: script snippet as returned by folderGetIDStringFromPath
			theScript: script snippet to run; folder will be referenced as "theFolder"
			
		Example:
			To get name of folder: _folderRunScript(folderIDString, "return name of theFolder")
	*)
	set theScript to "
	on run()
		tell application \"Photos\"
			set theFolder to " & folderIDString & " 
			" & theScript & "
		end tell
	end run
	"
	
	--display dialog theScript
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return run script theScript
end _folderRunScript

on _folderSplitFolderPath(folderPath)
	(* split folderPath string into list of folder IDs *)
	set oldDelimiters to AppleScript's text item delimiters
	set AppleScript's text item delimiters to " of "
	set folderPathList to every text item of folderPath
	set AppleScript's text item delimiters to oldDelimiters
	return folderPathList
end _folderSplitFolderPath

on _folderGetAlbumID(folderIDString, albumName)
	(* Returns album ID of folder's album albumName or missing value if not found
	
		Args:
			folderIDString: script snippet as returned by folderGetIDStringFromPath for folder path
	
		Returns: album ID	
	*)
	set theScript to "
	try
		return id of theFolder's album \"" & albumName & "\"" & "
	on error
		return missing value
	end try
	"
	
	set albumID to _folderRunScript(folderIDString, theScript)
	return albumID
end _folderGetAlbumID

on _folderGetFolderForID(_id)
	(* return folder for _id *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set albums_folders to _photosLibraryGetAlbumsFolders()
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
end _folderGetFolderForID

on folderExists(folderIDString)
	(* return true if folder identified by folderIDString exists otherwise false *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	try
		return _folderRunScript(folderIDString, "return true")
	on error
		return false
	end try
end folderExists

on folderUUID(folderIDString)
	(* return UUID of folder *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return _folderRunScript(folderIDString, "return id of theFolder as text")
end folderUUID

on folderName(folderIDString)
	(* return name of folder identified by folderIDString *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return _folderRunScript(folderIDString, "return name of theFolder")
end folderName

on folderSetName(folderIDString, theName)
	(* set name of folder identified by folderIDString to theName
	
	Args:
		folderIDString: script snippet as returned by folderGetIDStringFromPath
		theName: new name for folder	

	Returns: true if successful otherwise false
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set retryCount to 0
	repeat while retryCount < MAX_RETRY
		_folderRunScript(folderIDString, "set name of theFolder to \"" & theName & "\"")
		if folderName(folderIDString) = theName then
			return true
		end if
		set retryCount to retryCount + 1
	end repeat
	return folderName(folderIDString) = theName
end folderSetName

on folderParent(folderIDString)
	(* return folder script for parent path of folder at folderIDString
	
	Args:
		folderIDString: script snippet as returned by folderGetIDStringFromPath
	
	Returns:
		parent folder path of folder at folderPath or missing value if no parent
	*)
	set folderParts to _folderSplitFolderPath(folderIDString)
	if length of folderParts > 2 then
		set folderParentPath to item 2 of folderParts
		repeat with i from 3 to (length of folderParts)
			set folderParentPath to folderParentPath & " of " & {item i of folderParts}
		end repeat
		return folderParentPath
	else if length of folderParts = 2 then
		return item 2 of folderParts
	else
		return missing value
	end if
end folderParent

on folderAlbums(folderIDString)
	(* return list of album IDs in folder *)
	set theScript to "
		set theIDs to {}
		repeat with theAlbum in albums of theFolder
			set end of theIDs to id of theAlbum
		end repeat
		return theIDs
	"
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return _folderRunScript(folderIDString, theScript)
end folderAlbums

on folderFolders(folderIDString)
	(* return list of folder IDs in folder *)
	set theScript to "
		set theIDs to {}
		repeat with aSubFolder in folders of theFolder
			set end of theIDs to id of aSubFolder
		end repeat
		return theIDs
	"
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set subFolderIDs to _folderRunScript(folderIDString, theScript)
	if length of subFolderIDs = 0 then
		return {}
	end if
	
	set subFolders to {}
	repeat with subFolderID in subFolderIDs
		set subFolderIDScript to "folder id(\"" & subFolderID & "\") of " & folderIDString
		set end of subFolders to subFolderIDScript
	end repeat
	return subFolders
end folderFolders

on folderCount(folderIDString)
	(* return count of items (albums and folders) in folder *)
	set theScript to "
		set albumsCount_ to (count of albums in theFolder)
		set foldersCount_ to (count of folders in theFolder)
		set theLength to albumsCount_ + foldersCount_
		return theLength
	"
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	return _folderRunScript(folderIDString, theScript)
end folderCount

on folderIDByPath(folderPath)
	(* return folder id for folder by path
	Args:
		folderPath: list of folder names, e.g. {"Folder","SubFolder", "SubSubFolder"}
		
	Returns: 
		folder id or missing value if not found
	*)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set folderString to folderGetIDStringFromPath(folderPath)
	if folderString is not missing value then
		return _folderRunScript(folderString, "return id of theFolder")
	else
		return missing value
	end if
end folderIDByPath

on folderGetPath(folderIDString, pathDelimiter)
	(* Return path to folder as a string, delimited by pathDelimiter *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set thePath to folderName(folderIDString)
	set theParent to folderParent(folderIDString)
	repeat while theParent is not missing value
		set thePath to folderName(theParent) & pathDelimiter & thePath
		set theParent to folderParent(theParent)
	end repeat
	return thePath
end folderGetPath

on folderGetPathFolderIDScript(folderIDString)
	(* Return list of folder ID scripts for the folder and it's parents *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set thePath to {}
	set theParent to folderParent(folderIDString)
	repeat while theParent is not missing value
		set thePath to {theParent} & thePath
		set theParent to folderParent(theParent)
	end repeat
	return thePath
end folderGetPathFolderIDScript

on folderSpotlight(folderIDString)
	(* spotlight folder *)
	photosLibraryWaitForPhotos(WAIT_FOR_PHOTOS)
	set theScript to "
		activate
		spotlight theFolder
	"
	return _folderRunScript(folderIDString, theScript)
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
	set _albums_folders to _photosLibraryGetAlbumsFolders()
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

on revealInFinder(itemList)
	(* reveal list of POSIX paths in itemList in Finder *)
	if the class of itemList is not list then set itemList to theItemlist as list
	-- reveal items in file viewer
	tell current application's NSWorkspace to set theWorkspace to sharedWorkspace()
	tell theWorkspace to activateFileViewerSelectingURLs:itemList
end revealInFinder

--------- Test ----------
