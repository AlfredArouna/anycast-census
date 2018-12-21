#!/usr/bin/env bash
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
#

#This script analises the data from an anycast census, it requires 2 parameters
# $1 - census folder
# $2 - month of the census

function help {
            echo "
                Usage: analyseCensus.sh censusFolder month
                where: 
                - censusFolder: folder containing the census measurements
                - month: month of the census
                "
            
            }
main() {

    
    if [ -z "$1" ]
      then
        help
        exit
    fi

    if [ -z "$2" ]
      then
        help
        exit
    fi
    local censusFolder=$1; shift #censusFolder=~/measurement/measurementAnycastCensus/2017-06
    local date=$1; shift #2017-06
    echo "Starting analysing the $month census in the directory: $censusFolder"
    
    #removing tmp directory
    rm -f -r /tmp/anycastMeas;
    mkdir /tmp/anycastMeas;
    #To be safe, we copy the files in a tmp directory.
    echo "phase 0: Copying the data in a tmp directory"
    cp $(find $censusFolder | grep "\.rw") /tmp/anycastMeas

    #removing tmp directory
    rm -f -r /tmp/anycastMeasIpLong;
    mkdir /tmp/anycastMeasIpLong;
    #removing tmp directory
    rm -f -r /tmp/anycastMeasSorted;
    mkdir /tmp/anycastMeasSorted;

    echo "phase 1: converting the IPs in Long"
    if [ "$(uname)" == "Darwin" ]; then
        # MAC OS
        ls /tmp/anycastMeas/ | parallel -j $(gnproc) 'python2 code/ip2long.py /tmp/anycastMeas/{} /tmp/anycastMeasIpLong/$(basename {.} )'
        
        echo "phase 2: sorting the Long IPs"
        for file in /tmp/anycastMeasIpLong/*; do 
            gsort --parallel=$(gnproc) -n -u $file -o /tmp/anycastMeasSorted/$(basename $file); 
        done;
    else
        #LINUX
        ls /tmp/anycastMeas/ | parallel --gnu -j $(nproc) 'python2 code/ip2long.py /tmp/anycastMeas/{} /tmp/anycastMeasIpLong/$(basename {.} )'

        echo "phase 2: sorting the Long IPs"
        for file in /tmp/anycastMeasIpLong/*; do 
            sort --parallel=$(nproc) -n -u $file -o /tmp/anycastMeasSorted/$(basename $file); 
        done;
    fi

    #removing tmp directory
    rm -f -r datasets/censusData;
    mv /tmp/anycastMeasSorted/ datasets/censusData;
    rm -f -r /tmp/anycastMeas;
    rm -f -r /tmp/anycastMeasIpLong;

    echo "phase 3: finding speed of light violation"
    mkdir -p datasets/anycast-measurements-$date 
    python2 code/analyseCensus.py datasets/censusData/ datasets/planetlab-vps datasets/anycast-measurements-$date 
    
    echo 'phase 4: running iGreedy on the anycast IPs'
    mkdir -p anycast-results-$date
    cd code/igreedy/

    for file in ../../datasets/anycast-measurements-$date/*; do 
        ./igreedy -i $file -o ../../anycast-results-$date/$(basename $file)>>log-igreedy-$date;
    done;
    
    echo "Finished: results in anycast-results-$date"
}
main "$@"
