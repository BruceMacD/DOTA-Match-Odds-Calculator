import json
import urllib
import ijson

# A tool for getting DOTA2 match details from Steam

#TODO: ADD YOUR STEAM API KEY HERE
steamapi_key = 'XXXXXX'
# match ids retrieved from OpenDOTA
pro_match_id_json_file = 'match-ids.json'
# file to write data from Steam
match_data_json_file = 'match-details.json'

# Move match ids into list
with open(pro_match_id_json_file, 'r') as f:
    objects = ijson.items(f, 'rows')
    all_match_ids = list(objects)[0];

# Valve server dota 2 API endpoint
request_url = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?key=" + steamapi_key + "&match_id="

match = 0

print('reading match data... \n')

with open(match_data_json_file, 'w') as out:
    out.write('{\n')
    out.write('"all_matches":[\n')

    for row in all_match_ids:

        match += 1

        try:
            if match > 1:
                # do not write a comma at the start of the file
                out.write(',\n')
            # match = next in file
            match_id = str(row['match_id'])
            # append to request url
            url = request_url + match_id
            response = urllib.urlopen(url)
            objects = ijson.items(response, 'result')
            result = list(objects)
            # dump result to output file
            json.dump(result[0], out)
            print('processed request #' + str(match) + ': ' + match_id)
        except:
            print(str(match) + ') ERROR retrieving ' + match_id)
    # done reading, close json
    out.write(']\n')
    out.write('}\n')