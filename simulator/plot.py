import matplotlib.pyplot as plt

y_file_name = "page_stream_accesses"
y_file = open(y_file_name, "r")
y = y_file.read().split()
x = []

time = 0.01

for val in y:
	x.append(time)
	time += 0.01

plt.plot(x, y)
plt.show()
y_file.close()

	
