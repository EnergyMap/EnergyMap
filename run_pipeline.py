import sys, os, psutil, subprocess
from pipeline.log import log

def list_files(folder):
    return [x for x in os.listdir(folder) if '.osm.pbf' in x and '-ready' not in x]
    
def main():
    if len(sys.argv) > 3:
        print('Please use this script with two arguments: name of python in bash, e.g. "python3", and work-folder')
        return
    if len(sys.argv) > 2:
        folder = os.path.join(os.getcwd(),sys.argv[2])
    else:
        folder = os.getcwd()
    files = list_files(folder)
    for file in files:
        log('Handling file ' + file)
        log('Using memory before handling file '+str(psutil.virtual_memory().percent))
        bashCommand = f'{sys.argv[1]} pipeline/process_file.py {folder} {file}'
        #print(bashCommand)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            print(error)
        log('Using memory after handling file '+str(psutil.virtual_memory().percent))

if __name__ == "__main__":
    main()