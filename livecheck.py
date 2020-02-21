import urllib.request
import urllib.error
import json
from time import sleep

def twitchapi( chan_name  ):
    try:
        url = f"https://api.twitch.tv/helix/streams?user_login={chan_name}"
        heading = {
            "Client-ID": "myID"
        }
        req = urllib.request.Request( url , headers = heading )
        response = urllib.request.urlopen( req )
        output = json.loads( response.read() )
        output = output["data"]
        for i in output:
            output = i
        if "type" in output:
            return True
        else:
            return False
    except Exception as e:
        print( 'gettwitchapi' , e )
        return e



def getuserid( chan_name ):
    try:
        url = f"https://api.twitch.tv/kraken/users?login={chan_name}"
        heading = {
            "Client-ID": "myID" ,
            'Accept': 'application/vnd.twitchtv.v5+json' ,
        }
        req = urllib.request.Request( url , headers = heading )
        resp = urllib.request.urlopen( req )
        output = json.loads( json.dumps( json.loads( resp.read() )[ 'users' ][ 0 ] ) )
        return output[ '_id' ]
    except urllib.error as e:
        print( 'getuserid' , e )
        return e
    except Exception as e:
        print( 'getuserid' , e )
        return e



