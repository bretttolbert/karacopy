# karacopy

The purpose of this script is to copy matching files from a source directory
into a destination directory (optionally? preserving folder structure)

Use-case: You want to create a Karaoke party mix for KaraFun player.
Assumning you have a large media library and some of your media files (mp3/m4a) have
associated LRC (synched lyrics) files (same filename but with .lrc file extension)
With this script you can copy a subset of your media (mp3/m4a) files into a folder
(only those having .lrc files), so you can then open that folder in KaraFun Player, 
queue those tracks, shuffle them, and it's karaoke party time.

Players like MusicBee allow you to copy tracks into a folder but it doesn't copy
the .lrc files. This script, on the other hand, copies the .lrc files and
does not copy media if it doesn't find a matching .lrc file.

Additionally you may want to filter based on criteria such as year or genre.
Rather than use ID3 tags, this scripts expects your album folders are labeled
such that the year is in square brackets.
You can use another script of mine (mediatest) to ensure that your media library
is organized according to these conventions. mediatest uses pytest to enforce 
rules such as "all album folders must contain the year in brackets".

## Usage

```bash
python karacopy.py D:\Music\ D:\Playlists\1980s --min-year 1980 --max-year 1989
```
