import argparse
import os
import pathlib
import re
import shutil
import sys
from typing import List

"""
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
You can use another script of mine (MediaTest) to ensure that your media library
is organized according to these conventions. MediaTest uses pytest to enforce 
rules such as "all album folders must contain the year in brackets".
"""

parser = argparse.ArgumentParser(
    prog="KaraCopy", description="Copies music and LRC files", epilog=""
)

SOURCE_FOLDER = "D:\\Music"
DEST_FOLDER = "D:\\Playlists\\1980s"

EXTS_MEDIA = ["mp3", "m4a"]
EXTS_ART = ["jpg"]
EXTS_LYRICS = ["lrc"]
ALLOWED_EXTS = EXTS_MEDIA + EXTS_ART + EXTS_LYRICS

MIN_YEAR = '1980'
MAX_YEAR = '1989'


def query_yes_no(question, default="yes") -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def get_path_depth(path: str) -> int:
    return len(path.strip(os.path.sep).split(os.path.sep))


def get_file_ext(path: str) -> str:
    _, ext = os.path.splitext(path)
    return ext.strip(".")


def is_file_type_media(path: str) -> bool:
    ext = get_file_ext(path)
    return ext in EXTS_MEDIA


def sizeof_fmt(num, suffix="B") -> None:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def process_album_dir(album_path: str, min_year: str, max_year: str) -> List[str]:
    """Returns a list of absolute file paths to files which should be copied,
    including .mp3/.m4a, .lrc and .jpg (cover art) files."""
    ret = []
    tokens = album_path.split(os.path.sep)
    album_name = tokens[-1]
    artist_name = tokens[-2]

    album_year = 0
    try:
        album_year = int(re.findall("\[(\d{4})\]", album_name)[-1])
    except Exception as e:
        print("Exception processing album: " + album_name)
        print(e)
        sys.exit(1)

    if (min_year == "any" or album_year >= int(min_year)) and (
        max_year == "any" or album_year <= int(max_year)
    ):
        for root, _, files in os.walk(album_path):
            for f in files:
                ext = get_file_ext(f)
                if ext in EXTS_LYRICS:
                    ret.append(os.path.join(root, f))
                    # Find media file associated with LRC file
                    basename, ext = os.path.splitext(f)
                    for ext in EXTS_MEDIA:
                        mf = os.path.join(root, basename + "." + ext)
                        if os.path.exists(mf):
                            ret.append(mf)
                elif ext in EXTS_ART:
                    ret.append(os.path.join(root, f))
    return ret


def copy_file(source_dir: str, dest_dir: str, source_file_abspath: str) -> None:
    """Copy specified file to destination directory, preserving directory structure
    and creating destination subdirectories as needed.

    E.g. given:
    source_dir="D:\\Music"
    dest_dir="D:\\Playlists\\1990"
    source_file_abspath="D:\\Music\Martha and the Muffins\\Danseparc [1983]\\01 - Obedience.mp3"

    It will create the two destination subdirectories:
    "D:\\Playlists\\1990\\Martha and the Muffins"
    "D:\\Playlists\\1990\\Martha and the Muffins\Danseparc [1983]"

    And copy the file to:
    "D:\\Playlists\\1990\\Martha and the Muffins\\Danseparc [1983]\\01 - Obedience.mp3"

    """
    # First we need to compute the relative path by stripping the source_dir
    if not source_file_abspath.startswith(source_dir):
        raise Exception("Source file path doesn't match source directory")
    rel_file_path = source_file_abspath.strip(source_dir).strip(os.path.sep)
    # rel_path_path is now like "Martha and the Muffins\\Danseparc [1983]\\01 - Obedience.mp3"
    dest_file_abspath = os.path.join(dest_dir, rel_file_path)
    # dest_file_abspath is now like "D:\\Playlists\\1990\\Martha and the Muffins\\Danseparc [1983]\\01 - Obedience.mp3"
    dest_dir_abspath, _ = os.path.split(dest_file_abspath)
    # dest_dir_abspath is now like "D:\\Playlists\\1990\\Martha and the Muffins\\Danseparc [1983]"
    # make necessary subdirectories
    pathlib.Path(dest_dir_abspath).mkdir(parents=True, exist_ok=True)
    # copy file
    shutil.copy(source_file_abspath, dest_file_abspath)


def walk_media_dir(media_path: str, min_year: str, max_year: str) -> List[str]:
    files = []
    base_depth = get_path_depth(media_path)
    for root, dirs, _ in os.walk(media_path, topdown=False):
        for name in dirs:
            fullpath = os.path.join(root, name)
            current_depth = get_path_depth(fullpath)
            # 1 = artist dir
            # 2 = album [year] dir
            if current_depth - base_depth == 2:
                files.extend(process_album_dir(fullpath, min_year, max_year))
    return files


def show_copy_stats(files: List[str]) -> None:
    print("Files to be copied:")
    tot_size_bytes = 0
    media_file_count = 0
    for f in files:
        print(f)
        fstat = os.stat(f)
        tot_size_bytes += fstat.st_size
        if is_file_type_media(f):
            media_file_count += 1
    print(
        f"Total number of files to be copied (including media/lyrics/art): {len(files)}"
    )
    print(f"Total number of media files to be copied: {media_file_count}")
    print(
        f"Total filesize to be copied: {tot_size_bytes} bytes ({sizeof_fmt(tot_size_bytes)})"
    )


def show_copy_proceed_menu(files: List[str], dest_folder: str) -> bool:
    if not query_yes_no("Proceed with copy?"):
        print("Copy aborted")
        return False
    print("Proceeding with copy")
    if os.path.exists(dest_folder):
        if not query_yes_no(
            "Destination folder exists, are you sure you wish to overwrite it (all contents will be lost)?"
        ):
            print("Copy aborted")
            return False
        else:
            shutil.rmtree(dest_folder)
            os.mkdir(dest_folder)
            print("Existing folder deleted successfully. Proceeding with copy")
    return True


def copy_files(files: List[str], source_dir: str, dest_dir: str) -> None:
    for f in files:
        copy_file(source_dir, dest_dir, f)
    print(f"Copied {len(files)} files")


def main():
    files = walk_media_dir(SOURCE_FOLDER, MIN_YEAR, MAX_YEAR)
    show_copy_stats(files)
    if show_copy_proceed_menu(files, DEST_FOLDER):
        copy_files(files, SOURCE_FOLDER, DEST_FOLDER)


if __name__ == "__main__":
    main()
