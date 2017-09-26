import PySmart
import logging

def dotest():    
    logging.basicConfig(level=logging.INFO)

    smart = PySmart.SmartInfo()
    
    logging.info('SMART initialized')
    logging.info('Read SMART')

    ret = smart.Read('D:')

    logging.info('result: {}'.format(ret))

    if (ret != 0):
        print('got error:', smart.GetErrorMessage())
    
    print(smart.BasicInfo)
    

if __name__ == '__main__':
    	dotest()
else:
	pass