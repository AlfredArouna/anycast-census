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


from socket import inet_aton
from struct import unpack
from sys import argv


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = inet_aton(ip)
    return unpack("!L", packedIP)[0]


def main():
    VPFile = open(argv[1])
    VPFile.readline()
    result = []
    for line in VPFile.readlines():
        try:
            ip, rtt = line.strip().split("\t")
            result.append([ip2long(ip), float(rtt)])
        except Exception as e:
            print "Warning: skipping malformed line("+ line +") in \t" + argv[1]

    output = open(argv[2], 'w')
    output.write("#ipLong\trtt\n")
    for element in result:
        output.write(str(element[0]) + "\t" + format(element[1], '.5f') + "\n")
    output.close()
if __name__ == "__main__":
    main()
