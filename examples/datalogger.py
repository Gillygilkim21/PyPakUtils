import pakbus

class DataLogger:    
    class LinkState:
        "from pg 1-3 of BMP5 Transparent Commands rev: 9/08"
        OFF_LINE = 8
        RING = 9
        READY = 10
        FINISHED = 11
        PAUSE = 12
        
    def __init__(self, host, remote_pakbus_address, 
                 local_pakbus_address = 4085, timeout = 6):
        """Connect to a remote datalogger
        
        @param host/port to connect to:
            eg: 60e90457.eairlink.com:6785,
        @param remote_pakbus_address: the address/node id to connect to
        @param local_pakbus_address: this stations node id/pakbus address [0...4095], Loggernet uses 4095                
        """
        
        self.local_address = local_pakbus_address        
        self.link_state = DataLogger.LinkState.OFF_LINE        
        self.remote_address = remote_pakbus_address
        
        host,port = host.split(":")
        self.link = pakbus.open_socket(host,int(port))                
        self.timeout = timeout
        
    def ring(self):        
        pakbus.send(self.link, 
            pakbus.Link_hdr(
                self.remote_address, self.local_address))
        
        pkt = pakbus.recv(self.link)

        print "ring got:", pakbus.decode_pkt(pkt)
    
    def hello(self):
        pakbus.send(self.link,
                    pakbus.pkt_hello_cmd(
                        self.remote_address,
                        self.local_address,
                        )[0])
        pkt = pakbus.recv(self.link)

        print "hello got:", pakbus.decode_pkt(pkt)
    
    def close(self):
        self.send(
            pakbus.pkt_byte_cmd(self.remote_address, self.local_address))
        self.link.close()
        self.link_state = DataLogger.LinkState.OFF_LINE
    
    def __del__(self):            
        if self.link_state > DataLogger.LinkState.OFF_LINE:
            self.close()
    