"""
------------------------------------------------------------------------
Script to call Hyundai API and construct accessory files
------------------------------------------------------------------------
Author: Dylan Doyle
Updated: 2021-08-08
------------------------------------------------------------------------
Notes:

------------------------------------------------------------------------
"""

import requests
import json
import pandas as pd
import os
import urllib.request
import sys
import traceback
import shutil
import glob
from slack_sdk import WebClient
import config

try:
    sys.path.insert(1, os.path.join('..', 'SlackBot'))
    from SlackBot import *
except ImportError as e :
    print('Cannot import SlackBot. Either it is not installed or the path "../SlackBot/" does not point to it.')
    print(e)
    exit(0)

SLACK_BOT_TOKEN = 'xoxb-4950217216-1580739024241-KE4CsYwOouHLxmpuEmk8BYJ4'
# Create instance of slackbot
curr_dir = os.getcwd()
client = WebClient(token=SLACK_BOT_TOKEN)

regions = {

    'AB': '1',
    'BC': '2',
    'MB': '3',
    'NB': '4',
    'NL': '5',
    'NS': '6',
    'ON': '7',
    'PE': '8',
    'QC': '9',
    'SK': '10'
}


model_url = "https://sapps.hac.ca/Api/models/en/{region}"
vehicles = []
payload = {}
headers = {}

class Vehicle:
    """
    -------------------------------------------------------
    Creates the current month directory if one does not
    already exist.
    -------------------------------------------------------
    Attributes:
        model_id: int
            Unique model identifier
        year: int
            Model year
        make: str
            Make of vehicle
        model: str
            Model name
        region_code: str
            Code for respective region
        trim_ids: list(int)
            List of unique trim identifiers
        trim_names: list(str)
            List of trim names
        accessories: list(str)
            List of all applicable accesories and respective information
    ------------------------------------------------------
    """

    trim_url = "https://apps.hac.ca/Api/trims/en/{region}/{model}"
    acc_url = 'https://apps.hac.ca/API/Accessories/EN/{region}/{model}/{trim}'
    acc_url_fr = 'https://apps.hac.ca/API/Accessories/FR/{region}/{model}/{trim}'
    payload={}
    headers = {}


    def __init__(self, model_id, year, make, model, region_code):
        self.model_id = model_id
        self.year = year
        self.make = make
        self.model = model
        self.region_code = region_code
        self.get_trims()
        self.get_accessories()
        self.rename_models()


    def create_model(response, region_code):
        """
        -------------------------------------------------------
        Function will call class constructor and create a class
        instance for each vehicle and region. Pass response from
        Hyundai API "GET ALL MODELS" call and list of region codes.
        -------------------------------------------------------
        Args:
            response - Hyundai API response containing ID and names of all available models
            region_code - Respective region code

        Returns:
            Calls class constructor and creates an instance using passed variables
        -------------------------------------------------------
        """
        model_id = response['ModelId']
        year = response['ModelYear']
        make = 'Hyundai'
        model = response['ModelName']
        return Vehicle(model_id, year, make, model, region_code)


    def get_trims(self):
        """
        -------------------------------------------------------
        Calls API trim endpoint using respective vehicle information
        to retrieve list of available trim names and IDs
        -------------------------------------------------------
        """
        url = self.trim_url.format(region=self.region_code, model=self.model_id)
        response2 = requests.request("GET", url, headers=self.headers, data=self.payload)

        if response2.status_code != 200:
            self.trim_ids = ('NO RESPONSE FROM API')
            self.trim_names = ('NO RESPONSE FROM API')
        else:
            response2 = response2.json()
            response2 = response2['Models']['Model']['Trims']['Trim']
            self.trim_ids = ([y['TrimId'] for y in response2])
            self.trim_names = ([y['TrimName'] for y in response2])


    def get_accessories(self):
        """
        -------------------------------------------------------
        Calls API accessory endpoint to retrieve list of available
         accessories
        -------------------------------------------------------
        """
        acc_list = []
        acc_list_fr = []

        # Iterate through trim attributes, mapping each name to its id
        for trim_id, trim_name in zip(self.trim_ids, self.trim_names):

            # Call english trim endpoint
            url = self.acc_url.format(region=self.region_code, model=self.model_id, trim=trim_id)
            response3 = requests.request("GET", url, headers=headers, data=payload)
            if response3.status_code != 200:
                self.accessories = 'ERROR'
                continue
            response3 = response3.json()

            # call french trim endpoint
            url = self.acc_url_fr.format(region=self.region_code, model=self.model_id, trim=trim_id)
            response_fr = requests.request("GET", url, headers=headers, data=payload)
            if response_fr.status_code != 200:
                self.accessories = 'ERROR'
                continue
            response_fr = response_fr.json()

            # Iterate through JSON response to extract accessory info
            for groups in response3['AccessoryGroups']['AccessoryGroup']:
                for accessory in groups['Accessorries']['Accessory']:
                    found = False
                    while found is False:
                        for groups_fr in response_fr['AccessoryGroups']['AccessoryGroup']:
                            for accessory_fr in groups_fr['Accessorries']['Accessory']:
                                if accessory_fr['AcessoryPartNumber'] == accessory['AcessoryPartNumber']:
                                    acc_name_fr = accessory_fr['AccessoryName']
                                    acc_desc_fr = accessory_fr['AccessoryDescription']
                                    found = True

                    # Create blank list of all accessories and create a list of sublists, with each sublist containing all the respective accessory information
                    acc = []
                    acc.extend((accessory['AccessoryName'], accessory['AccessoryDescription'], acc_name_fr, acc_desc_fr, accessory['AcessoryPartNumber'], accessory['MSRP'], accessory['AccessoryImagePath'].replace('sccms.', '')))
                    acc_list.append(acc)
            self.accessories = acc_list


    def rename_models(self):
        pass
        # """
        # -------------------------------------------------------
        # Iterates through dict to replace models names with system
        # compatible names
        # -------------------------------------------------------
        # """
        #
        # model_dict_2021 = {
        # 'Veloster N': 'Veloster',
        # 'Elantra': 'Elantra Sedan',
        # 'Elantra Hybrid': 'Elantra Sedan',
        # 'IONIQ plug-in hybrid': 'IONIQ Plug-In Hybrid',
        # 'IONIQ Plug-in hybrid': 'IONIQ Plug-In Hybrid',
        # 'IONIQ Plug-in Hybrid': 'IONIQ Plug-In Hybrid',
        # 'Kona Electric': 'Kona electric',
        # 'Sonata N Line': 'Sonata'
        # }
        #
        # model_dict_2022 = {
        # 'IONIQ plug-in hybrid': 'IONIQ Plug-In Hybrid',
        # 'IONIQ Plug-in hybrid': 'IONIQ Plug-In Hybrid',
        # 'IONIQ Plug-in Hybrid': 'IONIQ Plug-In Hybrid',
        # 'Kona Electric': 'Kona electric',
        # }
        #
        # if self.model in model_dict_2022.keys() and self.year = '2022':
        #     self.model = model_dict_2022[self.model]
        #
        # if self.model in model_dict_2021.keys() and self.year = '2021':
        #     self.model = model_dict_2021[self.model]


def __create_df(vehicles, region_name):
    """
    -------------------------------------------------------
    Helper function to format DataFrame
    -------------------------------------------------------
    """
    entry_list = []
    for vehicle in vehicles:
        year = vehicle.year
        make = vehicle.make
        model = vehicle.model
        trims = vehicle.trim_names
        accessories = vehicle.accessories


        if accessories == 'ERROR':
            continue

        name_list, desc_list, fr_name_list, fr_desc_list, part_number_list, price_list, image_path_list = zip(*accessories)
        for name, desc, name_fr, desc_fr, part_number, price, image_path in zip(name_list, desc_list, fr_name_list, fr_desc_list, part_number_list, price_list, image_path_list):
            # TRIMS ARE ERASED HERE
            trim = ''

            entry = [name, desc, name_fr, desc_fr, part_number, price, year, make, model, trim, image_path]
            entry_list.append(entry)

    df = pd.DataFrame(entry_list, columns=['Accessory', 'Description', 'Accessory FR', 'Description FR', 'Part Number', 'Price', 'Year', 'Make', 'Model', 'Trim', 'Image Path'])
    df['Category'] = ''
    df = df.drop_duplicates()
    return df, region_name


def create_model_requests(model_url, vehicles):
    """
    -------------------------------------------------------
    Handler that creates complete list of all available vehicles
    and respective information using Vehicle class method
    -------------------------------------------------------
    Args:
        model_url: str
            API endpoint to retrieve list of available models
        vehicles: list
            Empty list to hold Vehicle class objects


    Return:
        final_sku_list: list
            Complete list of all SKUs
    ------------------------------------------------------
    """

    final_sku_list = []

    # Iterate through all available regions
    for region_name, region_code in regions.items():
        print(f'Region {region_name}...')
        url = model_url.format(region=region_code)

        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        i = 0
        for model_group in response['ModelGroups']['ModelGroup']:

            for model in model_group['Models']['Model']:
                print(f"Creating vehicle {i+1} ---> {model['ModelName']} {model['ModelYear']}")
                vehicles.append(Vehicle.create_model(model, region_code))
                i += 1

        df, region_name = __create_df(vehicles, region_name)
        sku_list = create_upload(df, region_name)
        final_sku_list.extend(sku_list)

        print()


    return final_sku_list


def create_upload(df, region):
    """
    -------------------------------------------------------
    Formats DataFrame into a format that can be imported into
    motocommerce platform (vehicles per Accessory as opposed
    accessories per vehicle)
    -------------------------------------------------------
    Args:
        df: DataFrame
            Constructued information retrieved from API
        region: str
            Region variable

    Return:
        sku_list: list
            List of SKUs included in respective region

    ------------------------------------------------------
    """
    print()
    print('Processing into uploadable file...')
    df_unique = df.drop(columns=['Year', 'Make', 'Model', 'Trim'])
    df_unique = df_unique.drop_duplicates()
    df_unique['Models'] = ''

    # Consolidate all repeat accessories to create a list of available, formatted model names
    for index_unique, row_unique in df_unique.iterrows():
        model_list = []
        part_number = row_unique['Part Number']
        for index, row in df.iterrows():

            if part_number == row['Part Number']:

                if type(row['Trim']) == str and len(row['Trim']) != 0:
                    model_list.append('[All ' + str(row['Year']) + " " + row['Make'] + " " + row['Model'] + " " + row['Trim'] + "]")
                else:
                    model_list.append('[All ' + str(row['Year']) + " " + row['Make'] + " " + row['Model'] + "]")

        df_unique.loc[index_unique, 'Models'] = ", ".join(x for x in model_list)
        df_unique.loc[index_unique, 'Image Path'] = f'moto_dealer/accessory_images/Hyundai/CTB_Images/{part_number}.jpg'
    sku_list = df_unique['Part Number'].tolist()
    df_unique.columns = ['accessory', 'desc', 'french name', 'french desc', 'sku', 'price', 'pic path', 'category', 'model']
    df_unique['origin'] = 'OEM'
    df_unique['disclaimer'] = ''
    df_unique['disclaimer fr'] = ''
    df_unique = __set_category(df_unique)
    title = f'PROCESSED - {region}.csv'
    path = os.path.join('Complete', title)
    df_unique.to_csv(path, index=None)

    return sku_list


def __set_category(df):
    """
    -------------------------------------------------------
    Helper function to fill in category fields from preset list
    -------------------------------------------------------
    """
    int_list = ['Floor', 'Liner', 'Mat', 'Cargo', 'Seat', 'Pedal', 'Interior', 'Cup']
    print('Formatting categories...')
    for index, row in df.iterrows():
        interior = False
        for item in int_list:
            if item in row['accessory']:
                interior = True
                break
        if interior is True:
            df.loc[index, 'category'] = 'Interior'
        else:
            df.loc[index, 'category'] = 'Exterior'
    return df


def download_images(sku_list):
    """
    -------------------------------------------------------
    Downloads list of all unique images
    -------------------------------------------------------
    Args:
        sku_list: list
            List of unique SKUs to download images of
    ------------------------------------------------------
    """
    print('Downloading images...')

    # Avoid re-downloading images that are already available
    existing_pics = [pic.strip('.jpg').strip('Images/') for pic in glob.glob('Images/*.jpg')]
    for index, sku in enumerate(set(sku_list)):
        if sku in existing_pics:
            continue
        image_link = f'https://www.hyundaicanada.com/-/media/Hyundai/feature/accessories/responsiveimage/{sku}.JPG'
        image_path = os.path.join('.', 'Images', f'{sku}.jpg')
        urllib.request.urlretrieve(image_link, image_path)


def markups():
    """
    -------------------------------------------------------
    Creates individual accessory files for dealerships with
    marked up priced
    -------------------------------------------------------
    """
    df_markup = pd.read_csv('markups.csv')
    for index1, row1 in df_markup.iterrows():
        name = row1['name']
        region = row1['region']
        markup = float(row1['markup'])
        df_region = pd.read_csv(os.path.join('Complete', f'PROCESSED - {region}.csv'))
        if markup == '16.95':
            df_region['price'] = round(df_region['price'].apply(lambda x: float(x)+float(16.95)), 2)
        else:
            df_region['price'] = round(df_region['price'].apply(lambda x: float(x)*markup), 2)
        title = f'MARKED UP - {name}.csv'
        path = os.path.join('Markup', title)
        df_region.to_csv(path, index=None)

    return

def remove_images():
    filelist = [f for f in os.listdir('Images')]
    for f in filelist:
        os.remove(os.path.join('Images', f))

def main():
    channels = ['ctb-accessory-generation']
    # Post start message to slack
    data = json.dumps(json.loads(config.start_message)['blocks'])
    response = client.chat_postMessage(channel='ctb-accessory-generation', blocks=data)

    try:
        sku_list = create_model_requests(model_url, vehicles)
        markups()
        download_images(sku_list)

        # compress folders
        shutil.make_archive('Complete', 'zip', 'Complete')
        shutil.make_archive('Markup', 'zip', 'Markup')
        shutil.make_archive('Images', 'zip', 'Images')

        data = json.dumps(json.loads(config.exit_message)['blocks'])
        response = client.chat_postMessage(channel='ctb-accessory-generation', blocks=data)
        slack_send_file(channels, ['Complete.zip', 'Markup.zip', 'Images.zip'], ['Accessory Files', 'Markup Files', 'Accessory Images'])
        remove_images()
    except:
        # Report error to slack channel
        messages = [f'AN ERROR HAS OCCURED:\n {traceback.format_exc()}']
        traceback.print_exc()
        slack_send_message(channels, messages)



if __name__ == '__main__':
    main()
