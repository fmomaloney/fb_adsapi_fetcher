# fb_adsapi_fetcher
Runs Requests against FBs ads api and returns ad account, custom audience or placement detail.
Written in Python3.

<p>prod@qacentral:~/bin$ ./gp2_main.py -h
usage: gp2_main.py [-h] [-sc] [-gc] [-p PIPELINE] [-l LOOKUP] [-m {1,2,3,4,5}]
                   [-f FBID] [-v]

This script returns results from Facebook graph calls against various objects.

optional arguments:
  -h, --help            show this help message and exit
  -sc, --show_cred      Show the FB Ad Account (cred) we are working with.
  -gc, --get_cred       Lookup credential and get access token. Please provide Pipeline for central (1,2,4,5), and a string
                        to match against the credential name. Example -gc -p5 -lqa5@nanigans
  -p PIPELINE, --pipeline PIPELINE
                        For Credential lookup (only), give us the # of the pipeline of the ad account you are interested in...
                        Valid options are 1, 2, 4, and 5
  -l LOOKUP, --lookup LOOKUP
                        For Credential lookup (only), give us a string to match against (a single) Ad Account Name.
  -m {1,2,3,4,5}, --menu {1,2,3,4,5}
                        Choose a graph call per the menu.
                        1) Show Ad Account detail and connections.
                        2) Show Ad Account spend from yesterday from reportstats.
                        3) Show FB placement details for -f=FB_ID.
                        4) Show FB spend stats for -f=FB_ID.
                        5) Campaign-Adset-Placement Status for -f=FB_ID!
  -f FBID, --fbid FBID  Pass in the FB ID for graph calls requesting placement level data.
  -v, --verbose         Show all fields FB provides.<p>

