# Hyundai_Accessories_ETL

This script is used to call the Hyundai API and construct accessory files for use on the motocommerce platform. The API provides information on Hyundai vehicle models, trims, and accessories available in different regions of Canada.

## Requirements
The following packages are required to run the script:

requests
pandas
slack_sdk
config
urllib
sys
traceback
shutil
glob

## Usage
The script can be run in any Python environment that has the required packages installed. The user must provide a valid Slack API token in the SLACK_BOT_TOKEN variable.

To run the script, simply execute the following command:

`python hyundai_accessory_script.py`

The script will then call the Hyundai API and generate accessory files in the Complete folder. The Markup folder will contain accessory files with marked-up prices. The Images folder will contain all the images downloaded from the API.

The script will also compress the Complete, Markup, and Images folders into zip files and upload them to the specified Slack channel.
