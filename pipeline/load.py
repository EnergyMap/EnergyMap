import subprocess, os, math, sys
import osmium as o

#Downloads one country file from geofabrik
#Parameter, string: country
#NOTE! Only runs if you have wget on your path, and only on Linux/bash
def download_country(country, folder):
    bashCommand = f'wget http://download.geofabrik.de/europe/{country}-latest.osm.pbf -P {folder}'
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

#List of european countries for loading osm-files
europe = ['albania', 'andorra', 'austria', 'azores', 'belarus', 'belgium', 'bosnia-herzegovina', 'bulgaria', 'croatia', 'cyprus', 
              'czech-republic', 'denmark', 'estonia', 'faroe-islands', 'finland', 'france', 'georgia', 'germany', 'great-britain',
              'greece', 'guernsey-jersey', 'hungary', 'iceland', 'ireland-and-northern-ireland', 'isle-of-man', 'italy', 'kosovo', 
             'latvia', 'liechtenstein', 'lithuania', 'luxembourg', 'macedonia', 'malta', 'moldova', 'monaco', 'montenegro', 
              'netherlands', 'norway', 'poland', 'portugal', 'romania', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 
             'switzerland', 'turkey', 'ukraine']

#list of countries in Europe that have bigger osm-files than this pipeline can handle (with <=32GB RAM)
big_countries_in_europe = ['france', 'germany', 'great-britain', 'italy', 'netherlands', 'norway', 'poland', 'spain']

#Downloads the osm.pbf-files from the geofabrik-mirror into the same folder where its running
#Parameter, list: countries (can be None, then this implementation will use the list for Europe)
def download_osm_files(folder,countries):
    for country in countries:
        print("Now downloading: "+ country)
        download_country(country, folder)

#Uses osmium in a docker container to filter out only building data from osm-files
#Parameter, boolean: delete_unfiltered (default fault, that is, will not delete after filtering)
#Parameter, list: files (if none will process all osm.pbf-files in the same folder)
#Parameter, string: folder (if none will use current working directory)
def filter_out_buildings(folder, delete_unfiltered=False):
    files = [x for x in os.listdir(folder) if 'osm.pbf' in x and 'filtered' not in x]
    for file in files:
        print(f'Now filtering buildings from file: {file}...')
        bashCommand = f'docker run -w /wkd -v {folder}:/wkd stefda/osmium-tool '
        bashCommand += f'osmium tags-filter -o filtered-{file} {file} building'
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            print(error)
    if delete_unfiltered:
        for file in files:
            print(f'Deleting unfiltered file: {file}...')
            bashCommand = f'rm {os.path.join(folder,file)}'
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                print(error)
        

#Executes the docker container for osmium to split osm.pbf-files into smaller files
#parameter, dir: directory where the files are located, if None, assumes current working directory
#Parameter, string: country
#Parameter, tuple with six parameters (lon1, lat1, lon2, lat2, width, height)
#NOTE! Will not run unless you have docker on your path, only runs on Linux/bash
def split_country(file, folder, parameters):
    lon1, lat1, lon2, lat2, width, height = parameters
    for i in range(4):
        for j in range(4):
            box_lon1 = lon1+(i*width)
            box_lat1 = lat1+(j*height)
            box_lon2 = lon1+((i+1)*width)
            box_lat2 = lat1+((j+1)*height)
            coordinates = f'{box_lon1},{box_lat1},{box_lon2},{box_lat2}'
            print(f'Splitting {file} with coordinates {coordinates}... please wait.')
            bashCommand = f'docker run -it -w /wkd -v {folder}:/wkd stefda/osmium-tool osmium extract '
            bashCommand += f'--bbox={coordinates} -o part{i}{j}-{file} {file}'
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                print(error)
    
            
#Splits the osm.pbf-files in Europe that are too big for the pipeline (atleast with <=32GB RAM).
#NOTE! Here is assumed that the countries are being split from the filtered files, so "filtered" is added to filename
#Parameter, list: countries (can be None, then this implementation will use the list for big files for Europe)
def split_osm_files(folder, delete_unsplit=True):
    files = [x for x in os.listdir(folder) if 'osm.pbf' in x and os.path.getsize(os.path.join(folder,x)) > 400000000]
    for file in files:
        parameters = get_split_parameters(file, folder)
        split_country(file, folder, parameters)
        if delete_unsplit:
            print(f'Deleting original file: {file}...')
            bashCommand = f'rm {os.path.join(folder,file)}'
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                print(error)
        
#Checks the bounding box coordinates for a osm.pbf-file and returns a tuple with (lon1, lat1, lon2, lat2, width, height),
#where 'width' and 'height' are suitable specs for the smaller files to be split out of the bigger one.
def get_split_parameters(file, folder):
    f = o.io.Reader(os.path.join(folder,file), o.osm.osm_entity_bits.NOTHING)
    bbox = f.header().box()
    lon1 = math.floor(bbox.bottom_left.lon.real)
    lat1 = math.floor(bbox.bottom_left.lat.real)
    lon2 = math.ceil(bbox.top_right.lon.real)
    lat2 = math.ceil(bbox.top_right.lat.real)
    width = math.ceil((lon2-lon1) / 4)
    height = math.ceil((lat2-lat1) / 4)
    return (lon1, lat1, lon2, lat2, width, height)
    

def main():
    if len(sys.argv) > 2:
        print('Please use this script with only one argument: work-folder')
        return
    if len(sys.argv) > 1:
        folder = os.path.join(os.getcwd(),sys.argv[1])
    else:
        folder = os.getcwd()
    download_osm_files(folder, europe)
    filter_out_buildings(delete_unfiltered=True, folder=folder)
    split_osm_files(folder)

if __name__ == "__main__":
    main()