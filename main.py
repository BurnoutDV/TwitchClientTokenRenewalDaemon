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
__author__ = "BurnoutDV"
__contact__ = "development@burnoutdv.com"
__copyright__ = "Copyright 2021"
__credits__ = ["BurnoutDV"]
__date__ = "2021/08/26"
__deprecated__ = False
__email__ = "development@burnoutdv.com"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.0.1"

TOKEN_FILE = "tokens.json"

import Utility
import logging
import json
from datetime import datetime, timedelta

logging.basicConfig(filename="log.log", format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO)


def boiler_plate_expiration(a_token: dict):
    status = Utility.token_validate(a_token['token'])
    if status:
        then = datetime.now() + timedelta(seconds=int(status['expires_in']))
        a_token['expiration_date'] = then.isoformat()
        if int(status['expires_in']) > 60 * 30:  # aka. 30 minutes:
            return False
        return True
    return True


if __name__ == "__main__":
    # Load basic config file, see tokens.example.json
    tokens = Utility.load_generic_json(TOKEN_FILE)
    if not tokens:
        logging.critical(f"Cannot read {TOKEN_FILE}. Aborting process.")
        exit(0)
    for a_token in tokens:
        if 'active' not in a_token:
            a_token['active'] = True # initial set
        if a_token['active']:
            if not boiler_plate_expiration(a_token):
                continue

            resp = Utility.token_refresh(a_token['refresh_token'], a_token['client_id'], a_token['client_secret'])
            if resp:
                a_token['token'] = resp['access_token']
                a_token['scope'] = resp['scope']
                boiler_plate_expiration(a_token)
            else:
                a_token['active'] = False
    try:
        with open(TOKEN_FILE, "w") as json_file:
            json.dump(tokens, json_file, indent=4)
    except Exception as e:
        logging.critical(f"Writing failed: {e.__class__.__name__}: {e}")
        exit(1)
    print("Procedure finished")

