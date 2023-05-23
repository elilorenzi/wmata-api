import requests

api_key = 'b18ceda221c645d5bd1d5386f40ca0e1'
base_url = 'https://api.wmata.com/'
headers = {
    'api_key': api_key,
}
stationsEndpoint = "/Rail.svc/json/jStations/"

#get all the station codes:
stationsUrl = base_url + stationsEndpoint
response = requests.get(stationsUrl, headers=headers)
if response.status_code == 200:
    stationsData = response.json()
    for elem in stationsData['Stations']:
        print(elem['Name'] + ": " + elem['Code'])
else: 
    print('Error in retreiving station data:', response.status_code)

#retreive the desired station code
stationName = 'Metro Center'
stationCode = 'A04'
#append, don't overwrite. then it can't be a dictionary
stationDictionary = {element['Name']: element['Code'] for element in stationsData['Stations']}
#print(stationDictionary)
if stationName in stationDictionary:
    stationCode = stationDictionary[stationName]
else:
    print("No station found: {stationName}, using default code 'A04'")
    
#get arrivals data    
arrivalsEndpoint = 'StationPrediction.svc/json/GetPrediction/' + stationCode
arrivalsUrl = base_url + arrivalsEndpoint
response = requests.get(arrivalsUrl, headers=headers)

# If success, format and print data
if response.status_code == 200:
    data = response.json()
    # Print arrival data
    filteredTrains = []
    for train in data['Trains']:
        filteredTrain = [train['Line'], train['Car'], train['Destination'], train['Min']]
        filteredTrains.append(filteredTrain)
    max_lengths = [max(map(len, col)) for col in zip(*filteredTrains)]
    print(stationName)
    for row in filteredTrains:
        formatted_row = ' '.join('{{:<{}}}'.format(length).format(elem) for length, elem in zip(max_lengths, row))
        print(formatted_row)
else:
    print('Error in retreiving arrival data:', response.status_code)


#make this an ongoing thread that updates at .1 hz
#two keyboard interrupts
#l: change lines: Red, Blue, Green, Orange, Yellow, Silver, Purple
#s: flick through stations in alphabetical order
#display will immediately update when new station is selected
#errors will be handled and displayed
#depending on hardware we will need to serialize the output to be put on wire.
#merge all the trains at all stations. MC, LEF, GP, FT
