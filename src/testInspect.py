import inspect

def add(a,b):
	res = a+b
	current_line_no = inspect.stack()[0][2]
	current_function_name = inspect.stack()[0][3]
	print current_line_no
	print current_function_name
	print inspect.stack()
	return res	

def main():
	file_name = __file__ 
	current_line_no = inspect.stack()[0][2]
	print file_name
	print current_line_no
	print inspect.stack()
	add(1,2)
	print inspect.stack()

if __name__ == '__main__':
	main()