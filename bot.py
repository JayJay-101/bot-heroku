import logging
import requests
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import multiprocessing 
import asyncio
import time
import lo
from pyrogram import Client
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
proxy=None

API_URL=None
_token="1234:abcdabcd"
PORT = 8443
logger = logging.getLogger(__name__)


api_id = '1234'
api_hash = "abcds"

adpp=Client(lo.session, api_id, api_hash) 
async def fetchIt(d,r):
    t=[]
    async with adpp:
        for i in d:
            if i[0]=="@":
                i=i[1:]
            try:
                j=((await adpp.get_history(i, offset_date =int(time.time()), limit=1))[0].message_id-((await adpp.get_history(i, offset_date =int(time.time())-86400, limit=1))[0].message_id))
            except:
                j=None
            print(j)
            if j==0 or j==None:
                t.append(0)
                continue
            t.append(j)
        r['d']=t
            

def get_data(d,r):
    adpp.run(fetchIt(d,r))
    
def _fmain():
    def _make_request(token, method_name, params=None):

        """Makes a request to the Telegram API.
        :param token: The bot's API token. (Created with @BotFather)
        :param method_name: Name of the API method to be called. (E.g. 'getUpdates')
        :param method: HTTP method to be used. Defaults to 'get'.
        :return: The result parsed to a JSON dictionary.
        """
       
        request_url = "https://api.telegram.org/bot{0}/{1}".format(token, method_name)
        try:
            result = requests.get(request_url,params=params)
            got_result = True
        except :
            logger.debug("Timeout Error on {0} method ".format(method_name))
        logger.debug("The server returned: '{0}'".format(result.text.encode('utf8')))
        
        json_result = result.json()
        if json_result["ok"]:
            return json_result['result']
        else:
            json_result['result']=0
            return json_result['result']


    def get_chat_members_count(token, chat_id):
        method_url = r'getChatMembersCount'
        payload = {'chat_id': chat_id}
        return _make_request(token, method_url, params=payload)
    def sort_list(result):
        s=sorted(result.items(), key=lambda e: e[1])
        return s
    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.
    def start(update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('send me chat_id_list, i will rank them')


    def help(update, context):
        """Send a message when the command /help is issued."""
        a=''.join(context.args)

        update.message.reply_text(a+' Help!')


    def echo(update, context):
        """Echo the user message."""
        input_list=update.message.text.split()
        input_list=[i for n, i in enumerate(input_list) if i not in input_list[:n]]##sortify
        unsort_list=[]
        
        for i in input_list:
            if '@' in i[0] and '@'not in i[1:]:
                unsort_list.append(get_chat_members_count(_token,i))
            else:
                unsort_list.append(get_chat_members_count(_token,'@'+i))
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=get_data, args=(input_list,return_dict))
        p.start()
        p.join()
        d=return_dict
        print(d)
        result = { k:v  for k,*v in zip(input_list,unsort_list,d['d'])}
        fil=[d for d in result.keys() if result[d][1]==0 or result[d][0]==0]
        lastput=['{} is either dead / bad / not a group / private\n'.format(f) for f in fil]
        lastput=''.join(lastput)
        for i in fil:
        	del(result[i])

        sorted_list=sort_list(result)
        output = ["{} {} \n".format(i,count) for i,count in zip(range(1,len(sorted_list)+1),sorted_list)]
        output=''.join(output)
       
        update.message.reply_text('Ranks are:- \n'+output+lastput)


    def error(update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)


    def main():
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater(_token, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, echo))
        # log all errors
        dp.add_error_handler(error)

        # Start the Bot 
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
       
    main()
if __name__ == '__main__':
   
  
    d=_fmain()
