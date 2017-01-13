import json
import redis
from jinja2 import Environment, FileSystemLoader
from utils import ip2int, check_ip_continuous, generate_prefix_from_range, ip2int

r = redis.Redis(host='localhost', port=6379, db=0)

def read_ip_infos(fname='ip.log'):
    with open(fname, "r") as fd:
	line = fd.readline()
	while line:
	    line = line.strip()
	    clean(line)
	    line = fd.readline()

def clean(info):
    try:
	info = info.split()
	if len(info) != 4:
	    return
	start_ip = ip2int(info[0])
	end_ip = ip2int(info[1])
	region = info[2].lower()
	provider = info[3].lower()
    except :
	pass
    key = provider + "_" + region
    value = (start_ip, end_ip)
    store(key, value)

def store(key, value):
    count = r.hget(key, 'count')
    if count:	
        try:
            count = int(r.hget(key, 'count'))
            r.hincrby(key, 'count', 1)
            r.hset(key, count+1, value)
        except:
	    raise
    else:
	r.hset(key, 'count', 1)
	r.hset(key, 1, value)

def str2tuple(str1):
    str1 = str1[1:len(str1)-1]
    list1 = str1.split(',')
    assert len(list1) == 2
    num1, num2 = int(list1[0]), int(list1[1])
    return (num1, num2)

def add_ip_range(provider, ip_range_tuple):
    count = int(r.hget(provider, 'count'))
    r.hincrby(provider, 'count', 1) 
    r.hset(key, count+1, ip_range_tuple)

def delete_ip_range(provider, delete_ip_range_tuple):
    # TODO: need modify
    count = int(r.hget(provider, 'count'))
    for i in range(1, count+1):
	ip_range_tuple = str2tuple(r.hget(provider, str(i)))
        if ip_range_tuple == delete_ip_range_tuple:
	    r.hdel(provider, str(i))
    	    r.hincrby(provider, 'count', -1)

def update_ip_range(provider, old_ip_range_tuple, new_ip_range_tuple):
    count = int(r.hget(provider, 'count'))
    for i in range(1, count+1):
	ip_range_tuple = str2tuple(r.hget(provider, str(i)))
        if ip_range_tuple == old_ip_range_tuple:
	    r.hset(provider, str(i), new_ip_range_tuple)

def check_collision(new, old, new_provider=None, old_provider=None):
    new_start_ip, new_end_ip = new
    old_start_ip, old_end_ip = old

    try:
	new_start_ip, new_end_ip = int(new_start_ip), int(new_end_ip)
	old_start_ip, old_end_ip = int(old_start_ip), int(old_end_ip)
    except:
	raise
    assert new_start_ip <= new_end_ip and old_start_ip <= old_end_ip

    if new_start_ip < old_start_ip:
	if new_end_ip < old_start_ip:
	    #print "no collision"
	    pass
	elif old_start_ip <= new_end_ip < old_end_ip:
	    print "collision"
            if new_provider and old_provider:
		if new_provider != old_provider:
		    # split
                    add_ip_range(new_provider, (new_start_ip, new_end_ip))
                    update_ip_range(old_provider, (new_end_ip+1, old_end_ip))
		else:
		    # replace
		    update_ip_range(new_provider, (new_start_ip, old_end_ip))
	else:
	    print "collision"
            if new_provider and old_provider:
	        if new_provider != old_provider:
		    # new win
		    add_ip_range(new_provider, (new_start_ip, new_end_ip))
		    delete_ip_range(old_provider, (old_start_ip, old_end_ip))
	        else:
		    # replace
		    update_ip_range(new_provider, (old_start_ip, old_end_ip), (new_start_ip, new_end_ip))
		
    elif old_start_ip < new_start_ip <= old_end_ip: 
	if old_start_ip <= new_end_ip < old_end_ip:
	    print "collision"
            if new_provider and old_provider:
	        if new_provider != old_provider:
		    # split
		    add_ip_range(new_provider, (new_start_ip, new_end_ip))
		    delete_ip_range(old_provider, (old_start_ip, old_end_ip))
                    add_ip_range(old_provider, (old_start_ip, new_start_ip-1))
                    add_ip_range(old_provider, (new_end_ip+1, old_end_ip)) 
	        else:
		    # ignore
		    pass
	else:
	    print "collision"
            if new_provider and old_provider:
	        if new_provider != old_provider:
		    # split
		    add_ip_range(new_provider, (new_start_ip, new_end_ip))
		    update_ip_range(old_provider, (old_start_ip, old_end_ip), (old_start_ip, new_start_ip-1))
	        else:
		    # merge
		    update_ip_range(new_provider, (old_start_ip, old_end_ip), (old_start_ip, new_end_ip))
    else:
	#print "no collision"
	pass

def get_all_ranges():
    result = {}
    for key in r.scan_iter():
	if key not in result:
	    result[key] = []
	infos = r.hgetall(key)
	count = int(infos['count'])
	for  i in range(1, count+1):
	    ip_range = infos[str(i)]
	    result[key].append(ip_range)
    return result

def get_provider_ranges(provider):
    result = []
    infos = r.hgetall(provider)
    count = int(infos['count'])
    for i in range(1, count+1):
        ip_range = infos[str(i)]
	result.append(ip_range)
    return result

def generate_acls(provider):
    total_prefixes = []
    ip_ranges = get_provider_ranges(provider)
    for ip_range in ip_ranges:
	ip_range = str2tuple(ip_range)
	prefixes = generate_prefix_from_range(*ip_range)
        total_prefixes.extend(prefixes)
    # render template
    print render({"name": provider, "prefixes": total_prefixes})
         	    
def render(context):
    env = Environment(loader=FileSystemLoader('.'))
    return env.get_template('acl.j2').render(context)

if __name__ == "__main__":
    num1 = ip2int("1.2.8.8")
    num2 = ip2int("1.2.8.127")
    #read_ip_infos()
    print r.hgetall("cnc_guizhou")
    #print json.dumps(get_all_ranges(), indent=4)

#    ranges_dict = get_all_ranges()
#    for provider in ranges_dict:
#	ip_ranges = ranges_dict[provider]
#	for ip_range in ip_ranges:
#	    print ip_range
#	    check_collision((num1, num2), str2tuple(ip_range))


    #print render({"name": "default", "prefixes": ["192.168.1.0/24", "172.16.0.0/16", "10.0.0.0/8"]})
    #generate_acls("cm_hubei")
    for provider in r.scan_iter():
        generate_acls(provider)
