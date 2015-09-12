#!/usr/local/bin/python3.4

__author__ = 'fmaloney'

import json, logging, argparse, configparser, datetime, sys
import requests, pymysql

def main():
    '''
    GP-CLI. This script makes graph calls to FB opengraph adsapi and presents results in a form useful to Nanigans.
    Using 'requests' for HTTP. All graph calls should be gets. Initially doing subset of graph calls for placement,
    intend to expand for more graph options. Add some compund calls, which are useful to us.
    this is a test
    '''

    # Read the current account_id and token from config.ini for --show-cred
    config = configparser.ConfigParser()
    config.read('config.ini')
    mypipeline = config['DATABASE']['pipeline']
    myid = config['DATABASE']['id']
    myaccountid = config['DATABASE']['account_id']
    mytoken = config['DATABASE']['access_token']
    myltd = config['DATABASE']['last_touch']
    myname = config['DATABASE']['account_name']
    # Set up logging
    logging.basicConfig(filename ='graphfetch.log', format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)
    # Get CLI arguments
    args = get_args()
    fieldlist =[args.show_cred,args.get_cred,args.verbose,args.menu,args.fbid,args.pipeline,args.lookup]

    # This is the logic per the args
    if (args.show_cred):
        # Show Cred: get it from config and print it.
        print("The working config is for pipeline {}, name = {}, cred = {}, account = {}, last synced = {}, and...\ntoken = {}"
              .format(mypipeline, myname, myid, myaccountid, myltd, mytoken))
    elif (args.get_cred):
        # Get Cred: do the SQL query against our central hosts and lookup cred info
        allowed_pipelines = [1,2,3,4,5]
        if (args.pipeline in allowed_pipelines) and args.lookup:
            newcred = dosql(args.pipeline,args.lookup)
            if newcred is not None:
                #print("{} and {} and \n{}".format(newcred["account_id"],newcred["updated"],newcred["config"]))
                newaccount = newcred["account_id"]
                newid = newcred["id"]
                newupdate = newcred["updated"]
                newtime = datetime.datetime.fromtimestamp(int(newupdate)).strftime('%Y-%m-%d %H:%M')
                # pull some data out of the config JSON
                configdict = json.loads(newcred["config"])
                newtoken = configdict["auth_token"]
                newname = configdict["account_name"]
                print("Congratulations, you have matched cred {} on pipeline {}. Use -sc to view details"
                      .format(newname,args.pipeline))
                # Now write this stuff to the config file (overwrite previous)
                config['DATABASE']['pipeline'] = str(args.pipeline)
                config['DATABASE']['account_id'] = newaccount
                config['DATABASE']['id'] = str(newid)
                config['DATABASE']['last_touch'] = newtime
                config['DATABASE']['access_token'] = newtoken
                config['DATABASE']['account_name'] = newname
                logging.info("New working credential %s account ID %s.",newname,newaccount)
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
            else:
                # Did not match a cred. Message user and exit.
                print("Your string {} did not match a cred name on pipeline {}. Try again?".format(args.lookup,args.pipeline))
                sys.exit(0)
        else:
            # Invalid options for -gc
            print("You need to specify the correct pipeline and a string to match with cred name.")
            sys.exit(0)

    # The menu options go here
    elif (args.menu)==1:
        # This is the account lookup
        myurl,mypayload = account_connections(myaccountid,mytoken,args.verbose)
    elif (args.menu)==2:
        # This is the account reportstats for yesterday (hardcoded)
        myurl,mypayload = account_spend_yesterday(myaccountid,mytoken)
    elif (args.menu)==3:
        # Placement level graph info retrieved here
        myurl,mypayload = placement_detail(mytoken,args.fbid,args.verbose)
    elif args.menu == 4:
        # Placement stats retrieved here. Verbose not recognized.
        myurl,mypayload = placement_stats(mytoken,args.fbid,args.verbose)
    elif args.menu == 5:
        # Compound query on Adgroup, Adset, Campaign status. NOTE - we are exiting from this function!
        struct_status(mytoken,args.fbid)
    elif args.menu == 6:
        # custom audience detail
        myurl,mypayload = custom_audience(mytoken,args.fbid)
    elif args.menu == 7:
        # compound query on adgroup, creative, and page/post (if applicable). Also exiting from this function.
        myurl,mypayload = creative_post(mytoken,args.fbid)
    else:
        # should not get here
        print("hello from option ??\n")

    # If we have selected a valid menu option, get and print the FB response from url and payload we've constructed.
    if args.menu:
        r = requests.get(myurl, params=mypayload)
        # print(r.text, r.request)
        logging.info("Graph call to >> %s <<", r.request.url)
        # unpack the FB JSON and print it
        mydata = json.loads(r.text)
        for keyz in sorted(mydata.keys()):
            print("{} is {}.".format(keyz, mydata[keyz]))
        print("\n")
    # end of __main__


def get_args():
    ''' set up CLI menu and get args passed in. '''
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='This script returns results from Facebook graph calls against various objects.')
    parser.add_argument("-sc","--show_cred", action='store_true', default=False,
                        help ="Show the FB Ad Account (cred) we are working with.")
    parser.add_argument("-gc","--get_cred", action='store_true', default=False,
                        help ="Lookup credential and get access token. Please provide Pipeline for central (1,2,4,5), "
                              "and a string \nto match against the credential name. Example -gc -p5 -lqa5@nanigans")
    parser.add_argument("-p","--pipeline", action='store', type=int,
                        help ="For Credential lookup (only), give us the # of the pipeline of the ad account you are "
                              "interested in... \nValid options are 1, 2, 4, and 5")
    parser.add_argument("-l","--lookup", action='store', type=str,
                        help ="For Credential lookup (only), give us a string to match against (a single) Ad Account Name.")
    parser.add_argument("-m","--menu", type=int, choices=[1,2,3,4,5,6,7],
                        help ="Choose a graph call per the menu.\n"
                              "1) Show Ad Account detail and connections.\n"
                              "2) Show Ad Account spend from yesterday from reportstats.\n"
                              "3) Show FB placement details for -f=FB Assigned ID.\n"
                              "4) Show FB spend stats for -f=FB_ID.\n"
                              "5) Campaign-Adset-Placement Status for -f=FB Assigned ID!\n"
                              "6) Show Custom Audience details for -f=CA ID.\n" 
                              "7) Creative and Page/Post detail for -f=FB Assigned ID.") 
    parser.add_argument("-f","--fbid", action='store', type=int,
                        help ="Pass in the FB ID for graph calls requesting placement level data.")
    parser.add_argument("-v","--verbose", action='store_true', default=False, help ="Show all fields FB provides.")
    args = parser.parse_args()
    #print("looking up stats for option {} for placement {} with verbosity = {}!".format(args.menu, args.fbid,args.verbose))
    return args


def dosql(pipeline,matchstr):
        ''' connect to the central of specified pipeline and get credential info '''
        if pipeline in (1,2):
            hostno = ''
        else:
            hostno = pipeline
        myhost = "qacentral{}.nanigans.com".format(hostno)
        # myhost2 = '"{}"'.format(myhost)
        ### put a try/except block here for the connection
        dbhandle = pymysql.connect(host=myhost, user="readonly", passwd="secrets!!!!", db="nan_central")
        cur = dbhandle.cursor(pymysql.cursors.DictCursor)
        # does this count as a SQL placeholder?
        my_sql = "SELECT id,account_id,unix_timestamp(last_updated) as updated,config FROM credentials " \
                 "where displayable = 1 and config like '%{}%'".format(matchstr)
        cur.execute(my_sql)
        #row = cur.fetchone()
        rows = cur.fetchall()
        cur.close()
        dbhandle.close()
        # only updating working cred if we match one and only one
        if rows and len(rows) > 1:
            print("Multiple creds matched. Please be more specific with lookup!")
            sys.exit(0)
        else:
            if rows:
                return rows[0]
            else:
                return None


# These are the definitions of the various graph calls. Put them into a module, whydontcha?
def account_connections(account_id,token,verbose):
    ''' MENU=1. Lookup some info for the working credential '''
    # print("https://graph.facebook.com/v2.3/{}/accounts?access_token={}".format(token, account_id))
    if verbose:
        payload = {'fields':'account_groups,account_id,account_status,age,agency_client_declaration,amount_spent,balance,business_city,'
                            'business_country_code,business_name,business_state,business_street2,business_street,business_zip,capabilities,'
                            'currency,daily_spend_limit,id,is_personal,name,spend_cap,timezone_id,timezone_name,'
                            'timezone_offset_hours_utc,tos_accepted,users','access_token': token}
    else:
        payload = {'fields':'account_id,account_status,age,id,timezone_name','access_token': token}
    url_string = "https://graph.facebook.com/v2.3/act_{}/".format(account_id)
    return url_string, payload

def account_spend_yesterday(account_id,token):
    ''' MENU=2.Lookup yesterday's spend for account '''
    payload = {'date_preset':'yesterday','data_columns':'["account_id","spend","impressions","clicks"]','access_token': token}
    url_string = "https://graph.facebook.com/v2.3/act_{}/".format(account_id)
    return url_string, payload

def placement_detail(token,fb_id,verbose):
    ''' MENU=3. Get placement level graph details for a given FBID.'''
    # print("this is the graph info for placement {} okay".format(token, fb_id))
    if verbose:
        payload = {'fields':'id,account_id,adgroup_status,bid_info,bid_type,campaign_id,conversion_specs,'
                            'impression_control_map,last_updated_by_app_id,locations,name,targeting,tracking_specs,'
                            'view_tags,updated_time,created_time,creative','access_token':token}
    else:
        payload = {'fields':'id,account_id,adgroup_status,bid_info,bid_type,campaign_id,created_time','access_token':token}
    url_string = "https://graph.facebook.com/v2.3/{}/".format(fb_id)
    return url_string, payload

def placement_stats(token,fb_id,verbose):
    ''' MENU=4. Get spend, impression, etc... info for placement.'''
    # note that this graph call does not seem to pay attention to fields...
    myfields="id,campaign_id,spent,impressions,clicks,actions"
    if verbose:
        myfields=''
    payload = {'fields':myfields,'access_token':token}
    url_string = "https://graph.facebook.com/v2.3/{}/stats/".format(fb_id)
    print("arg {} and payload = {}".format(verbose,payload))
    return url_string, payload

def struct_status(token,fb_id):
    '''
    MENU=5. This is a compound query against FB ad_campaign_group, adset, and adgroup for status.
    '''
    mixeddict = {}
    # define payloads: 1=adgroup, 2=adset, 3=campaign
    payload1 = {'fields':'id,account_id,bid_type,bid_info,created_time,adgroup_status,name,campaign_id','access_token':token}
    payload2 = {'fields':'id,name,is_autobid,campaign_status,created_time,daily_budget,budget_remaining,campaign_group_id',
                'access_token': token}
    payload3 = {'fields':'id,name,campaign_group_status,objective','access_token': token}
    myurl = "https://graph.facebook.com/v2.3/{}/".format(fb_id)
    # placement graph call
    r = requests.get(myurl, params=payload1)
    logging.info("Compound Status call 1 to >> %s <<", r.request.url)
    mydata = json.loads(r.text)
    for keyz in mydata.keys():
        keyy = "Placement: " + keyz
        #mixeddict.update(keyy,mydata[keyz])
        mixeddict[keyy] = mydata[keyz]
    # get the adset data now
    r1 = requests.get("https://graph.facebook.com/v2.3/{}/".format(mixeddict["Placement: campaign_id"]), params=payload2)
    logging.info("Compound Status call 2 to >> %s <<", r1.request.url)
    moredata = json.loads(r1.text)
    for keyz in moredata.keys():
        keyy = "Adset: " + keyz
        mixeddict[keyy] = moredata[keyz]
    # get the campaign_group data now
    r2 = requests.get("https://graph.facebook.com/v2.3/{}/".format(mixeddict["Adset: campaign_group_id"]), params=payload3)
    logging.info("Compound Status call 3 >> %s <<", r2.request.url)
    yetmoredata = json.loads(r2.text)
    for keyz in yetmoredata.keys():
        keyy = "Campaign: " + keyz
        mixeddict[keyy] = yetmoredata[keyz]
    # print info and exit - might want to consider removing dupe campaign_id from this dict
    for keyz in sorted(mixeddict.keys()):
        print("{} is {}.".format(keyz, mixeddict[keyz]))
    print("\n")
    # and bail out of here
    sys.exit(1)


def creative_post(token,fb_id):
    '''
    MENU=7. This compound query returns creative for a FBID. Will also return page_post detail if appropriate
    '''
    mixeddict = {}
    # define payloads: 1=adgroup, 2=creative, 3=page_post
    payload1 = {'fields':'id,account_id,name,creative','access_token':token}
    payload2 = {'fields':'name,body,image_url,object_story_id,object_story_spec,run_status,actor_id,url_tags,link_url','access_token': token}
    #payload2 = {'fields':'name,body,image_url,image_file,image_crops,link_url,url_tags,object_url,object_id,object_story_id,object_story_spec,run_status,actor_id','access_token': token}
    payload3 = {'fields':'id,name,type,link,source,created_time,message,actions,from,object_id,status_type,picture','access_token': token}
    myurl = "https://graph.facebook.com/v2.3/{}/".format(fb_id)
    # placement graph call
    r = requests.get(myurl, params=payload1)
    logging.info("Compound Status call 1 to >> %s <<", r.request.url)
    mydata = json.loads(r.text)
    for keyz in mydata.keys():
        keyy = "Placement: " + keyz
        #mixeddict.update(keyy,mydata[keyz])
        mixeddict[keyy] = mydata[keyz]
    # get the creative ID
    tinydict = mixeddict["Placement: creative"]
    creativeid = tinydict["id"]
    #print("ran placement query, the creative id is {}.".format(creativeid))
    # get the creative data now
    r1 = requests.get("https://graph.facebook.com/v2.3/{}/".format(creativeid), params=payload2)
    logging.info("Compound Status call 2 to >> %s <<", r1.request.url)
    moredata = json.loads(r1.text)
    for keyz in moredata.keys():
        keyy = "Creative: " + keyz
        mixeddict[keyy] = moredata[keyz]
    # get the  page/post data if there is an object_story_id
    if (mixeddict["Creative: object_story_id"]):
        r2 = requests.get("https://graph.facebook.com/v2.3/{}/".format(mixeddict["Creative: object_story_id"]), params=payload3)
        logging.info("Compound Status call 3 >> %s <<", r2.request.url)
        yetmoredata = json.loads(r2.text)
        for keyz in yetmoredata.keys():
            keyy = "Page-Post: " + keyz
            mixeddict[keyy] = yetmoredata[keyz]
    else:
        pass # no r2 query ro run
    # print compound query info and exit
    for keyz in sorted(mixeddict.keys()):
        print("{} is {}.".format(keyz, mixeddict[keyz]))
    print("\n")
    # and bail out of here
    sys.exit(1)


def custom_audience(token,ca_id):
    ''' MENU=6. Lookup custom audience details '''
    payload = {'fields':'account_id,approximate_count,name,operation_status,subtype,data_source','access_token':token}
    url_string = "https://graph.facebook.com/v2.3/{}/".format(ca_id)
    return url_string, payload


if __name__ == '__main__':
    main()
    sys.exit(1)

# the end
