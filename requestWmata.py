import requests
import time
import readchar

def sort_by_arrival(train_data):
    arrival_time_index = 3
    arrival_time = train_data[arrival_time_index]
    if(arrival_time) == 'BRD':
        return -1
    elif(arrival_time) == 'ARR':
        return 0
    elif(arrival_time) == 'DLY':
        return 100
    elif(arrival_time) == '':
        return 50
    elif(arrival_time) == '---':
        return 51
    #add a generic catch here
    else:
        try:
            return int(arrival_time)
        except Exception as e:
            return 52

def construct_multi_track_station_code_mapa(stations_data):
    multi_track_station_code_map = {}
    stations_data_list = stations_data['Stations']
    for station in stations_data_list:
        station_name = station['Name']
        station_code = station['Code']
        for station_two in stations_data_list:
            station_two_name = station_two['Name']
            station_two_code = station_two['Code']
            if(station_name == station_two_name and station_code != station_two_code):
                multi_track_station_code_map[station_code] = station_two_code
    return multi_track_station_code_map

line_index = 0
station_index = 0
while True:
    try:
        api_key = 'b18ceda221c645d5bd1d5386f40ca0e1'
        base_url = 'https://api.wmata.com/'
        headers = {
            'api_key': api_key,
        }
        stations_endpoint = "/Rail.svc/json/jStations/"
        line_codes = ['RD', 'BL', 'YL', 'OR', 'GR', 'SV']
        healthy_status = 200
        multi_track_station_code_map = {}

        #get all the station codes for the current line:
        line_code = line_codes[line_index]
        stations_url = base_url + stations_endpoint
        response = requests.get(stations_url, headers = headers)
        filtered_station_data = []
        if response.status_code == healthy_status:
            stations_data = response.json()
            multi_track_station_code_map = construct_multi_track_station_code_mapa(stations_data)
            for elem in stations_data['Stations']:
                if elem['LineCode1'] == line_code or elem['LineCode2'] == line_code or elem['LineCode3'] == line_code:
                    filtered_station_data.append(elem)
        else:
            print('Error in retreiving station data:', response.status_code)

        #retreive the desired station code
        station_name = filtered_station_data[station_index]["Name"]
        station_code = 'A04'
        station_dictionary = {element['Name']: element['Code'] for element in filtered_station_data}
        if station_name in station_dictionary:
            stationCode = station_dictionary[station_name]
        else:
            print("No station found: {station_name}, using default code 'A04', for Metro Center")
            
        #get arrivals data    
        arrivals_endpoint = 'StationPrediction.svc/json/GetPrediction/' + station_code
        arrivals_url = base_url + arrivals_endpoint
        response = requests.get(arrivals_url, headers=headers)

        # If success, format and print data
        if response.status_code == healthy_status:
            data = response.json()
            filtered_trains = []
            for train in data['Trains']:
                filtered_train = [train['Line'], train['Car'], train['Destination'], train['Min']]
                #filter out trains that aren't on a line, such as no passenger
                if not filtered_train[1] in line_codes:
                    filtered_trains.append(filtered_train)

            #check for station that has more than one track
            if station_code in multi_track_station_code_map.keys():
                #get the data for the second track too
                additional_arrivals_endpoint = 'StationPrediction.svc/json/GetPrediction/' + multi_track_station_code_map[station_code]
                additional_arrivals_url = base_url + additional_arrivals_endpoint
                additional_response = requests.get(additional_arrivals_url, headers=headers)
                if additional_response.status_code == 200:
                    additional_data = additional_response.json()
                    for train in additional_data['Trains']:
                        filtered_train = [train['Line'], train['Car'], train['Destination'], train['Min']]
                        if not filtered_train[1] in line_codes:
                            filtered_trains.append(filtered_train)
                    #now we have to sort the filtered trains based on arrival time
                    sort_lambda = lambda x: sort_by_arrival(x)
                    filtered_trains.sort(key = sort_lambda)
                else: 
                    print('Error in retreiving additional arrival data:', additional_response.status_code)

            # Print arrival data
            print(station_name)
            max_lengths = [max(map(len, col)) for col in zip(*filtered_trains)]
            for row in filtered_trains:
                formatted_row = ' '.join('{{:<{}}}'.format(length).format(elem) for length, elem in zip(max_lengths, row))
                print(formatted_row)
        else:
            print('Error in retreiving arrival data:', response.status_code)
    except Exception as e:
        print(f"An exception occurred: {type(e).__name__}: {e}")
    finally:
        time.sleep(10)
    pass



#two keyboard interrupts
#l: change lines: Red, Blue, Green, Orange, Yellow, Silver, Purple
#s: flick through stations in alphabetical order
#display will immediately update when new station is selected
