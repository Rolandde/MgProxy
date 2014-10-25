import sys
if sys.version_info[0] != 2:
    sys.stderr.write('MgProxy only works with Python 2')
    sys.exit()


from src.mg_proxy_creator import main

if __name__ == "__main__":
    '''Run the main program.'''
    main()
