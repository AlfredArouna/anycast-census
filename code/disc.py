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

from collections import OrderedDict
from math import sin, cos, acos, pi

# Index of refraction for optical fiber
FIBER_RI = 1.52
# km/s
SPEED_OF_LIGHT = 299792.458


class Disc(object):

    def __init__(self, hostname, latitude, longitude, ping):
        """
        ping (float): (in ms)
        """

        # in km:ping*98,615940132
        self._radius = ping * SPEED_OF_LIGHT / FIBER_RI / 2
        self._hostname = hostname
        self._latitude = latitude
        self._longitude = longitude

    def getHostname(self):
        return self._hostname

    def getLatitude(self):
        return self._latitude

    def getLongitude(self):
        return self._longitude

    def getRadius(self):
        return self._radius

    def getTtl(self):
        return self._ttl

    def overlap(self, other):
        """
        Two discs overlap if the distance between their centers is lower than
        the sum of their radius.
        """

        return (self.distanceFromTheCenter(other._latitude, other._longitude)) <= (self.getRadius() + other.getRadius())

    def distanceFromTheCenter(self, lat, longi):
        # Convert latitude and longitude to
        # spherical coordinates in radians.
        degrees_to_radians = pi / 180.0

        # phi = 90 - latitude
        phi1 = (90.0 - self._latitude) * degrees_to_radians
        phi2 = (90.0 - lat) * degrees_to_radians

        # theta = longitude
        theta1 = self._longitude * degrees_to_radians
        theta2 = longi * degrees_to_radians

        # Compute spherical distance from spherical coordinates.

        # For two locations in spherical coordinates
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) =
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length

        cos_noerr = (sin(phi1) * sin(phi2) * cos(theta1 - theta2) +
               cos(phi1) * cos(phi2))
        if (abs(cos_noerr - 1.0) < 0.000000000000001):
            arc = 0.0
        else:
            arc = acos(cos_noerr)

        # Remember to multiply arc by the radius of the earth
        # in your favorite set of units to get length.
        return arc * 6371

    def __str__(self):
        return "%s\t%s\t%s\t%s\n" % (self._hostname, self._latitude,  self._longitude, self._radius)


class Discs(object):

    def __init__(self):
        self._setDisc = {}
        self._orderDisc = OrderedDict()

    def getDiscs(self):
        return self._setDisc

    def removeDisc(self, disc):
        self._setDisc[disc[0].getRadius()].remove(disc)

    def overlap(self, other):
        for radius, listDisc in self._setDisc.iteritems():
            for disc in listDisc:
                if disc[0].overlap(other):
                    return True
        return False

    def add(self, disc, geolocated):
        if(self._setDisc.get(disc.getRadius()) is None):
            self._setDisc[disc.getRadius()] = [(disc, geolocated)]
        else:
            self._setDisc[disc.getRadius()].append((disc, geolocated))

    def getOrderedDisc(self):
        self._orderDisc = collections.OrderedDict(
            sorted(self._setDisc.items()))
        return self._orderDisc

    def smallestDisc(self):
        self._orderDisc = collections.OrderedDict(
            sorted(self._setDisc.items()))
        return next(iter(self._orderDisc))