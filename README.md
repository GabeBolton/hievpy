# HIEvPy
HIEvPy is a python package for interfacing with the [HIEv](https://hiev.westernsydney.edu.au), a data capture application used by the [Hawkesbury Institute for the Environment](https://www.westernsydney.edu.au/hie) at Western Sydney University. HIEvPy provides programmatic shortcuts for the following operations in HIEv:
- Search
- Download


**To use HIEVPY you must have an account on HIEv.**
### Installation
Pre-requisites required on local machine
- Python (python2.7)
- Pip
- Git

You can install HIEvPy directly from the main GitHub repository using:
```sh
$ pip install --user git+git://github.com/gdevine/hievpy.git
```
where the "--user" flag is for a local user install. 
The 'sudo' command should only be used if you are installing HIEvPy system-wide (with admin priviledges):
```sh
$ sudo pip install git+git://github.com/gdevine/hievpy.git
```

Once HIEvPy has been installed, you can import it into a python console or script using:
```sh
from hievpy import hievpy
```


### Instructions

*Docstrings, outlining the full functionality, have been provided against all primary functions and can be accessed using help(function), for example*
```sh
help(hievpy.search_hiev)
```


All commands available via HIEvPy will require passing in your HIEv API key. Please consider keeping your API key outside of your actual
code (particularly if you intend on sharing code). Instead, store your API key in a separate file or in a local environment variable.


#### Search
To search against the HIEv database, you can use
```sh
hievpy.search(api_key, <optional args>)
```

Use the help function on *hievpy.search* to see a full list of optional search arguments.

**It is highly recommended that you supply at least one search query to your search to limit returning the full database in one call**

As an example, to search for all records with data for February 2017 from the DriGrass facility and save to a variable called *dgFiles* use:
```sh
dgFiles = hievpy.search(MY_API_KEY, from_date="2017-02-01", to_date="2017-02-28", facilities = ['14'])
```


#### Download
The HIEvPy.download function can be used in conjunction with the search function to download a file from HIEv (with option to specify download location)  
```sh
hievpy.download(api_key, search_record, <optional path>)
```

Use the help function on *hievpy.search* to see a full list of optional search arguments.

As an example, the following code is used to search for all files with data for Feb 15th 2017 from the DriGrass facility and to download the results to a directory called DG_DATA (directory must exist) 
```sh
dg_files = hievpy.search(MY_API_KEY, from_date="2017-02-15", to_date="2017-02-15", facilities = ['14'])
for dg_file in dg_files:
    hievpy.download(MY_API_KEY, dg_file, path='/Users/MY_USERNAME/')
```


