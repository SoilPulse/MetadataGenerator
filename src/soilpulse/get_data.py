# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:35:03 2023

@author: Jonas Lenz
"""

#from io import BytesIO
import requests
#from zipfile import ZipFile
#from urllib.request import urlopen
import get_metadata as gm

#def load_data(url):
#    f = urlopen(url)

#    with ZipFile(BytesIO(f.read())) as my_zip_file:
#        for contained_file in my_zip_file.namelist():
#            st.write(contained_file)
#            if (contained_file.endswith("README.md")):
            # with open(("unzipped_and_read_" + contained_file + ".file"), "wb") as output:
#                st.header("accesing README")
#                for line in my_zip_file.open(contained_file).readlines():
#                    st.write(line)
                    
                    
def doi_data(doi):
    meta_ra = gm.doi_meta(doi)
    dataset_url = meta_ra['data']['attributes']['url']
    if ("zenodo.org" in dataset_url):
        zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
        print("retrieving information for Zenodo dataset: "+zenodo_id)
        
        response = requests.get("https://zenodo.org/api/deposit/depositions/"+zenodo_id+"/files").json()
        if (type(response) == dict):
            print("Data set can not be retrieved.")
        else:
            for file in response:
                if (".zip" in file['filename']):
                    print(file['filename'])
                print("Download-url: https://zenodo.org/records/"+zenodo_id+"/files/"+file['filename']+"?download=1")

