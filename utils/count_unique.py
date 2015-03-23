f = open('log.txt')

file_stuff = f.read()
lines = file_stuff.split()
page_nos = set()

for line in lines:
	virt_addr, pid = line.split(',')
	page_no = int(virt_addr, 16) >> 12
	page_nos.add(page_no)

print len(page_nos)
