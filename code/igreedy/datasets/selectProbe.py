#!/usr/bin/env python
#usage:  python code/selectProbe.py dario-code/measurement/edgecast-ripe 480 > datasets/measurement/edgecast-ripe
import sys, time

rootFile = sys.argv[1]
km= sys.argv[2]

import math

#faster
def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    if (abs(cos - 1.0) <0.000000000001):
        arc=0.0   
    else:
        arc = math.acos( cos )
        
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc*6371

class Probe(object):
    def __init__(self, hostname, latitude, longitude,ping):

        self.hostname  = hostname
        self.latitude=latitude
        self.longitude=longitude
        self.ping=ping

 

root = open(rootFile)
#matrix=open(matrixFile, 'w')


#doesn't work!!!!
def printMatrix(testMatrix):
        for i, element in enumerate(testMatrix):
              print ' '.join(element)

#<-----------------load data----------------->
count=0
allProbes ={}
root.readline()
for line in root.readlines():
        #hostname, instance, ping, latitude, longitude = line.strip().split()
        hostname, latitude, longitude,country  = line.strip().split("\t")
        ping=0
        probe = Probe(hostname, float(latitude), float(longitude),ping)
        allProbes[count]=probe
        count+=1
root.close()
#<-----------------END load data----------------->

matrix = [["0" for x in xrange(len(allProbes))] for x in xrange(len(allProbes))] 
i=0
allProbes2=allProbes.copy() #can I  improve?

#<---------------------selectionProbe--------------------->
element=[]
array = ["-1" for x in xrange(len(allProbes))]
i=0
print "#hostname	latitude	longitude	gt	min(rtt)[ms]"
for probe in allProbes:
         if array[probe]==0: #if 0 the probe is close to another, so skip the cycle
            continue
         array[probe]=1 
         print allProbes[probe].hostname, allProbes[probe].latitude, allProbes[probe].longitude, allProbes[probe].ping
         del allProbes2[probe]
         #for el in element:
          #   del allProbes2[el]
          #  print el
         element=[]
         for other in allProbes2:
             if(distance_on_unit_sphere(allProbes[probe].latitude,allProbes[probe].longitude, allProbes2[other].latitude,allProbes2[other].longitude)<float(km)):
            #if(distance(allProbes[probe].get_point(), allProbes2[other].get_point()).kilometers<float(km)):
                array[other]=0
                element.append(other)
                #print str(probe)+"\t"+str(other)
         i+=1
