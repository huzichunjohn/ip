import math

def generate_prefix_from_range(start_ip, end_ip):
    if start_ip > end_ip:
	raise ValueError("{} is greater than {}.".format(start_ip, end_ip))
    elif start_ip == end_ip:
	return [ get_prefix(start_ip, 1) ]
    else:
    	prefixes = []
    	current_ip = start_ip

    	while current_ip <= end_ip:
    	    if current_ip % 2 == 0:
		#print "#" * 10
		#print end_ip - current_ip
                #print current_ip, end_ip
		#print "#" * 10
	        if current_ip == end_ip:
		    prefix = get_prefix(current_ip, 1)
		    prefixes.append(prefix)
		    break
		else:
	    	    count = int(math.pow(2, int(math.log(end_ip - current_ip + 1, 2))))
	    	    prefix = get_prefix(current_ip, count)
	    	    prefixes.append(prefix)
	    	    current_ip += count
    	    else:
	    	prefixes.append(get_prefix(start_ip, 1))
	    	current_ip += 1
    	return prefixes

def get_prefix(start_ip, count):
    length = int(math.log(count, 2))
    if math.pow(2, length) != count:
	raise ValueError("{} is invalid.".format(count))
    return "{}/{}".format(int2ip(start_ip), 32 - length)
    
def int2ip(num):
    result = []
    for i in range(1, 5):
	temp = num >> (32 - 8 * i) & 0xff
	result.append(str(temp))
    return '.'.join(result)

def ip2int(ip):
    parts = ip.split('.')
    if len(parts) != 4:
	raise ValueError("{} is invalid.".format(ip))
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

def check_ip_continuous(ip1_tuple, ip2_tuple):
    return True if ip1_tuple(1) + 1 == ip2_tuple(0) or ip1_tuple(0) == ip2_tuple(1) + 1 else False

def get_network_range(prefix):
    ip, netmask = prefix.split('/')
    start_ip = ip2int(ip)
    end_ip = start_ip + int(math.pow(2, 32 - int(netmask))) - 1
    return (start_ip, end_ip)

if __name__ == "__main__":
    print ip2int("192.168.0.0")
    print int2ip(3232235520)
    print ip2int("192.168.0.255")
    print int2ip(3232235775) 
    #print get_prefix(3232235520, 256)
    #print get_prefix(3232235583, 1)
    #print generate_prefix_from_range(3232235520, 3232235775)
    #print generate_prefix_from_range(3232235521, 3232235586)
    #print get_network_range("192.168.0.1/32")
    #print get_network_range("192.168.0.2/26")
    #print get_network_range("192.168.0.66/32")

    num1 = 3232235536
    num2 = 3232235872
    print num1, num2
    prefixes = generate_prefix_from_range(num1, num2)
    print prefixes
    for prefix in prefixes:
	print get_network_range(prefix)
