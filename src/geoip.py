#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  geoip.py
#
# Copyright © 2026 Antergos NeXT
#
# This file is part of Cnchi.
#
# Cnchi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Cnchi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# The following additional terms are in effect as per Section 7 of the license:
#
# The preservation of all legal notices and author attributions in
# the material or in the Appropriate Legal Notices displayed
# by works containing it is required.
#
# You should have received a copy of the GNU General Public License
# along with Cnchi; If not, see <http://www.gnu.org/licenses/>.

""" GeoIP Location module using ip-api.com (free, no API key needed) """

import logging
import requests
import misc.extra as misc

class CountryInfo:
    """ Simple country info object matching geoip2's country shape """
    def __init__(self, name, iso_code):
        self.iso_code = iso_code
        self.names = {"en": name}

class GeoIP():
    """ Fetch geographic location via ip-api.com """

    def __init__(self):
        self._country = None
        if misc.has_connection():
            self._fetch()

    def _fetch(self):
        """ Fetch location data from ip-api.com """
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=10)
            data = resp.json()
            if data.get('status') == 'success':
                self._country = CountryInfo(
                    data.get('country', ''),
                    data.get('countryCode', ''))
                logging.debug("GeoIP: %s (%s)",
                    data.get('country'), data.get('countryCode'))
            else:
                logging.warning("GeoIP: ip-api.com error: %s",
                    data.get('message', 'unknown'))
        except Exception as e:
            logging.warning("GeoIP: request failed: %s", e)

    def get_city(self):
        return None

    def get_country(self):
        return self._country

    def get_continent(self):
        return None

    def get_location(self):
        return None

def test_module():
    """ Test module """
    geo = GeoIP()
    country = geo.get_country()
    if country:
        print("Country:", country.names.get('en', ''))
        print("ISO Code:", country.iso_code)
    else:
        print("No location data")

if __name__ == "__main__":
    test_module()
