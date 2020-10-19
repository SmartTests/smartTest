import errno
import os
from datetime import datetime
# Last modified Aug 03, 2020 by Kesina Baral
#creates new folder within output folder to store results


def createOutputDir():
    base = os.getcwd()
    outputpath=os.path.join(os.path.dirname(base),'output')
    newFolder = datetime.now().strftime('%d-%m-%Y_%H_%M_%S')
    directoryToCreate = os.path.join(outputpath,newFolder)
    try:
        print(newFolder)
        os.makedirs(directoryToCreate)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # This was not a "directory exist" error..


createOutputDir()


# os.system('cd '+outputpath)
# os.system('ls -Ur | head -1')
