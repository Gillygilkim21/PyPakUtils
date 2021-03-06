#!/usr/bin/env python

#
# Example program for listing the files on a data logger
#
# Update the file pakbus.conf to your local settings first!
#

#
# (c) 2009 Dietrich Feist, Max Planck Institute for Biogeochemistry, Jena Germany
#          Email: dfeist@bgc-jena.mpg.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import socket
import sys
import pakbus
from bintools import str2int

#
# Initialize parameters
#

# Parse command line arguments
import optparse
parser = optparse.OptionParser()
parser.add_option('-c', '--config', help = 'read configuration from FILE [default: %default]', metavar = 'FILE', default = 'pakbus.conf')
(options, args) = parser.parse_args()

# Read configuration file
import ConfigParser, StringIO
cf = ConfigParser.SafeConfigParser()
print 'configuration read from %s' % cf.read(options.config)

# Data logger PakBus Node Id
NodeId = str2int(cf.get('pakbus', 'node_id'))
# My PakBus Node Id
MyNodeId = str2int(cf.get('pakbus', 'my_node_id'))

# Open socket
s = pakbus.open_socket(cf.get('pakbus', 'host'), cf.getint('pakbus', 'port'), cf.getint('pakbus', 'timeout'))

# check if remote node is up
msg = pakbus.ping_node(s, NodeId, MyNodeId)
if not msg:
    raise Warning('no reply from PakBus node 0x%.3x' % NodeId)

#
# Main program
#

# Upload directory data
FileData, Response = pakbus.fileupload(s, NodeId, MyNodeId, '.DIR')

#print FileData
#print '\n'


# List files in directory
filedir = pakbus.parse_filedir(FileData)



#print filedir
#print '\n'



for file in filedir['files']:
    print file
print '\n'


# pakbus address
print pakbus.getvalues(s,NodeId, MyNodeId, 'Status', 'Int4', 'PakBusAddress')
print '\n'

'''
FileData, RespCode = pakbus.fileupload(s, NodeId, MyNodeId, FileName = '.TDF')
tabledef = pakbus.parse_tabledef(FileData)

tableName = tabledef[tableno - 1]['Header']['TableName']

import time
t =  time.time()
i = 0
while i < 100:
	
	values = pakbus.getvalues(s, NodeId, MyNodeId, 'Test', 'FP2', 'PTemp')
	#print time.time()-t
	#print values
	#print '\n'
	i += 1
print time.time()-t


t = time.time()
i = 0
while i < 100:
	values = pakbus.getvalues(s, NodeId, MyNodeId, 'Test', 'FP2', 'batt_volt_Min')
	#print time.time()-t
	#print values
	#print '\n'
	i += 1
print time.time()-t


print 'HERE \n'
'''

#number = input('How many samples do you want?: ')
#FileData, RespCode = pakbus.fileupload(s, NodeId, MyNodeId, FileName = '.TDF')
#tabledef = pakbus.parse_tabledef(FileData)
#data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table')


FileData, RespCode = pakbus.fileupload(s, NodeId, MyNodeId, FileName = '.TDF')
tabledef = pakbus.parse_tabledef(FileData)




'''
# get P1 amount of most recent records
print pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x05, P1 = 10), '\n'

# get everything after record number specified by P1 (inclusive), but it can do a max of 40 records (when printing)
print pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x04, P1 = 0), '\n'

# CollectMode = 0x07 : get data within timestamp range specified by P1(not inclusive) and P2 (inclusive)
print pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x07, P1 = 770744820, P2 = 770744880), '\n'


# get data from p1 record number (inclusive) to p2 record number (non inclusive of p2)
print pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x06, P1 = 3, P2 = 8), '\n'

#
print pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x08, P1 = 1, P2 = 5), '\n'
'''


'''
import time
start_time = 770901795
asdf = []
for i in range(1000):
	begin_time = time.time()
	count = 0
	while count < 4:
		data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x07, P1 = start_time, P2 = start_time+15)
		start_time += 15
		count += 1
	#print time.time()-begin_time
	asdf += [time.time()-begin_time]
print sum(asdf)/len(asdf)
'''
#average time is 0.865349040031






'''

trying to match up the time with python time module

import time
FileData, RespCode = pakbus.fileupload(s, NodeId, MyNodeId, FileName = '.TDF')
#print FileData, '\n'
tabledef = pakbus.parse_tabledef(FileData)

data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table')
oldDataTime = data[0][0]['RecFrag'][0]['TimeOfRec'][0]
#print data, "\n"
while True:
	new_data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table')
	new_dataTime = new_data[0][0]['RecFrag'][0]['TimeOfRec'][0]
	if new_dataTime != oldDataTime:
		#print new_data
		oldDataTime = new_data[0][0]['RecFrag'][0]['TimeOfRec'][0]
		print "current time: ", time.time()
		print "datalogger time: ", new_data[0][0]['RecFrag'][0]['TimeOfRec'][0]
		diff = time.time()-time.mktime(time.strptime("31 Dec 1989 22 59 57", "%d %b %Y %H %M %S"))
		print "error: ", diff - new_data[0][0]['RecFrag'][0]['TimeOfRec'][0]
'''
import time
print time.time()
print time.localtime()
print time.strptime("1 Jan 1990", "%d %b %Y")
print "1/1/1990: ", time.mktime(time.strptime("1 Jan 1990", "%d %b %Y"))
diff = time.time()-time.mktime(time.strptime("1 Jan 1990", "%d %b %Y"))
print "current time - 1/1/1990: ", diff
#print "error: ", diff - data[0][0]['RecFrag'][0]['TimeOfRec'][0]


data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x04, P1 = 67)
print 'timestamp: ', data[0][0]['RecFrag'][0]['TimeOfRec'][0]
print time.mktime(time.strptime("12 Jun 2014 11 56 00", "%d %b %Y %H %M %S"))

'''
#oldData = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table')
#oldDataTime = oldData[0][0]['RecFrag'][0]['TimeOfRec'][0]
start_time = 770901795
end_time = 770901885

start_time -= 15
while start_time < end_time:
	
	data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table',CollectMode = 0x07, P1 = start_time, P2 = start_time)
	start_time = start_time+15
	#if data[0][0]['RecFrag'][0]['TimeOfRec'][0] != oldDataTime:
	#print data
	#	oldDataTime = data[0][0]['RecFrag'][0]['TimeOfRec'][0]
	#time.sleep(15)

	print 'Table Name: ', data[0][0]['TableName']
	print 'Begin Record Number: ', data[0][0]['BegRecNbr']

	print 'Batt Voltage: ', data[0][0]['RecFrag'][0]['Fields']['BattV'][0]
	print 'AirTemp Celsius: ', data[0][0]['RecFrag'][0]['Fields']['AirTC_2'][0]
	print 'Rain mm: ', data[0][0]['RecFrag'][0]['Fields']['Rain_mm_Tot'][0]
	print 'WaterTemp Celsius: ', data[0][0]['RecFrag'][0]['Fields']['Temp_C'][0]
	print 'Wind Direction: ', data[0][0]['RecFrag'][0]['Fields']['WindDir'][0]
	print 'SlrMJ_Tot: ', data[0][0]['RecFrag'][0]['Fields']['SlrMJ_Tot'][0]
	print 'SlrkW: ', data[0][0]['RecFrag'][0]['Fields']['SlrkW'][0]
	print 'WindSpeed m/s: ', data[0][0]['RecFrag'][0]['Fields']['WS_ms'][0]
	print 'Rel Humidity: ', data[0][0]['RecFrag'][0]['Fields']['RH_2'][0]
	print 'Water level meters: ', data[0][0]['RecFrag'][0]['Fields']['Lvl_m'][0]
	print 'PanelTemp Celsius: ', data[0][0]['RecFrag'][0]['Fields']['PTemp_C'][0]

	print 'Record Number: ', data[0][0]['RecFrag'][0]['RecNbr']
	print 'Time of Record: ', data[0][0]['RecFrag'][0]['TimeOfRec'][0]


	print 'Table Number: ', data[0][0]['TableNbr']
	print 'Number of Records Displayed: ', data[0][0]['NbrOfRecs']

	print '\n'
'''

#asdf = pakbus.fileupload(s, NodeId, MyNodeId, 'templateexample.cr1')
#print asdf, '\n'


print 'HERE HERE \n'



# say good bye
pakbus.send(s, pakbus.pkt_bye_cmd(NodeId, MyNodeId))

# close socket
s.close()
