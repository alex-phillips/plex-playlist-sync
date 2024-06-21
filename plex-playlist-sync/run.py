import logging
import os
import time

import deezer
import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials

from utils.deezer import deezer_playlist_sync
from utils.spotify import spotify_playlist_sync
import configparser

plex_config = {
    "url": os.getenv("PLEX_URL"),
    "token": os.getenv("PLEX_TOKEN"),
}

app_config = {
    "write_missing_as_csv": os.getenv("WRITE_MISSING_AS_CSV", "0") == "1",
    "append_service_suffix": os.getenv("APPEND_SERVICE_SUFFIX", "1") == "1",
    "add_playlist_poster": os.getenv("ADD_PLAYLIST_POSTER", "1") == "1",
    "add_playlist_description": os.getenv("ADD_PLAYLIST_DESCRIPTION", "1") == "1",
    "append_instead_of_sync": os.getenv("APPEND_INSTEAD_OF_SYNC", False) == "1",
    "wait_seconds": int(os.getenv("SECONDS_TO_WAIT", 86400)),
}

spotify_config = {
    "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
    "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
    "user_id": os.getenv("SPOTIFY_USER_ID"),
}

cfg_file = "./config.ini"
cfg = configparser.ConfigParser()
if not os.path.exists(cfg_file):
    cfg["app"] = {}
    cfg["plex"] = {}
    cfg["spotify"] = {}
    for k, v in plex_config.items():
        if v is None:
            cfg["plex"][k] = input(f"{k}: ")
        else:
            cfg["plex"][k] = v

    for k, v in spotify_config.items():
        if v is None:
            cfg["spotify"][k] = input(f"{k}: ")
        else:
            cfg["spotify"][k] = v

    cfg["app"] = {
        "write_missing_as_csv": os.getenv("WRITE_MISSING_AS_CSV", "0") == "1",
        "append_service_suffix": os.getenv("APPEND_SERVICE_SUFFIX", "1") == "1",
        "add_playlist_poster": os.getenv("ADD_PLAYLIST_POSTER", "1") == "1",
        "add_playlist_description": os.getenv("ADD_PLAYLIST_DESCRIPTION", "1") == "1",
        "append_instead_of_sync": os.getenv("APPEND_INSTEAD_OF_SYNC", False) == "1",
        "wait_seconds": int(os.getenv("SECONDS_TO_WAIT", 86400)),
    }

    with open(cfg_file, 'w') as configfile:
        cfg.write(configfile)

cfg.read(cfg_file)

# Read ENV variables
# userInputs = UserInputs(
#     plex_url=os.getenv("PLEX_URL", "https://plx.w00t.cloud"),
#     plex_token=os.getenv("PLEX_TOKEN", "v4meVwusxBrVj_nwnyxK"),
#     write_missing_as_csv=os.getenv("WRITE_MISSING_AS_CSV", "0") == "1",
#     append_service_suffix=os.getenv("APPEND_SERVICE_SUFFIX", "1") == "1",
#     add_playlist_poster=os.getenv("ADD_PLAYLIST_POSTER", "1") == "1",
#     add_playlist_description=os.getenv("ADD_PLAYLIST_DESCRIPTION", "1") == "1",
#     append_instead_of_sync=os.getenv("APPEND_INSTEAD_OF_SYNC", False) == "1",
#     wait_seconds=int(os.getenv("SECONDS_TO_WAIT", 86400)),

#     deezer_user_id=os.getenv("DEEZER_USER_ID", None),
#     deezer_playlist_ids=os.getenv("DEEZER_PLAYLIST_ID", None),
# )

while True:
    logging.info("Starting playlist sync")

    if cfg["plex"]["url"] and cfg["plex"]["token"]:
        try:
            plex = PlexServer(cfg["plex"]["url"], cfg["plex"]["token"])
        except:
            logging.error("Plex Authorization error")
            break
    else:
        logging.error("Missing Plex Authorization Variables")
        break

    ########## SPOTIFY SYNC ##########

    logging.info("Starting Spotify playlist sync")

    SP_AUTHSUCCESS = False

    if (
        cfg["spotify"]["client_id"]
        and cfg["spotify"]["client_secret"]
        and cfg["spotify"]["user_id"]
    ):
        try:
            sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    cfg["spotify"]["client_id"],
                    cfg["spotify"]["client_secret"],
                )
            )
            SP_AUTHSUCCESS = True
        except:
            logging.info("Spotify Authorization error, skipping spotify sync")

    else:
        logging.info(
            "Missing one or more Spotify Authorization Variables, skipping"
            " spotify sync"
        )

    if SP_AUTHSUCCESS:
        spotify_playlist_sync(sp, plex, cfg)

    logging.info("Spotify playlist sync complete")

    ########## DEEZER SYNC ##########

    # logging.info("Starting Deezer playlist sync")
    # dz = deezer.Client()
    # deezer_playlist_sync(dz, plex, userInputs)
    # logging.info("Deezer playlist sync complete")

    # logging.info("All playlist(s) sync complete")
    # logging.info("sleeping for %s seconds" % userInputs.wait_seconds)

    time.sleep(userInputs.wait_seconds)
