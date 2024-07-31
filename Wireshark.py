import sys
import socket 
from struct import *

def getMacAdddr(myData):
    myMAC = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (myData[0], myData[1], myData[2], myData[3], myData[4], myData[5])
    return myMAC

try:
    mySocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
except Exception as msg:
    print("Socket could not be created. Error code:" + str(msg))
    sys.exit()
# receive a pocket 
while True:
    packet = (mySocket.recvfrom(65565))
    # packet string from tuple
    myPacket = packet[0]
    print("-"*50)
    #parse ethernet header
    myEthLength = 14
    myEthHeader = myPacket[:myEthLength]
    myEth = unpack('!6s6sH', myEthHeader)
    myEthProtocol = socket.ntohs(myEth[2])
    print('Destination MAC : ' + getMacAdddr(str(myPacket[0:6])) + 'Source MAC : ' + getMacAdddr(str(myPacket[6:12])) + 'Protocol : ' + str(myEthProtocol))

    #Parse IP packets, IP Protocol number = 8
    if myEthProtocol == 8:
        #Parse IP header
        #take first 20 character for this the IP header
        myIPHeader = myPacket[myEthLength:20+myEthLength]
        #now unpack them :)
        iph = unpack('!BBHHHBBH4s4s', myIPHeader)
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        myIPHeaderLength = ihl * 4
        ttl = iph[5]
        protocol = iph[6]
        mySrcIP = socket.inet_ntoa(iph[8])
        myDstIP = socket.inet_ntoa(iph[9])

        print('Version : ' + str(version) + 'IP Header Length : ' + str(ihl)+ ' TTL : ' + str(ttl) + 'Protocol : ' + str(protocol) + 'Source IP : ' + str(mySrcIP)+ 'Destination IP : ' + str(myDstIP))

        #TCP protocol
        if protocol == 6:
            t = myIPHeaderLength + myEthLength
            myTCPHeader = myPacket[t:t+20]
            #now unpack them :)
            tcph = unpack('!HHLLBBHHH',myTCPHeader)
            mySrcPort = tcph[0]
            myDstPort = tcph[1]
            sequence = tcph[2]
            acknowledgement = tcph[3]
            doff_reserved = tcph[4]
            tcph_length = doff_reserved >> 4
            print('Source Port : ' + str(mySrcPort)+ 'Destination Port : ' + str(myDstPort)+ 'Sequence Number : ' + str(sequence)+ 'Acknowledgement : ' + str(acknowledgement) + 'TCP header Length : ' + str(tcph_length))
            
            myHeaderSize = myEthLength + myIPHeaderLength + tcph_length * 4
            myPkData = myPacket[myHeaderSize:]
            print('Data : ' + str(myPkData))
        #ICMP Packets
        elif protocol == 1:
            u = myIPHeaderLength + myEthLength
            myICMPHeaderLength = 4
            icmp_header = myPacket[u:u+4]

            #now unpack them :)
            icmph = unpack('!BBH', icmp_header)

            icmp_type = icmph[0]
            code = icmph[1]
            checksum = icmph[2]

            print('Type : ' + str(icmp_type)+ 'Code : ' + str(code)+ 'checksum : ' + str(checksum))
            myHeaderSize = myEthLength + myIPHeaderLength + myICMPHeaderLength
            myPktDataSize = len(myPacket) - myHeaderSize
            myPktData = myPacket[myHeaderSize:]
            print('Data : ' + myPktData)
        #UDP packets
        elif protocol == 17:
            u = myIPHeaderLength + myEthLength
            myUDPHeaderLength = 8
            myUDPHeader = myPacket[u:u+8]

            #now unpack them :)
            udph = unpack('!HHHH', myUDPHeader)
            mySrcPort = udph[0]
            myDstPort = udph[1]
            length = udph[2]
            checksum = udph[3]

            print('Source Port : ' + str(mySrcPort)+ 'Destination Port : ' + str(myDstPort) + 'Length : ' + str(length)+ 'checksum : ' + str(checksum))
            myHeaderSize = myEthLength + myIPHeaderLength + myUDPHeaderLength
            myPktDataSize = len(myPacket) - myHeaderSize

            #get data from the packet 
            myPktData = myPacket[myHeaderSize:]
            print('Data : ' + str(myPktData))

        #Some other IP packet like IGMP
        else:
            print('Protocol other than TCP/UDP/ICMP')
