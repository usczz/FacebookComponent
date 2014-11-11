from datetime import datetime
import calendar

d = datetime.utcnow()
print d.year
y = d.year
newd = d.replace(year=y-1)
print newd

timestamp = calendar.timegm(d.utctimetuple())

print timestamp

timestamp = calendar.timegm(newd.utctimetuple())
print repr(timestamp)
print repr(str(timestamp))
print timestamp
