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


# exmaple of usage:
#python code/analyseCensus.py datasets/censusData/ datasets/planetlab-vps results-2017-02

from sys import argv
from os import listdir
from struct import pack
from anycast import Anycast
from itertools import islice
from socket import inet_ntoa


# 1 the files have to be sorted
# 2 the IPs should be long

def loadVPs(inputFile):
    VPsInfo = {}
    for line in open(inputFile).readlines():
        if(line.startswith("#")):
            continue
        # VP,lat,long
        columns = line.strip().split("\t")
        VPsInfo[columns[0]] = columns
    return VPsInfo


def main():
    # slice size
    numberLine = 1000000
    folderCensus = argv[1]
    cachedInfoPerVp = {}
    # index of line we have to read
    lineVP = {}

    # load vps information
    VPsInfo = loadVPs(argv[2])
    # create an index per each line and load first block
    for VP in listdir(folderCensus):
        lineVP[VP] = [0, 0]  # ip,rtt
        cachedInfoPerVp[VP] = [
            open(folderCensus + "/" + VP, "r")]  # pointer to file
        cachedInfoPerVp[VP].append(
            islice(cachedInfoPerVp[VP][0], numberLine))  # load the first block
        next(cachedInfoPerVp[VP][0])  # skip the header

    # current IP set to 255.255.255.255 (in long 4294967295)
    currentIP = 4294967295
    count = 0
    while(len(lineVP) > 0):
        # there is at least one file with the information
        count += 1
        # track the smallest IP
        minIP = 4294967295
        # list of VPs containing the minIP
        VPsWithMinimumIP = []

        for VP in lineVP:
            infoVP = lineVP[VP]
            ipVP = long(infoVP[0])

            # if the current IP is smaller or equal than the one in currentIP,
            # read new

            if(ipVP <= currentIP):
                try:
                    # read the new line
                    newValue = next(cachedInfoPerVp[VP][1]).strip().split('\t')
                # no new line in the block
                except StopIteration:
                    # loading a new block of lines
                    try:
                        cachedInfoPerVp[VP][1] = islice(
                            cachedInfoPerVp[VP][0], numberLine)
                        # read the new line
                        newValue = next(cachedInfoPerVp[VP][
                                        1]).strip().split('\t')
                    except StopIteration:
                        # we read all the lines of the file
                        # delete it
                        del lineVP[VP]
                        break

                lineVP[VP] = newValue  # updating the info
                infoVP = lineVP[VP]
                ipVP = long(infoVP[0])
            # search for the smaller IP
            if(ipVP < minIP):
                # new min IP, reinitialise the list
                VPsWithMinimumIP = [[VP, infoVP[1]]]  # list of VP,rtt
                minIP = ipVP
            elif(ipVP == minIP):
                # the IP contains the min IP, we save the info
                VPsWithMinimumIP.append([VP, infoVP[1]])
        # update the currentIp we are analyzing
        currentIP = minIP

        anycastArray = []
        if len(VPsWithMinimumIP) > 1:
            for el in VPsWithMinimumIP:
                # VP,latitude,longitude,rtt
                VPsLatLong = VPsInfo[el[0].split("_")[0]]
                anycastArray.append(
                    [el[0], VPsLatLong[1], VPsLatLong[2], el[1]])
            anycast = Anycast(anycastArray)
            if(anycast.detection()):
                IP = inet_ntoa(pack('!L', currentIP))
                # to add in an array and print only at the end
                for measure in anycastArray:
                    # for each IP, save the info in a different file
                    anycastFile = open(
                        argv[3] + "/" + str(IP) + "-" + str(currentIP), 'a')
                    anycastFile.write("\t".join(measure) + "\n")
                anycastFile.close()

if __name__ == "__main__":
    main()
