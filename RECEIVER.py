import socket
import sys
import os
import time
import random

next_seq = 0

def write_to_file(filename,data_list):
	f = open(filename,'wb')
	# data_list.sort()
	# print data_list
	# for i in data_list:
	# 	print "writing seq no:" + str(i)
	# 	f.write(str(data_list[i]))
	for key in sorted(data_list.iterkeys()):
#		print key
		f.write(data_list[key])
	f.close()

def decimal_to_binary(number,total_number):
	get_bin = lambda x: format(x,'b')
	value = get_bin(number)
	size = len(value)
	str1 = ''
	for i in xrange(total_number-size):
		str1= '0' + str1
	return str1 + str(value)

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = ord(data[i]) + (ord(data[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

def verify_checksum(message,senderchecksum):
	calculatechecksum = checksum(message)
	bcalculatechecksum = decimal_to_binary(calculatechecksum,16)
	if(bcalculatechecksum == senderchecksum):
		return 1		
		#pass
		#print 'Checksum verified: Correct Data'
	else:
		return 0
		#print 'Invalid Checksum: Dropping the packet'

def ack_send(serversocket,sequenceno,destaddress):
	zero = '0000000000000000'
	ackpkt = '1010101010101010'
	msg = str(sequenceno) + zero + ackpkt
	#print msg
	serversocket.sendto(msg,destaddress)

def main():
	global next_seq
	port = 7765
	sequenceno = 0
	hostname = socket.gethostname()
#	print hostname
	if len(sys.argv) != 4:
		print 'Invalid Argument: Must have 4 parameters'
		exit()
	else:
		serverPort = int(sys.argv[1])
		filename = sys.argv[2]
		probability = float(sys.argv[3])
	if os.path.exists(filename):
		os.remove(filename)
	#print serverPort, filename, probability
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serversocket.bind(("", port))
	packet_list = []
	data_list = {}
	while True:
		data,addr = serversocket.recvfrom(1500)
		loss_prob = random.random()
		sequenceno = data[0:32]
		senderchecksum = data[32:48]
		senderack = data[49:63]
		message = data[64:]
		convert_int = str(sequenceno)
		convert_int_seq = int(convert_int,2)
		#print 'SEQUENCE NUMBER : ' + str(convert_int_seq)
		if loss_prob <= float(probability):
			print 'Packet Loss, Sequence Number:(p)'+str(convert_int_seq)
			continue
		data_list[convert_int_seq] = message
		#data_list.append(convert_int_seq,str(data))
		if verify_checksum(message,senderchecksum):
			ack_number = convert_int_seq +len(message)
		#	print 'Ack in string form: ' + str(ack_number)
			b_ack = decimal_to_binary(ack_number,32)
			ack_number = convert_int_seq +len(message)
			#print 'Ack in string form: ' + str(ack_number)
	#		b_ack = decimal_to_binary(ack_number)
			write_to_file(filename,data_list)

			ack_send(serversocket,b_ack,addr)
		else:
			print 'Packet Loss, Sequence Number:(c)' + str(convert_int_seq)		 

if __name__ == '__main__':
	main()
