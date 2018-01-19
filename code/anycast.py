#!/usr/bin/env python
#
# Telecom Paristech
# cicalese@enst.fr
#
# Authors: Danilo Cicalese, Dario Rossi
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


from disc import *
from collections import OrderedDict


class Anycast(object):

    def __init__(self, dataArray):
        # disc from the input
        self._setDisc = {}
        # disc belong maximum indipendent set
        self._discsMis = Discs()

        # load the data in a structure has as key the ping--------
        # Example structure:
        # {ping1:[Disc1,Disc2,Disc3],ping2:[Disc3,Disc4,Disc5]}
        for columns in dataArray:
            hostname, latitude, longitude, minRTT = columns[0:4]

            if(self._setDisc.get(float(minRTT)) is None):
                self._setDisc[float(minRTT)] = [Disc(hostname, float(
                    latitude), float(longitude), float(minRTT))]
            else:
                self._setDisc[float(minRTT)].append(
                    Disc(hostname, float(latitude), float(longitude), float(minRTT)))
        self.orderDisc = OrderedDict(
            sorted(self._setDisc.items()))  # order the discs by ping

    def detection(self):
        self._discsMis = Discs()
        for ping, _setDiscs in self.orderDisc.iteritems():
            for disc in _setDiscs:
                if not self._discsMis.overlap(disc):
                    self._discsMis.add(disc, False)
                    if(len(self._discsMis.getDiscs()) > 1):
                        return True
        return False