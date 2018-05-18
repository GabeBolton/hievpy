# coding: utf-8
import os
import urllib.request
import urllib.parse
import json
import pandas as pd
import requests
import io
import tqdm
from hievpy.utils import *


# def is_toa5(record):
#     """ Utility function to check if a supplied record (as generated by hievpy.search) is in TOA5 format
#
#     Input
#     -----
#     Required
#     - record: record object returned by the search function
#
#     Returns
#     -------
#     True or False
#
#     """
#
#     if record['format'] == 'TOA5' and record['file_processing_status'] == 'RAW':
#         return True
#
#     return False


def search(api_token, base_url='https://hiev.westernsydney.edu.au/', **kwargs):
    """ Returns a list of HIEv records (or their IDs) matching a set of input search parameters.

    (see https://github.com/IntersectAustralia/dc21-doc/blob/2.3/Search_API.md)

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - base_url - Base URL of the HIEv/Diver instance

    Optional keyword arguments
    - from_date - This is "Date->From Date" in search box of WEB UI: "from_date"=>"2013-01-01"
    - to_date - This is "Date->To Date" in search box of WEB UI: "to_date"=>"2013-01-02"
    - filename - This is "Filename" in search box of WEB UI: "filename"=>"test"
    - description - This is "Description" in search box of WEB UI: "description"=>"test"
    - file_id - This is "File ID" in search box of WEB UI: "file_id"=>"test"
    - id (here replaced as record_id)- This is "ID" in search box of WEB UI: "id"=>"26"
    - stati - This is "Type" in search box of WEB UI: "stati"=>["RAW", "CLEANSED"]
    - automation_stati - This is "Automation Status" in search box of WEB UI, "automation_stati"=>["COMPLETE",
      "WORKING"]
    - access_rights_types - This is the "Access Rights Type" in the search box of the WEB UI: "access_rights_types"=>
      ["Open", "Conditional", "Restricted"]
    - file_formats - This is "File Formats" in search box of WEB UI, "file_formats"=>["TOA5", "Unknown", "audio/mpeg"]
    - published - This is "Type->PACKAGE->Published" in search box of WEB UI: "stati"=>["PACKAGE"], "published"=>
      ["true"]
    - unpublished - This is "Type->PACKAGE->Published" in search box of WEB UI: "stati"=>["PACKAGE"], "unpublished"=>
      ["true"].
    - published_date - This is "Type->PACKAGE->Published Date" in search box of WEB UI: "stati"=>["PACKAGE"],
      "published_date"=>"2013-01-01"
    - tags - This is "Tags" in search box of WEB UI: "tags"=>["4", "5"]
    - labels - This is "Labels" in search box of WEB UI, "labels"=>["label_name_1", "label_name_2"]
    - grant_numbers - This is the "Grant Numbers" in search box of WEB UI, "grant_numbers"=>["grant_number_1",
      "grant_number_2"]
    - related_websites - This is the "Related Websites" in the search box of WEB UI, "related_websites"=>
      ["http://www.intersect.org.au"]
    - facilities - This is "Facility" in search box of WEB UI, ask system administrator to get facility ids :
      "facilities"=>["27"]
    - experiments - This is "Facility" in search box of WEB UI, when one facility is clicked, experiments of this
      facility are selectable, ask system administrator to get experiment ids: "experiments"=>["58", "54"]
    - variables - This is "Columns" in search box of WEB UI, when one group is clicked, columns of this group are
      selectable: "variables"=>["SoilTempProbe_Avg(1)", "SoilTempProbe_Avg(3)"]
    - uploader_id - This is "Added By" in search box of WEB UI, ask system administrator to get uploader ids:
      "uploader_id"=>"83"
    - upload_from_date - This is "Date Added->From Date" in search box of WEB UI, "upload_from_date"=>"2013-01-01"
    - upload_to_date - This is "Date Added->To Date" in search box of WEB UI, "upload_to_date"=>"2013-01-02"

    Returns
    -------
    List of matching hiev search results (with file download url included)

    Example
    -------
    my_files = hievpy.search('MY_API_TOKEN', experiments=['90'], from_date="2016-02-12")

    """

    request_url = base_url + 'data_files/api_search'

    request_data = kwargs
    # Add Auth/API token to request_data
    request_data['auth_token'] = api_token

    # -- Set up the http request and handle the returned response
    data = urllib.parse.urlencode(request_data, True)
    data = data.encode('ascii')
    req = urllib.request.Request(request_url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()

    encoding = response.info().get_content_charset('utf-8')
    results = json.loads(the_page.decode(encoding))

    return results


def download(api_token, record, path=None):
    """ Downloads a file from HIEv to local computer given the file record (as returned by search)

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - record: record object returned by the search function

    Optional
    - path: Full path of download directory (if path not provided, file will be downloaded to current directory)
    """

    download_url = record['url'] + '?' + 'auth_token=%s' % api_token

    if path:
        download_path = os.path.join(path, record['filename'])
        urllib.request.urlretrieve(download_url, download_path)
    else:
        urllib.request.urlretrieve(download_url, record['filename'])


def search_download(api_token, base_url='https://hiev.westernsydney.edu.au/', path=None, **kwargs):
    """ Downloads a file from HIEv to local computer given the file record (as returned by search)

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - record: record object returned by the search function

    Optional
    - path: Full path of download directory (if path not provided, file will be downloaded to current directory)
    - See hievpy.search function for full list of optional search keyword arguments
    """

    results = search(api_token, base_url='https://hiev.westernsydney.edu.au/', **kwargs)

    for result in tqdm.tqdm(results):
        download_url = result['url'] + '?' + 'auth_token=%s' % api_token

        if path:
            download_path = os.path.join(path, result['filename'])
            if not os.path.isfile(download_path):
                urllib.request.urlretrieve(download_url, download_path)
        else:
            if not os.path.isfile(result['filename']):
                urllib.request.urlretrieve(download_url, result['filename'])


def toa5_summary(api_token, record):
    """ Returns variable information (daterange of data, and all variable names, units and measurement types) from a
    HIEv TOA5 file given the file record (returned by search function).

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - record: record object returned by the search function

    Returns
    -------
    TOA5 summary information printed to the console
    """

    if is_toa5(record):
        download_url = record['url'] + '?' + 'auth_token=%s' % api_token
        url_data = requests.get(download_url).content
        # TODO Check that file is actually a TOA5 file before proceeding....
        df = pd.read_csv(io.StringIO(url_data.decode('utf-8')), skiprows=1, header=None)
        for column in df:
            print("  ".join(str(x) for x in df[column][0:3].values))
    else:
        print('Error: This is not a TOA5 record')


def toa5_to_df(api_token, record):
    """ Loads a TOA5 file from HIEv into a pandas dataframe given the file record (returned by search function).

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - record: record object returned by the search function

    Returns
    -------
    Pandas dataframe of TOA5 data with index equal to TIMESTAMP and TOA5 variable names as column header

    Notice:
    The top row of the original TOA5 file (logger info etc) and the units and measurement type rows are discarded
    during dataframe creation. Thus information can alternatively be found via the toa5_summary function.
    """

    if is_toa5(record):
        download_url = record['url'] + '?' + 'auth_token=%s' % api_token
        url_data = requests.get(download_url).content
        df = pd.read_csv(io.StringIO(url_data.decode('utf-8')), skiprows=1)

        # Disregard the units + measurement type rows (whose info can alternatively returned via the toa5_info function)
        df = df.iloc[2:, :]
        df = df.set_index('TIMESTAMP')
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)

        return df
    else:
        print('Error: This is not a TOA5 record')


def search_load_toa5df(api_token, base_url = 'https://hiev.westernsydney.edu.au/', path=None, **kwargs):
    """ Search 0Loads a file from HIEv to local computer given the file record (as returned by search)

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - record: record object returned by the search function

    Optional
    - path: Full path of download directory (if path not provided, file will be downloaded to current directory)
    """

    results = search(api_token, base_url='https://hiev.westernsydney.edu.au/', **kwargs)

    data = pd.DataFrame()

    for result in tqdm.tqdm(results):
        download_url = result['url'] + '?' + 'auth_token=%s' % api_token
        url_data = requests.get(download_url).content
        df = pd.read_csv(io.StringIO(url_data.decode('utf-8')), skiprows=1,
                         na_values='NAN')

        # Disregard the units and measurement type rows (whose info can alternatively returned via the toa5_info function)
        df = df.iloc[2:, :]
        df = df.set_index('TIMESTAMP')
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)
        data = pd.concat([data, df])

    if kwargs['from_date']:
        data = data[kwargs['from_date']:].sort_index()

    if kwargs['to_date']:
        data = data[:kwargs['to_date']].sort_index()

    return data


def plot_toa5df_var(df, variable):
    """ Simple line plot of a timeseries variable within a TOA5 file
    """
    if variable not in df:
        print('Error: "{0}" does not exist within this TOA5 file'.format(variable))
    else:
        df[variable].plot(style='-', color='b', title=variable)


def upload(api_token, upload_file, metadata, base_url = 'https://hiev.uws.edu.au/'):
    """

    """

    upload_url = base_url + 'data_files/api_create' + '?' + 'auth_token=%s' % api_token
    files = {'file': open(upload_file)}
    response = requests.post(upload_url, files=files, data=metadata)

    # Print the outcome of the upload
    if response.status_code == 200:
        print('File successfully uploaded to HIEv')
    else:
        print('ERROR - There was a problem uploading the file to HIEv')
