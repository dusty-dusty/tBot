import sqlite3
import asyncio
import twitchio
from twitchio.ext import commands
from time import sleep , strftime, time
from logging import getLogger , INFO
from logdna import LogDNAHandler
from livecheck import *
from botprefix import *
from keep_alive import keep_alive
from threading import Thread


key = 'myapiKey'
logs = getLogger( 'logdna' )
logs.setLevel( INFO )
options = { 'hostname': 'Twitch_Log' , 'index_meta': True , 'include_standard_meta': False }
logInput = LogDNAHandler( key , options )
logs.addHandler( logInput )
temp3 = False
hasBeenLive = False
startTimerP = time()
promptStop = 600

toCommit = []

chanID = { 'forsen': 22484632 , 'lirik': 23161357 ,'drdisrespect': 17337557 ,
           'mizkif': 94753024 ,
           'trainwreckstv': 71190292 , 'xqcow': 71092938 , 'pokelawls': 12943173 , 'itssliker': 39885827 ,
           'summit1g': 26490481 , 'alebrelle': 91859831 , 'dusty_________': 437214733 , 'greekgodx':15310631,
           'destiny': 18074328 , 'lacari': 29400754 , 'loltyler1': 51496027 , 'esfandtv': 38746172 ,
           'hasanabi': 207813352 , 'andymilonakis': 51858842 , 'jinnytty': 159498717 , 'm0xyy': 69012069 ,
           'valeria7k': 192376620 , 'sttasha': 205889273 , 'amouranth': 125387632 , 'legendarylea': 37116492 ,
           'pokimane': 44445592 , 'dizzykitten': 47474524 , 'loserfruit': 41245072 , 'kittyplays': 39627315 ,
           'loeya': 166279350 , 'alinity': 38718052 , 'stpeach': 100484450 , 'adeptthebest': 116885541 ,
           'nmplol': 21841789, 'paymoneywubby': 38251312 , 'knut': 43494917 , 'nymn': 62300805 ,
           'imaqtpie': 24991333 , 'kitboga': 32787655, 'sodapoppin':26301881, 'riotgames': 36029255,
           'academy':124421740, 'avoidingthepuddle':23528098,
           'esl_csgo':31239503, 'rainbow6':65171890}

# set up the bot
bot = commands.Bot(
    irc_token = TMI_TOKEN ,
    client_id = CLIENT_ID ,
    nick = BOT_NICK ,
    prefix = BOT_PREFIX ,
    initial_channels = CHANNELS
)

@bot.event
async def event_ready():
    #'Called once when the bot goes online.'
    print( f"{BOT_NICK} | Logging! {strftime( '%c')}" )
    opts = {'level': 'Warn', 'app': 'BotAlive'}
    logs.info(f"{BOT_NICK} | Logging! {strftime( '%c')}", opts)
    ws = bot._ws


@bot.event
async def event_message( ctx ):
    global startTimerP
    'Runs every time a message is sent in chat.'

    fixPre = str( ctx.content ).replace( '%' , "(Prefix) " )

    await bot.handle_commands( ctx )

    if '%' in ctx.content.lower()[ 0:1 ]:
        opts = {'level': 'Info', 'app': 'TwitchLogger'}
        logs.info(f"{ctx.channel} {ctx.author.name}, Has run command: {fixPre}", opts)
    if ctx.author.name == "dusty_________":
        opts = {'level': 'Info', 'app': 'TwitchLogger'}
        logs.info(f"{ctx.channel} {ctx.author.name}: {fixPre}", opts)
    promptTimer = time() - startTimerP
    if promptTimer > promptStop:  # check if live.
        startTimerP = time()
        await AlebrelleFirst( ctx )

    await listCommit( ctx )


@bot.command( name = 'c' )
async def checkLive2( ctx ):
    opts = {'level': 'Info', 'app': 'TwitchLogger'}
    logs.info(f"Size left to commit:{len(toCommit)}", opts)
    await bot._ws.send_privmsg( "dusty_________" , f'to commit left: {len(toCommit)}' )

async def listCommit( ctx ):
    global hasNot
    fixString = str( ctx.content ).replace( '"' , "''" )
    fixPre = fixString.replace( '%' , "(Prefix) " )

    userType = 'User'
    try:
        if ctx.author.is_mod is True:
            userType = "Mod"
            if ctx.author.is_subscriber == 1:
                userType += ',Sub'
        elif ctx.author.is_subscriber == 1:
            userType = 'Sub'
        if ctx.author.is_turbo == 1:
            userType += ',Turbo'
    except Exception as e:
        pass

    opts = {'level': 'Info', 'app': 'AllLogs'}
    logs.info(f"({userType}) ID:{ctx.author.id} Username:{ctx.author.name} Channel-ID:{chanID[ str( ctx.channel ) ]} channel:{ctx.channel} Said:{fixPre}", opts)

    toCommit.append((f"{ctx.author.id}",f"{ctx.author.name}",f"{userType}",f"{chanID[ str( ctx.channel ) ]}",f"{ctx.channel}",f'{strftime( "%c" )}',f"{fixString}"))

async def AlebrelleFirst( ctx ):
    global temp3
    global promptStop

    liveCheck = twitchapi( "alebrelle" )

    if liveCheck != False and liveCheck != True:
        opts = {'level': 'Info', 'app': 'AllLogs'}
        logs.info(f"liveCheck = {liveCheck}", opts)


    if liveCheck and temp3:
        temp3 = False
        await bot._ws.send_privmsg( "alebrelle" , '!first' )
        await asyncio.sleep( 4 )
        await bot._ws.send_privmsg( "alebrelle" , 'A bot beat you all :) if not  @Dusty_________ and tell him how bad he is!' )
        opts = {'level': 'Info', 'app': 'AllLogs'}
        logs.info(f"liveCheck : Is Frist. Check :)", opts)
    if not liveCheck and not temp3:
        temp3 = True

    if liveCheck:
        promptStop = 600
    else:
        promptStop = 2


def databasecommit():
    while True:
        if len(toCommit) >= 500:
            insertMultipleRecords(toCommit)
        else:
            sleep(0.1)

def insertMultipleRecords(recordList):
    global toCommit
    try:
        toRemove = len(recordList)
        sqliteConnection = sqlite3.connect(f'{strftime( "%m" )}-{strftime( "%d" )}-{strftime( "%y" )}.db' )
        cursor = sqliteConnection.cursor()
        sqlite_insert_query = """INSERT INTO messages_tracker
                          (user_id, display_name, user_type, channel_id, channel_name, timestamp, message) 
                          VALUES (?, ?, ?, ?, ?, ? ,?);"""

        cursor.executemany(sqlite_insert_query, recordList)
        sqliteConnection.commit()
        sqliteConnection.commit()
        cursor.close()

    except Exception as e:
        noTable = str(e)
        if noTable == "no such table: messages_tracker":
            conn = sqlite3.connect(f'{strftime( "%m" )}-{strftime( "%d" )}-{strftime( "%y" )}.db' )
            c = conn.cursor()
            c.execute('''CREATE TABLE messages_tracker
                (user_id integer,display_name text,user_type text, channel_id integer,channel_name text,timestamp text ,message blob)''')
            conn.commit()
            conn.close()
        else:
            meta = {'Error Info': str(e)}
            opts = {'level': 'ERROR', 'app': 'DataBase', 'meta': meta}
            logs.info('Click for info!', opts)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            toCommit = toCommit[toRemove:]


commitStart = Thread( target = databasecommit )
commitStart.start()

keep_alive()

bot.run()

