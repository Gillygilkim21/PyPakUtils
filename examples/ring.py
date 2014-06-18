# code to ring a node using link-level messaging

import ConfigParser, StringIO
import optparse
from datalogger import DataLogger

def main():
    # Parse command line arguments
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', 
                      help = 'read configuration from FILE [default: %default]', 
                      metavar = 'FILE', 
                      default = 'campbell.conf')
    (options, args) = parser.parse_args()
    
    # Read configuration file

    cf = ConfigParser.SafeConfigParser()
    print 'configuration read from %s' % cf.read(options.config)
        
    for pakbus_id in cf.get('pakbus', 'dataloggers').split(','):
        pakbus_id = int(pakbus_id, base = 0)
        dl = DataLogger(cf.get('pakbus', 'host'),
                        pakbus_id,
                        int(cf.get('pakbus', 'my_node_id'), base = 0),
                        cf.getint('pakbus', 'timeout'))
        print "ringing node {}...".format(pakbus_id)
        
        dl.ring()
        dl.hello()
        
        
    
if __name__ == "__main__":
    main()

