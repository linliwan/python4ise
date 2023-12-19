# This scripts is used to migration ISE guest accounts from 2.x to 3.x
import base64
import requests
import json
import time
from pprint import pprint

# ise credentials, host1 is the one to be exported, host2 is the one to be imported
host1 = "ise.abc.com"
host2 = "ise.abc.com"
sponsor_user = "<sponsor_name>"
sponsor_password = "<sponsor_password>"
# credential encoding
creds = str.encode(':'.join((sponsor_user, sponsor_password)), encoding='utf-8')
encoded_creds = bytes.decode(base64.b64encode(creds))
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': " ".join(("Basic", encoded_creds))
}
guest_base_url1 = f"https://{host1}:9060/ers/config/guestuser"
guest_base_url2 = f"https://{host2}:9060/ers/config/guestuser"


def get_guests(page_number):
    all_guests = []
    response = requests.request("GET", guest_base_url1 + "?size=100&page=" + str(page_number), verify=False,
                                headers=headers)
    response.raise_for_status()
    guests_list = response.json()['SearchResult']['resources']
    guest_number = response.json()['SearchResult']['total']
    for item in guests_list:
        response = requests.request("GET", guest_base_url1 + "/" + item['id'], verify=False, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        # delete customFields and link information
        response_json['GuestUser'].pop('customFields')
        response_json['GuestUser'].pop('link')
        all_guests.append(response_json)

    with open(f"guests_{page_number}.json", "w") as f:
        json.dump(all_guests, f, indent=4)
        print(f"{guest_number} of guests found, and have been added to guests_{page_number}.json")


# default page size is 100, set the page number manually to export every guest accounts.
# get_guests(1)

def create_guests(file_name, portal_id):
    with open(file_name) as f:
        guests_to_be_created = json.load(f)
        for guest in guests_to_be_created:
            # add portalID, this field is mandatory
            guest['GuestUser']['portalId'] = portal_id
            payload = json.dumps(guest)
            post_response = requests.request("POST", guest_base_url2, data=payload, verify=False, headers=headers)
            if post_response.status_code == 201:
                print(f"{guest['GuestUser']['name']} created successfully.")
            else:
                print(f"{guest['GuestUser']['name']} could not be created. Status code: {post_response.status_code}")
            time.sleep(1)


# load specific file and create guests
# create_guests("guests_1.json", "b7e7d773-7bb3-442b-a50b-42837c12248a")
