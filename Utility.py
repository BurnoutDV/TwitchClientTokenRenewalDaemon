#!/usr/bin/env python3
# coding: utf-8

# Copyright 2021 by BurnoutDV, <burnoutdv@gmail.com>
#
# This file is part of TwitchClientTokenRenewalDaemon.
#
# TwitchClientTokenRenewalDaemon is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# TwitchClientTokenRenewalDaemon is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0-only <https://www.gnu.org/licenses/gpl-3.0.en.html>

# ! copied from https://github.com/BurnoutDV/YtPlaylistUpload/LocalUtility.py

import errno
import requests
import logging
import json
from json.decoder import JSONDecodeError

logger = logging.getLogger(__name__)

VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"
REFRESH_URL = "https://id.twitch.tv/oauth2/token"


def load_generic_json(filename):
    """
    Just loads a generic file, tries to json interpret it and gives back the content if everything succeeds.
    There is probably some boilerplate for that exact purpose
    :param filename:
    :return:
    """
    try:
        with open(filename, "r") as json_file:
            return json.load(json_file)
    except IOError as e:
        if e.errno == errno.ENOENT:
            logger.error(f"While loading json file {filename} no file could be found")
        elif e.errno == errno.EACCES:
            logger.error(f"While loading json file {filename} there was a lack of permission")
        else:
            logger.error(f"While loading json file {filename} some unknown error '{e}' turned up")
        return None
    except JSONDecodeError as e:
        logger.error(f"Json Decode Error in {filename}: {e}")
        return None


def token_validate(token: str) -> dict:
    """
    Validates the given twitch token against the validation API
    :param token: given 30 digits tokens
    :return: result dictionary from twitch
    """
    url = VALIDATE_URL
    validate_header = {"Authorization": f"OAuth {token}"}
    r = requests.get(url, headers=validate_header)
    if r.status_code != 200:
        handle_response_error(r.text)
        return {}
    try:
        data = json.loads(r.text)
        if 'error' in data:
            logger.error(f"TwitchData came back, but status {data['status']}: {data['message']}")
            return {}
        if data['expires_in'] < 60 * 30:  # 30 minutes left
            logger.warning(f"Token about to expire ({data['expires_in']} seconds left)")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"validate request returned with 200 but the content wasnt jsonable - {e}")
        return {}


def token_refresh(refresh: str, client_id: str, client_secret:str) -> dict:
    """
    :param refresh: secret refresh token that came with the original token
    :param client_id: the client id of that app
    :param client_secret: client secret for key generation
    :return:
    """
    url = REFRESH_URL
    package = {
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret
    }
    r = requests.post(url, data=package)
    if not r.status_code == 200:
        logger.error(f"request returned with code {r.status} instead of 200")
        handle_response_error(r.text)
        return {}
    try:
        data = json.loads(r.text)
        if 'error' in data:
            logger.error(f"TwitchData came back, but status {data['status']}: {data['message']}")
            return {}
        return data
    except json.JSONDecodeError as e:
        logger.error(f"request returned with 200 but the content wasnt jsonable - {e}")
        return {}


def handle_response_error(response):
    if is_jsonable(response):
        e_m = json.loads(response)
        if 'status' in e_m and 'error' in e_m and 'message' in e_m:
            logger.error(f"[{e_m['status']}]{e_m['error']} - {e_m['message']}")
            return e_m['message']
        else:
            logger.error(json.dumps(e_m))
            return json.dumps(e_m)
    else:
        logger.error(f"No Json: {response[:128]}")
        return response[:128]


def is_jsonable(x):
    """
    Checks if the thing can be json
    Copied & Stolen: https://stackoverflow.com/a/53112659
    :param x: an object
    :return: True/False if the thing can be json
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

