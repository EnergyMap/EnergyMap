import subprocess, os, math
import osmium as o

#Downloads one country file from geofabrik
#Parameter, string: country
def download_country(country):
    bashCommand = f'wget http://download.geofabrik.de/europe/{country}-latest.osm.pbf'
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
def download_osm_files(countries=None):
    if countries is None:
        countries = europe
    for country in europe:
        print(country)
        #download_country(country)

#Executes the docker container for osmium to split osm.pbf-files into 9 smaller files
#Parameter, string: country
#Parameter, tuple with six parameters (lon1, lat1, lon2, lat2, width, height)
def split_country(country, parameters):
    print(parameters)
    lon1, lat1, lon2, lat2, width, height = parameters
    for i in range(3):
        for j in range(3):
            box_lon1 = lon1+(i*width)
            box_lat1 = lat1+(j*height)
            box_lon2 = lon1+((i+1)*width)
            box_lat2 = lat1+((j+1)*height)
            coordinates = f'{box_lon1},{box_lat1},{box_lon2},{box_lat2}'
            print(f'Splitting {country} with coordinates {coordinates}... please wait.')
            bashCommand = f'docker run -it -w /wkd -v {os.getcwd()}:/wkd stefda/osmium-tool osmium extract '
            bashCommand += f'--bbox={coordinates} -o {country}-{i}{j}-latest.osm.pbf {country}-latest.osm.pbf'
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(error)
            
#Splits the osm.pbf-files in Europe that are too big for the pipeline (atleast with <=32GB RAM).
#Parameter, list: countries (can be None, then this implementation will use the list for big files for Europe)
def split_osm_files(countries=None):
    if countries is None:
        countries = big_countries_in_europe
    for country in countries:
        parameters = get_split_parameters(country)
        split_country(country, parameters)
        
#Checks the bounding box coordinates for a osm.pbf-file and returns a tuple with (lon1, lat1, lon2, lat2, width, height),
#where 'width' and 'height' are suitable specs for the smaller files to be split out of the bigger one.
def get_split_parameters(country):
    f = o.io.Reader(f'{country}-latest.osm.pbf', o.osm.osm_entity_bits.NOTHING)
    bbox = f.header().box()
    lon1 = math.floor(bbox.bottom_left.lon.real)
    lat1 = math.floor(bbox.bottom_left.lat.real)
    lon2 = math.ceil(bbox.top_right.lon.real)
    lat2 = math.ceil(bbox.top_right.lat.real)
    #print(lat2 - lat1)
    width = math.ceil((lon2-lon1) / 3)
    height = math.ceil((lat2-lat1) / 3)
    return (lon1, lat1, lon2, lat2, width, height)
    

def main():
    download_osm_files()
    #split_big_countries()

if __name__ == "__main__":
    main()