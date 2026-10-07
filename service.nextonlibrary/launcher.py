# -*- coding: utf-8 -*-
import os
import sys
import xml.etree.ElementTree as ET

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

ADDON_ID = "service.nextonlibrary"
ADDON = xbmcaddon.Addon(ADDON_ID)
PLAYLIST_DIRECTORIES = ("special://profile/playlists/video/", "special://profile/playlists/mixed/")
SUPPORTED_PLAYLIST_TYPES = ("tvshows", "episodes")


def log(message, level=xbmc.LOGINFO):
    xbmc.log("[S.I.N.][Launcher] %s" % message, level)


def show_changelog():
    try:
        addon_path = ADDON.getAddonInfo("path")
        changelog_path = os.path.join(addon_path, "changelog.txt")

        if xbmcvfs.exists(changelog_path):
            handle = xbmcvfs.File(changelog_path)
            content = handle.read()
            handle.close()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
        else:
            content = "No changelog available."
            log("Changelog not found at %s" % changelog_path, xbmc.LOGWARNING)

        xbmcgui.Dialog().textviewer(
            "%s - Changelog" % ADDON.getAddonInfo("name"),
            content,
        )
    except Exception as exc:
        log("Failed to open changelog: %s" % exc, xbmc.LOGERROR)
        xbmcgui.Dialog().ok(
            ADDON.getAddonInfo("name"),
            "Error opening changelog:\n%s" % exc,
        )


def close_settings():
    xbmc.executebuiltin("Dialog.Close(addonsettings,true)")
    xbmc.sleep(300)


def edit_show_playlists():
    close_settings()
    xbmc.executebuiltin("ActivateWindow(videos,special://videoplaylists/,return)")


def find_show_playlists():
    playlists = []
    for directory in PLAYLIST_DIRECTORIES:
        try:
            _, files = xbmcvfs.listdir(directory)
        except Exception as exc:
            log("Could not list %s: %s" % (directory, exc), xbmc.LOGWARNING)
            continue
        for filename in files:
            if not filename.lower().endswith(".xsp"):
                continue
            path = directory + filename
            try:
                handle = xbmcvfs.File(path)
                content = handle.read()
                handle.close()
                root = ET.fromstring(content)
            except Exception as exc:
                log("Skipping unreadable playlist %s: %s" % (path, exc), xbmc.LOGWARNING)
                continue
            if root.get("type") not in SUPPORTED_PLAYLIST_TYPES:
                continue
            name = (root.findtext("name") or filename[:-4]).strip()
            playlists.append((name, root.get("type"), path))
    return sorted(playlists, key=lambda entry: entry[0].casefold())


def choose_show_playlist():
    playlists = find_show_playlists()
    close_settings()
    if not playlists:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo("name"), ADDON.getLocalizedString(30078))
        ADDON.openSettings()
        return

    labels = ["%s (%s)" % (name, playlist_type) for name, playlist_type, _ in playlists]
    index = xbmcgui.Dialog().select(ADDON.getLocalizedString(30074).rstrip("."), labels)
    if index >= 0:
        ADDON.setSetting("skip_intro_show_playlist", playlists[index][2])
    ADDON.openSettings()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "edit_show_playlists":
        edit_show_playlists()
    elif len(sys.argv) > 1 and sys.argv[1] == "choose_show_playlist":
        choose_show_playlist()
    elif len(sys.argv) > 1 and sys.argv[1] == "show_changelog":
        show_changelog()
    else:
        ADDON.openSettings()
