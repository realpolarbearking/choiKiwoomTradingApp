# from strategy.CHOIStrategy import *
import telegram
from util.const import *
from telegram.ext import Updater
from telegram.ext import CommandHandler

token = TELEGRAM_TOKEN
bot = telegram.Bot(token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


userChoice = ""
userChoice1 = ""
conditions = ""

def sendMessage():

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    conditions = CommandHandler('conditions', conditionSender)
    dispatcher.add_handler(conditions)
    conditionStartHandler = CommandHandler('search', search)
    dispatcher.add_handler(conditionStartHandler)
    conditionStartHandler1 = CommandHandler('search', searchResult)
    dispatcher.add_handler(conditionStartHandler1)

    # polling
    updater.start_polling()

def getConditionListMsg(mes):
    global conditions
    conditions = mes
    return conditions
def returnUserChoice():
    return userChoice
def getUserSelectionMsg(mes):
    global userChoice1
    userChoice1 = mes
    return userChoice1

# command hander
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="BULLS_BOT ON!")
def conditionSender(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=conditions)
def search(update, context):
    global userChoice
    keywords = 'Start: '
    keywords += '{}'.format(context.args[0])
    userChoice = context.args[0]
    context.bot.send_message(chat_id=update.effective_chat.id, text=keywords)
def searchResult(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=userChoice1)

"""
import requests

TARGET_URL = 'https://notify-api.line.me/api/notify'


def send_message(message, token=None):

    try:
        response = requests.post(
            TARGET_URL,
            headers={
                'Authorization': 'Bearer ' + token
            },
            data={
                'message': message
            }
        )
        status = response.json()['status']
        # 전송 실패 체크
        if status != 200:
            # 에러 발생 시에만 로깅
            raise Exception('Fail need to check. Status is %s' % status)

    except Exception as e:
        raise Exception(e)
"""
