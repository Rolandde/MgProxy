import sys

if sys.version_info[0] != 2:
	sys.stderr.write('MgProxy only works with Python 2')
	sys.exit()

from src.mg_proxy_creator import main

if __name__ == "__main__":
	'''Run the main program. Uncaught errors are displayed to the user.
	TODO: Also create a file with more detailed error report.
	'''
	# try:
	# 	main()
	# except:
	# 	error_msg = 'Unexpected error of type ' + str(sys.exc_info()[0]) + '\n'
	# 	sys.stderr.write(error_msg)
	main()