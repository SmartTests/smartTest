import errno
import os
from datetime import datetime

def createOutputDir():
    base = os.getcwd()
    outputpath=os.path.join(os.path.dirname(base),'output')
    directoryToCreate = os.path.join(outputpath,datetime.now().strftime('%d-%m-%Y_%H_%M'))
    try:
        print(directoryToCreate)
        os.makedirs(directoryToCreate)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # This was not a "directory exist" error..

    
createOutputDir()


# os.system('cd '+outputpath)
# os.system('ls -Ur | head -1')
