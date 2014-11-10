csvfile = open("usl_spanish.csv",'r')
line = csvfile.readline()
lines = line.split("\" \"")
print len(lines)
output = open("newusl.csv",'w')
for item in lines:
	output.write(item+'\n')
output.close()
csvfile.close()
