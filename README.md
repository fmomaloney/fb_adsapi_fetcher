# fb_adsapi_fetcher
It is tedious to run graph calls against the FB api, as it requires copying and pasting access_tokens and looking up endpoints in FB doc. This script runs graph Requests against the ads api and returns ad account, custom audience or ad  placement details, after looking up access token. Helpful in validation of placements. Written in Python3.

<pre>
prod@qacentral:~/bin$ ./gp2_main.py -h
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
  -v, --verbose         Show all fields FB provides.
  
fmaloney ~/PycharmProjects/gp-cli: ./gp2_main.py -sc
The working config is for pipeline 2, name = qa6_eur@nanigans.com, cred = 675, account = 124113917717380, last synced = 2015-08-31 10:06, and...
token = CAABjmNKT_an_access_token

fmaloney ~/PycharmProjects/gp-cli: ./gp2_main.py -m5 -f6033066118888
Adset: budget_remaining is 1000.
Adset: campaign_group_id is 6033066079288.
Adset: campaign_status is DELETED.
Adset: created_time is 2015-07-13T04:23:59+0100.
Adset: daily_budget is 1000.
Adset: id is 6033066080288.
Adset: is_autobid is False.
Adset: name is no_spend_112_[P].
Campaign: campaign_group_status is DELETED.
Campaign: id is 6033066079288.
Campaign: name is no_spend_112_2.
Campaign: objective is WEBSITE_CLICKS.
Placement: account_id is 124113917717380.
Placement: adgroup_status is DELETED.
Placement: bid_info is {'IMPRESSIONS': 15}.
Placement: bid_type is CPM.
Placement: campaign_id is 6033066080288.
Placement: created_time is 2015-07-13T04:26:55+0100.
Placement: id is 6033066118888.
Placement: name is Ad_10740520.
<pre>
