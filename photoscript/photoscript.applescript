on _activate()
	(* activate Photos app *)
	tell application "Photos"
		activate
	end tell
end _activate

on _import(filenames, skip_duplicate_check)
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
end _import

on _import_to_album(filenames, album_name, skip_duplicate_check)
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
		import file_list into album album_name skip check duplicates skip_duplicate_check
	end tell
end _import_to_album

to _album_names(top_level)
	(* return list of album names found in Photos *)
	if top_level then
		
		tell application "Photos"
			return name of every album
		end tell
	else
		set albums_folders to _get_album_folder_names()
		return album_names of albums_folders
	end if
end _album_names

to _folder_names(top_level)
	(* return list of folder names found in Photos *)
	if top_level then
		tell application "Photos"
			return name of every folder
		end tell
	else
		set albums_folders to _get_album_folder_names()
		return folder_names of albums_folders
	end if
	
end _folder_names

to _get_albums_folders()
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
end _get_albums_folders

on _get_album_folder_names()
	set albums_folders to _get_albums_folders()
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
end _get_album_folder_names

on _album_name(_id)
	(* return name of album with id _id *)
	tell application "Photos"
		return name of album id (_id)
	end tell
end _album_name

on _album_by_name(_name)
	(* return album id of album named _name or 0 if no album found with _name *)
	set albums_folders to _get_albums_folders()
	set _albums to _albums of albums_folders
	repeat with _a in _albums
		if name of _a = _name then
			return id of _a
		end if
	end repeat
	return 0
end _album_by_name

