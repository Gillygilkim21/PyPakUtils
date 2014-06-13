'''
Idea behind everything

1. get most recent entry from database
2. get most recent value from datalogger
3. if there is a time gap, then collect from missing time to most recent value

4. loop through and put data into database once time changes (every min or so)

5. if there is a failure, then save the most recent time of value from datalogger
6. once connection reestablished, collect from missing time to most recent value

7. go back to 4
'''
import string
# removes illegal characters from string
def make_follow_tag_rules(s):
        '''remove " ", "^", "%"'''
        s = string.replace(s, " ", "_")
        s = string.replace(s, "^", "")
        s = string.replace(s, "%", "Percent")
        return s

# check connections to list of devices
def check_connections(s, device_list, pakbus_address_list, MyNodeId):
        failed_nodes_list = []
        succeed_nodes_list = []
        for i in range(len(device_list)):
                if (i == 0):
                        msg = pakbus.ping_node(s, pakbus_address_list[i], MyNodeId)
                else:
                        msg = pakbus.ping_node(s, pakbus_address_list[i], MyNodeId, IsRouter = 0, HopCnt = 1)
                if not msg:
                #raise Warning('no reply from PakBus node/address 0x%.3x' % pakbus_address_list[i]
                        #print 'no reply from PakBus node/address: 0x%.3x' % pakbus_address_list[i]
                        #print 'no reply from device name: %s' % device_list[i]
                        failed_nodes_list += [device_list[i]]
                else:
                        succeed_nodes_list += [device_list[i]]

##        for i in range(4096):
##                msg = pakbus.ping_node(s, i, MyNodeId)
##                if not msg:
##                #raise Warning('no reply from PakBus node/address 0x%.3x' % pakbus_address_list[i]
##                        #print 'no reply from PakBus node/address: 0x%x' % i
##                        failed_nodes_list += [i]
##                        print 'node', i, 'failed'
##                else:
##                        succeed_nodes_list += [i]
##                        print 'node', i, 'worked'
        
        return failed_nodes_list, succeed_nodes_list

# get info of sensors on successful connections
def update_sensor_information(device_list, pakbus_address_list, MyNodeId, succeed_nodes_list):
        '''data_store_into_table_rate = []
        sensor_name = []
        sensor_unit = []
        sensor_processing = []
        sensor_count_for_devices = []
        table_names = []
        field_count_for_tables = []'''
        data_store_into_table_rate = {}
        sensor_name = {}
        sensor_unit = {}
        sensor_processing = {}
        sensor_count_for_devices = {}
        table_names = {}
        field_count_for_tables = {}
        for i in range(len(device_list)):
                count = 0
                data_store_into_table_rate[device_list[i]] = []
                sensor_name[device_list[i]] = []
                sensor_unit[device_list[i]] = []
                sensor_processing[device_list[i]] = []
                sensor_count_for_devices[device_list[i]] = 0
                table_names[device_list[i]] = []
                field_count_for_tables[device_list[i]] = []
                # ignore those that you can't connect to
                if (device_list[i] in succeed_nodes_list):
                        FileData, RespCode = pakbus.fileupload(s, pakbus_address_list[i], MyNodeId, FileName = '.TDF')
                        tabledef = pakbus.parse_tabledef(FileData)

                        if FileData:
                                for tableno in range(1, len(tabledef) + 1):
                                        # ignore tables "Public" and "Status"
                                        if tabledef[tableno - 1]['Header']['TableName'] != "Public" and tabledef[tableno - 1]['Header']['TableName'] != "Status":
                                                table_names[device_list[i]] += [tabledef[tableno - 1]['Header']['TableName']]
                                                data_store_into_table_rate[device_list[i]] += [tabledef[tableno - 1]['Header']['TblInterval'][0]]
                                                # get all of the sensors connected and their information
                                                for fieldno in range(1, len(tabledef[tableno - 1]['Fields']) + 1):
                                                        count += 1
                                                        sensor_name[device_list[i]] += [make_follow_tag_rules(tabledef[tableno - 1]['Fields'][fieldno - 1]['FieldName'])]
                                                        sensor_unit[device_list[i]] += [make_follow_tag_rules(tabledef[tableno - 1]['Fields'][fieldno - 1]['Units'])]
                                                        sensor_processing[device_list[i]] += [make_follow_tag_rules(tabledef[tableno - 1]['Fields'][fieldno - 1]['Processing'])]
                                                field_count_for_tables[device_list[i]] += [len(tabledef[tableno - 1]['Fields'])]
                sensor_count_for_devices[device_list[i]] = count
        return data_store_into_table_rate, sensor_name, sensor_unit, sensor_processing, sensor_count_for_devices, table_names, field_count_for_tables

# create tags for sensors on successful connections
def create_tags(device_list, sensor_count_for_devices, sensor_name, sensor_unit, sensor_processing):
        tags = {}
        for i in range(len(device_list)):
                tags[device_list[i]] = []
                for j in range(sensor_count_for_devices[device_list[i]]):
                        tags[device_list[i]] += [Tags(conf, device_list[i])]
                        tags[device_list[i]][j].addTag("sensor_name", sensor_name[device_list[i]][j])
                        tags[device_list[i]][j].addTag("sensor_unit", sensor_unit[device_list[i]][j])
                        tags[device_list[i]][j].addTag("sensor_processing", sensor_processing[device_list[i]][j])
                # add tag for record number
                if (sensor_count_for_devices[device_list[i]] > 0):
                        tags[device_list[i]] += [Tags(conf, device_list[i])]
                        tags[device_list[i]][sensor_count_for_devices[device_list[i]]].addTag("sensor_name", "RecordNumber")
        return tags


# update database to contain start to end record number of all devices
# "table_names", "sensor_name", and "tags" are lists
# "sensor_count_for_devices" is a number
def update_database(tabledef, device_list, succeed_nodes_list, pakbus_address_list, MyNodeId, table_names, sensor_name, tags, sensor_count_for_devices, addition_size = 1):

        # need to somehow get last entry into database for specific "tabledef"
        # and then get the record number of it

        # if no data in database for specific "tabledef"
        # then "start_record_number = 0"

        start_record_number = 0
        total = 0
        for i in range(len(table_names)):
                data = pakbus.collect_data(s, pakbus_address_list[i], MyNodeId, tabledef, table_names[i], CollectMode = 0x05, P1 = 1)
                end_record_number = data[0][0]['RecFrag'][0]['RecNbr']
 

                data_to_add_to_database = []

                count = 0
                while start_record_number < end_record_number:
                        data = pakbus.collect_data(s, pakbus_address_list[i], MyNodeId, tabledef, table_names[i], CollectMode = 0x06, P1 = start_record_number, P2 = start_record_number+1)
                        sensors = data[0][0]['RecFrag'][0]['Fields']
                        # add time offset to match python time
                        time_stamp = data[0][0]['RecFrag'][0]['TimeOfRec'][0] + 631166400
                        #print 'record number: ', start_record_number
                        start_record_number += 1
                        for j in range(sensor_count_for_devices):
                                #to take out issue with "NaN"
                                try:
                                        int(sensors[sensor_name[j]][0])
                                        data_to_add_to_database += [(time_stamp, sensors[sensor_name[j]][0], tags[j])]
                                except:
                                        data_to_add_to_database += [(time_stamp, -1, tags[j])]
                        # for record number
                        data_to_add_to_database += [(time_stamp, start_record_number-1, tags[sensor_count_for_devices])]
                        count += 1
                        #print data_to_add_to_database
                        #print time.localtime(time_stamp), '\n'
                        if (count == addition_size):
                                total += count
                                print client.multiplePut(data_to_add_to_database), '     total: ', total
                                count = 0
                                data_to_add_to_database = []
                if (len(data_to_add_to_database) != 0):
                        total += count
                        print client.multiplePut(data_to_add_to_database), '     total: ', total



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
parser.add_option('-c', '--config', help = 'read configuration from FILE [default: %default]', metavar = 'FILE', default = 'GilbertTest.conf')
(options, args) = parser.parse_args()

# Read configuration file
import ConfigParser, StringIO
cf = ConfigParser.SafeConfigParser()
print 'configuration read from %s' % cf.read(options.config)

# Data logger PakBus Node Id
# NodeId = str2int(cf.get('pakbus', 'node_id'))
# My PakBus Node Id
MyNodeId = str2int(cf.get('pakbus', 'my_node_id'))

# Open socket
s = pakbus.open_socket(cf.get('pakbus', 'host'), cf.getint('pakbus', 'port'), cf.getint('pakbus', 'timeout'))






# normal time between each update to database from datalogger tables
database_update_time_gap = str2int(cf.get('GilbertTest', 'database_update_time_gap'))

# time gap when it retries connections to list of devices and updates list
connection_retry_time = str2int(cf.get('GilbertTest', 'connection_retry_time'))

if (connection_retry_time < database_update_time_gap):
        raise Warning('"database_update_time_gap" is bigger than "connection_retry_time"')



# list of device names
import ast
device_list = ast.literal_eval(cf.get('GilbertTest', 'device_list'))

# pakbus addresses of devices
pakbus_address_list = ast.literal_eval(cf.get('GilbertTest', 'pakbus_address'))
pakbus_address_list = [str2int(x) for x in pakbus_address_list]

if (len(device_list) != len(pakbus_address_list)):
        raise Warning('"device_list" and "pakbus_address_list" must have the same length')




failed_nodes_list, succeed_nodes_list = check_connections(s, device_list, pakbus_address_list, MyNodeId)
print "failed_nodes_list: ", failed_nodes_list
print "succeed_nodes_list: ", succeed_nodes_list

'''

# things can go wrong here with connection with datalogger devices
data_store_into_table_rate, sensor_name, sensor_unit, sensor_processing, sensor_count_for_devices, table_names, field_count_for_tables = update_sensor_information(device_list, pakbus_address_list, MyNodeId, succeed_nodes_list)
print "data_store_into_table_rate: ", data_store_into_table_rate
print "sensor_name: ", sensor_name
print "sensor_unit: ", sensor_unit
print "sensor_processing: ", sensor_processing
print "sensor_count_for_devices: ", sensor_count_for_devices
print "table_names: ", table_names
print "field_count_for_tables: ", field_count_for_tables




from Client import *
# create configuration for sensor client
conf = Configuration()

# create a sensor client
client = SensorClient(conf)

# create individual tags
# tags should not have spaces
# nothing should go wrong here with connection with datalogger devices
tags = create_tags(device_list, sensor_count_for_devices, sensor_name, sensor_unit, sensor_processing)
print "tags: ", tags

import time




for i in range(len(device_list)):
        device = device_list[i]
        if device in succeed_nodes_list:
                try:
                        FileData, RespCode = pakbus.fileupload(s, pakbus_address_list[i], MyNodeId, FileName = '.TDF')
                        tabledef = pakbus.parse_tabledef(FileData)
                        update_database(tabledef, device_list, succeed_nodes_list, pakbus_address_list, MyNodeId, table_names[device], sensor_name[device], tags[device], sensor_count_for_devices[device], addition_size=100)
                except:
                        print 'something went wrong here with device', device

                print "done here", '\n'







# infinite loop to constantly collect data every number of seconds specified in config file
##time_so_far = 0
while True:	
        time.sleep(database_update_time_gap)
##        time_so_far += database_update_time_gap
        for i in range(len(device_list)):
                device = device_list[i]
                if device in succeed_nodes_list:
                        try:
                                FileData, RespCode = pakbus.fileupload(s, pakbus_address_list[i], MyNodeId, FileName = '.TDF')
                                tabledef = pakbus.parse_tabledef(FileData)
                                update_database(tabledef, device_list, succeed_nodes_list, pakbus_address_list, MyNodeId, table_names[device], sensor_name[device], tags[device], sensor_count_for_devices[device])
                        except:
                                print 'something went wrong here with device', device
                        print 'did this'
            
##        if (time_so_far >= connection_retry_time):
##                time_so_far = 0
##                failed_nodes_list, succeed_nodes_list = check_connections(device_list, pakbus_address_list, MyNodeId)
##                print 'checked this'


'''





# how should I get most recent entry in datalogger?
# what if some devices disconnect early while others stay connected?
# what happens when i try to get data for record numbers when the record numbers don't exist
# what if the record numbers dont match up between cr1000 and cr800
# what if record numbers dont match up between sensors for cr1000
#       (sensors wired in at diff points so start at diff record numbers)



# need to use combination of timestamp and record number




'''
import time
print time.time()
print client.now()


# infinite loop to constantly collect data every minute
while True:	
	time.sleep(time_gap-0.865349040031)
	count = 0
	while count < 4:
		data = pakbus.collect_data(s, NodeId, MyNodeId, tabledef, 'Table', CollectMode = 0x07, P1 = start_time, P2 = start_time+sample_gap)
		start_time += sample_gap
		count += 1


#always check that most recent input is 15 sec before next input


print '\n'
# query data
start = client.now() - 2000000
print client.singleQuery(start, client.now(), BattV)

'''



# say good bye
for i in range(len(device_list)):
        if device_list[i] not in failed_nodes_list:
                pkt = pakbus.pkt_bye_cmd(pakbus_address_list[i], MyNodeId)
                pakbus.send(s, pkt)

# close socket
s.close()
