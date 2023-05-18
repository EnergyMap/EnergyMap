import os, sys
from process_data import process_file
from log import log
    
def main():
    folder = sys.argv[1]
    file = sys.argv[2]
    process_file(os.path.join(folder,file))
    os.rename(os.path.join(folder,file), os.path.join(folder,file+'-ready'))

if __name__ == "__main__":
    main()