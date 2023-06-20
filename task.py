import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# suppose this must be an api call as 'https://data.nasa.gov/resource/gh4g-9sfh.json'
response = requests.get('s3://majorly-meteoric')
data = response.json()

# testing data from bucket to have all data stored correctly

records_miss_data = 0
records_deleted = 0

for record in data:
    name = record.get('name')
    record_id = record.get('id')
    name_type = record.get('nametype')
    rec_class = record.get('recclass')
    mass = record.get('mass')
    fall = record.get('fall')
    year = record.get('year')
    latitude = record.get('reclat')
    longitude = record.get('relong')
    geolocation = record.get('geolocation')

    name_validation = 'Valid'

    # test if name is not empty
    if not name.strip():
        name_validation = 'not valid'
        print(f'record: {record} has empty name')
        records_miss_data += 1
    else:
        # test if name doesn't have special characters(supposing that name should not contain it)
        special_characters = '!@#$%^&*+?_=<>/\\|'
        if any(c in special_characters for c in name):
            name_validation = 'not valid'
            print(f'record has special characters in name: {record}')
            records_miss_data += 1

    # test if id is not empty
    if not record_id.strip():
        print(f'record has empty id: {record}')
        records_miss_data += 1
    else:
        # test if id numeric
        if not record_id.isnumeric():
            print(f'record id is not numeric: {record}')
            records_miss_data += 1

    # test if nametype is not empty
    if not name_type:
        print(f'nametype is empty on record : {record}')
        records_miss_data += 1
        # test name validation
        if not name_type == name_validation:
            print(f'wrong name validation of the record : {record}')
            records_miss_data += 1

    # test if record class is not empty
    if not rec_class:
        print(f'record class is empty : {record}')
        records_miss_data += 1

    # test if mass data exists or is numeric
    try:
        mass.isnumeric()
    except AttributeError:
        print(f'record not having or wrong data for mass: {record}')
        records_miss_data += 1
        records_deleted += 1


    # not sure what to test here, will check for "Found"
    # Suppose there may be some calculation : if is not found not take it in calculations
    #    if not fall == 'Found':
    #        print(f'record meteor is not Found: {record}')
    #        data.remove(record)

    # validating coordinates
    def is_valid_latitude(lat):
        return re.match(r'^[-]?((([0-8]?[0-9])\.(\d+))|(90(\.0+)?))$', str(lat)) is not None


    def is_valid_longitude(long):
        return re.match(r'^[-]?((((1[0-7][0-9])|([0-9]?[0-9]))\.(\d+))|180(\.0+)?)$', str(long)) is not None


    test_geolocation = True
    if not is_valid_latitude(latitude) or is_valid_longitude(longitude):
        print(f'missing or wrong data for latitude or longitude: {record}')
        test_geolocation = False
        records_miss_data += 1

    # test geolocation
    if test_geolocation:
        geo_lat = geolocation.get('latitude')
        geo_lon = geolocation.get('longitude')

        if not float(geo_lat) == float(latitude) and float(geo_lon) == float(longitude):
            print(f"geolocation doesn't match with coordinates: {record}")
            records_miss_data += 1

    # if year is missing to delete the record
    # probably should test with the date format too here
    if not year:
        print(f'missing year for record: {record}')
        data.remove(record)
        records_miss_data += 1
        records_deleted += 1

print(f'records with missing/wrong data: {records_miss_data}')
print(f'records not taken in calculation: {records_deleted}')

df = pd.DataFrame(data)

df['dtyear'] = pd.to_datetime(df.year, errors='coerce')
df['mass'].fillna(0, inplace=True)
df['mass'] = pd.to_numeric(df['mass'], errors='coerce')

df

grouped = df.groupby('dtyear', as_index=False)['mass'].mean()

# Assuming we have a DataFrame named 'df' with columns 'category' and 'value'

# Create a bar plot
ax = grouped.plot(x='dtyear', y='mass', kind='bar')
ax.set_xticklabels(grouped.dtyear, rotation=90)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))  # Display ticks every 2 days
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))  # Format tick labels as 'DD-MMM'
# considering the max value as the top of y-axis
plt.ylim(0, round(grouped.mass.max()))
# if needed could use :
# plt.ylim(0,10000)
plt.yticks(fontsize=8)
plt.xticks(fontsize=8)

# Display the plot
plt.show()
