import asyncio
import aioschedule
import logging
import sys
import nltk
import string
from datetime import datetime
from gotquestions import gq_connector
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData 

TOKEN = 'MASKED_1' # test bot
#TOKEN = 'MASKED_2'   # real bot


# Bot token can be obtained via https://t.me/BotFather
#TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
start_router = Router()

class MyCallback(CallbackData, prefix="my"):
    command: str
    chat_id: int    


class question:    
    def __init__(self, number, text, answer, razdatkaText=None, razdatkaPic=None,  answerPic=None, zachet=None, nezachet=None, comment=None, note=None, 
                 commentPic=None, source=None, authors=None, editors=None, controversials=None, appeals=None, teams=None, correctAnswers=None
                 ):
        self.number = number
        self.text   = text
        self.answer = answer
        self.zachet = zachet
        self.nezachet = nezachet
        self.comment = comment
        self.note    = note  
        self.razdatkaText = razdatkaText
        self.razdatkaPic = razdatkaPic
        self.answerPic = answerPic
        self.zachet = zachet
        self.nezachet = nezachet
        self.comment = comment
        self.note    = note
        self.commentPic = commentPic
        self.source = source
        self.authors = authors
        self.editors = editors
        self.controversials = controversials
        self.appeals = appeals
        self.teams = teams
        self.correctAnswers = correctAnswers


class chat_info:
    cur_pack        = {}
    cur_question    = -1
    cur_timer_on    = True
    cur_timer       = 60
    cur_question_dt = datetime.now()    
    questions       = []
    running         = False
    list_message    = None
    list_page       = 0
    num_pages       = 15
    packs_list      = []

all_chats = {}


async def set_timer(chat_id, timer):
    await set_chat_info( chat_id = chat_id, timer = timer )
    await bot.send_message( chat_id, f"Таймер установлен в {timer} минут") 


async def set_chat_info(chat_id, pack=None, question_num=None, timer_on=None, timer=None, question_dt=None, list_page=0, list_message=None, packs_list=None, num_pages=None):
    if chat_id not in all_chats:
        all_chats[chat_id] = chat_info()

    all_chats[chat_id].cur_pack         = pack if pack is not None else all_chats[chat_id].cur_pack

    if pack is not None:

        all_chats[chat_id].questions = []
        all_chats[chat_id].cur_question = -1
        
        num_tours = len(pack["tours"])
        for cur_tour in range(num_tours):
            num_questions = len(pack["tours"][cur_tour]["questions"])
            for cur_question in range(num_questions):

                q = pack["tours"][cur_tour]["questions"][cur_question]

                editors_str = ""
                for editor in q["editors"]:
                    editors_str += editor["name"]

                authors_str = ""
                for author in q["editors"]:
                    authors_str += author["name"]
    
                r = question (  number = q["number"], text =   q["text"], answer = q["answer"], razdatkaText=q["razdatkaText"], razdatkaPic=q["razdatkaPic"],  answerPic=q["answerPic"], zachet=q["zachet"], nezachet=q["nezachet"], comment=q["comment"], note=q["note"], 
                 commentPic=q["commentPic"], source=q["source"], authors=authors_str, editors=editors_str, controversials=q["controversials"], appeals=q["appeals"], teams=q["teams"], correctAnswers=q["correctAnswers"])

                all_chats[chat_id].questions.append(r)
                                                
    all_chats[chat_id].cur_question     = question_num if question_num is not None else all_chats[chat_id].cur_question
    all_chats[chat_id].cur_timer_on     = timer_on if timer_on is not None else all_chats[chat_id].cur_timer_on
    all_chats[chat_id].cur_timer        = timer if timer is not None else all_chats[chat_id].cur_timer
    all_chats[chat_id].cur_question_dt  = question_dt if question_dt is not None else all_chats[chat_id].cur_question_dt
    all_chats[chat_id].list_page        = list_page if list_page is not None else all_chats[chat_id].list_page
    all_chats[chat_id].num_pages        = num_pages if num_pages is not None else all_chats[chat_id].num_pages
    all_chats[chat_id].list_message     = list_message if list_message is not None else all_chats[chat_id].list_message
    all_chats[chat_id].packs_list       = packs_list  if packs_list is not None else all_chats[chat_id].packs_list
                                

def answer_message(q: question, print_answer=True):
    
    answer = ""
    
    if print_answer:
        answer += f"<b>Ответ:</b>\n"    
        answer += f"{q.answer}\n\n" 

    if ( q.zachet != ""):
        answer += f"<b>Зачет:</b>\n"
        answer += f"{q.zachet}\n\n"

    if ( q.answerPic != ""):
        answer += f"<b>Картинка:</b>\n"
        answer += f"{q.answerPic}\n\n"

    answer += f"<b>Комментарий:</b>\n"
    answer += f"{q.comment}\n\n"

    if ( q.source != ""):
        answer += f"<b>Источник:</b>\n"
        answer += f"{q.source}\n\n"

    if ( q.editors != ""):
        answer += f"<b>Редактор(ы):</b> {q.editors}\n\n"        

    if ( q.authors != ""):
        answer += f"<b>Автор(ы):</b> {q.authors}\n\n"        
    
    if ( q.teams is not None and q.teams != 0):
        answer += f"<b>Взятий:</b> {q.correctAnswers}/{q.teams}({round(100*q.correctAnswers/q.teams)}%)\n"        

    return answer   

@start_router.callback_query(MyCallback.filter(F.command == 'send_hint'))
async def send_hint(query: CallbackQuery, callback_data: MyCallback):   
    # чтобы кнопка не мигала 
    await query.answer()

    cur_chat_id = callback_data.chat_id
    q = all_chats[cur_chat_id].questions[all_chats[cur_chat_id].cur_question]
    
    masked_answer = "".join([ '_' if c in string.punctuation else '*' if c.isalpha() else '0' if c.isdigit() else ' ' for c in q.answer ])    

    # remove last dot
    if masked_answer[-1:] == '.':
        masked_answer = masked_answer[:-1]        
    
    await bot.send_message( cur_chat_id, masked_answer )     
    

@start_router.callback_query(MyCallback.filter(F.command == 'send_next'))
async def send_next_question(query: CallbackQuery, callback_data: MyCallback):   
    # чтобы кнопка не мигала 
    await query.answer()

    cur_chat_id = callback_data.chat_id
    await ask_next_question(cur_chat_id)

@start_router.callback_query(MyCallback.filter(F.command == 'list_none'))
async def list_none(query: CallbackQuery, callback_data: MyCallback):       
    await query.answer()


@start_router.callback_query(MyCallback.filter(F.command == 'list_backward'))
async def list_backward(query: CallbackQuery, callback_data: MyCallback):       
    await query.answer()

    chat_id = callback_data.chat_id
    num_pages = all_chats[chat_id].num_pages    
    await set_chat_info(chat_id = chat_id, list_page = all_chats[chat_id].list_page + 1)    
    print ("Backward:" + str(all_chats[chat_id].list_page))

    await show_packs_page(chat_id, first_time = False, num_pages = num_pages)        


@start_router.callback_query(MyCallback.filter(F.command == 'list_forward'))
async def list_forward(query: CallbackQuery, callback_data: MyCallback):   
    await query.answer()

    chat_id = callback_data.chat_id
    num_pages = all_chats[chat_id].num_pages    
    await set_chat_info(chat_id = chat_id, list_page = all_chats[chat_id].list_page - 1)    
    print ("Backward:" + str(all_chats[chat_id].list_page))

    await show_packs_page(chat_id, first_time = False, num_pages = num_pages)        


@start_router.callback_query(MyCallback.filter(F.command == 'send_answer'))
async def send_answer(query: CallbackQuery, callback_data: MyCallback):     
    # чтобы кнопка не мигала 
    await query.answer()
    await direct_send_answer( callback_data.chat_id)



async def direct_send_answer(cur_chat_id):

    q = all_chats[cur_chat_id].questions[all_chats[cur_chat_id].cur_question]

    if ( q.answerPic != ""):
        await bot.send_photo( cur_chat_id, "http://gotquestions.online" + q.answerPic)
    
    if ( q.commentPic != ""):
        await bot.send_photo( cur_chat_id, "http://gotquestions.online" + q.commentPic)
    

    answer = answer_message( q, True)
    
    inline_kb_list = [
        [
        InlineKeyboardButton(text="Дальше", callback_data = MyCallback(command = 'send_next', chat_id = cur_chat_id).pack())
        ]        
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb_list )

    await bot.send_message( cur_chat_id, answer, reply_markup= keyboard )        
    all_chats[cur_chat_id].running = False


async def ask_next_question(chat_id):

    all_chats[chat_id].cur_question += 1   
    all_chats[chat_id].cur_question_dt = datetime.now()
    all_chats[chat_id].running = True

    q = all_chats[chat_id].questions[all_chats[chat_id].cur_question]
    if ( q.razdatkaPic != ""):
        await bot.send_photo( chat_id, "http://gotquestions.online" + q.razdatkaPic)

    if ( q.razdatkaText != ""):
        await bot.send_message( chat_id, q.razdatkaText)    
                
    text = f"<b>Вопрос {q.number}.</b>\n\n"
    text += f"{q.text}"
    
    inline_kb_list = [
        [        
        InlineKeyboardButton(text="Подсказка",  callback_data = MyCallback(command = 'send_hint'  , chat_id = chat_id).pack()),                
        InlineKeyboardButton(text="Ответ",  callback_data = MyCallback(command = 'send_answer'  , chat_id = chat_id).pack()),                
        InlineKeyboardButton(text="Дальше", callback_data = MyCallback(command = 'send_next', chat_id = chat_id).pack())
        ]        
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb_list )

    Message = await bot.send_message( chat_id, text, reply_markup= keyboard )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


async def load_pack(chat_id, num_pack):
    Message = await bot.send_message( chat_id, 'Загружаем пакет номер ' + str(num_pack))                        

    connector = gq_connector()
    json = connector.get_pack(num_pack)

    title = json["title"]    
    played = json["endDate"]    

    pack_info =  f"<b>{title}</b>\n\n"
    pack_info += f"{played[0:10]}\n\n"
    
    pack_info += f"Редакторы пакета: "    
    for editor in json["editors"]:
        pack_info += f"{editor["name"]},"

    if json["info"] != "":
        pack_info += f"\n\n{json["info"]}"         

    Message = await bot.send_message( chat_id, pack_info)                            
    await set_chat_info(chat_id = chat_id, pack = json)
    await ask_next_question(chat_id)


async def check_answer(chat_id, text_command, from_user):

    q = all_chats[chat_id].questions[all_chats[chat_id].cur_question]

    # first remove all symbols except alpha-numeric
    processed_command = ''.join(ch for ch in text_command if ch.isalnum()).lower()        
    processed_answer = ''.join(ch for ch in q.answer if ch.isalnum()).lower()

    zachets = q.zachet.split(",")
    processed_zachets = []    

    for z in zachets:
        processed_zachets.append(''.join(ch for ch in z if ch.isalnum()).lower())

    correct_answer = False        
    approximate_answer = False
    
    if processed_command == processed_answer: 
        correct_answer = True

    if not correct_answer:
        for z in processed_zachets:
            if processed_command == z: 
                correct_answer = True
                break
                
    if not correct_answer:
        dist1 = nltk.edit_distance(processed_command, processed_answer)
        print ( dist1 )

        dist2 = 99999 

        for z in processed_zachets:        
            dist2 = min(  dist2, nltk.edit_distance(processed_command, z))
            print ( dist2 )

        dist = min(dist1, dist2)   
        print ( dist )
        print ( processed_command )
        print ( processed_answer )

        if dist * 4 <=  min( len(processed_command), len(processed_answer)):
            approximate_answer = True
        else:
            approximate_answer = False    

    if correct_answer:
        ans =  f"Блестяще, <b>{from_user}</b>!\n"
        ans += f"<b>{text_command}</b> абсолютно верный ответ.\n\n"
    elif approximate_answer:
        ans =  f"Отлично, <b>{from_user}</b>!\n"
        ans += f"<b>{text_command}</b> не совсем верный ответ, но я его зачту. Верный ответ: <b>{q.answer}</b>\n\n"

    if correct_answer or approximate_answer:

        if ( q.answerPic != ""):
            await bot.send_photo( chat_id, "http://gotquestions.online" + q.answerPic)
    
        if ( q.commentPic != ""):
            await bot.send_photo( chat_id, "http://gotquestions.online" + q.commentPic)

        ans += answer_message( q, False)        

        inline_kb_list = [
            [
                InlineKeyboardButton(text="Дальше", callback_data = MyCallback(command = 'send_next', chat_id = chat_id).pack())
            ]        
        ]
    
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb_list )
        await bot.send_message(chat_id, ans, reply_markup = keyboard)
        all_chats[chat_id].running = False

    else:
        print ( processed_command)
        print ( q.answer.lower() )
        print ( dist )
        await bot.send_message(chat_id, f"<b>{text_command}</b> это неверный ответ. Попробуйте еще раз.")                                                           


async def packs_list_message(chat_id):
    packs_list = all_chats[chat_id].packs_list
    list_page = all_chats[chat_id].list_page
    print ( "Packs:" + str(list_page) )
    packs_per_page = 6

    final_message = ""

    for pack in packs_list[ packs_per_page * list_page : packs_per_page * (list_page + 1 ) ]:                  
            trueDl_str = ""
            if len(pack.trueDl) >= 1:
                trueDl_str = f"{pack.trueDl[0]}: "

            final_message += f"<b>{trueDl_str}{pack.title}</b>({pack.editors})\n"
            final_message += f"Сыграно {0} из {pack.questions}   Дата: {pack.endDate[0:10]}\n"
            final_message += f"Выбрать:    /load_{pack.id}\n\n"

    return final_message        

async def show_packs_page(chat_id, first_time, num_pages):

    final_message = await packs_list_message(chat_id)
    list_page = all_chats[chat_id].list_page
    print( "list_page = " + str(num_pages))
    print( "pages = " + str(num_pages))
            
    if ( list_page > 0 and list_page < num_pages - 1):
        inline_kb_list = [[        
        InlineKeyboardButton(text="Более новые ",  callback_data = MyCallback(command = 'list_forward'  , chat_id = chat_id).pack()),                                    
        InlineKeyboardButton(text="Более старые",  callback_data = MyCallback(command = 'list_backward' , chat_id = chat_id).pack()),                        
        ]]                     
    elif list_page == 0:    
        inline_kb_list = [[        
        InlineKeyboardButton(text="            ",  callback_data = MyCallback(command = 'list_none'      , chat_id = chat_id).pack()),                
        InlineKeyboardButton(text="Более старые",  callback_data = MyCallback(command = 'list_backward'  , chat_id = chat_id).pack()),                        
        ]]
    else:
        inline_kb_list = [[        
        InlineKeyboardButton(text="Более новые ",  callback_data = MyCallback(command = 'list_forward' , chat_id = chat_id).pack()),                
        InlineKeyboardButton(text="            ",  callback_data = MyCallback(command = 'list_none'   , chat_id = chat_id).pack()),                        
        ]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb_list )    

    # Сохраняем сообщение чтобы в будущем его править при нажатии кнопок вперед-назад
    if first_time:
        list_message = await bot.send_message( chat_id, final_message, reply_markup= keyboard)
        print ( "Сохранили: " + str(list_message.message_id))
        await set_chat_info(chat_id = chat_id, list_message = list_message.message_id)    
        print ( "Точно сохранили: " + str(all_chats[chat_id].list_message))
    else:
        print ( "Теперь читаем: " + str(all_chats[chat_id].list_message))
        await bot.edit_message_text( chat_id = chat_id, message_id = all_chats[chat_id].list_message, text = final_message, reply_markup= keyboard)    


async def show_packs(chat_id, num_pages):
    
    connector = gq_connector()
    
    # Почему деленное на 3? Потому что у gq в странице 18 пакетов, а у нас - 6
    packs_list = connector.get_packs_list(int((num_pages+5)/3))    

    await set_chat_info(chat_id = chat_id, list_page = 0, packs_list = packs_list, num_pages = num_pages)    

    await show_packs_page(chat_id, first_time = True, num_pages = num_pages)    
    
    
async def process_command(chat_id, text_command, from_user):
    
    if text_command.startswith('/timer'):        
        if text_command[7:].isdigit():
            timer = int(text_command[7:])
            await set_timer(chat_id, timer)
            return 
    
    if text_command.startswith('/list'):
        if text_command[6:].isdigit():
            num_pages = int(text_command[6:])
        else:   
            num_pages = 15

        await show_packs(chat_id, num_pages)
        return

    if text_command.startswith('/load'):      
        # find digits in text command after /load but before character @  
        part = text_command[6:].split('@')[0]
        if part.isdigit():
            num_pack = int(part)
            await load_pack(chat_id, num_pack)
            return 
    
    if text_command.startswith('/'):
        if ( all_chats[chat_id].cur_question != -1):
            await check_answer(chat_id, text_command[1:], from_user)
            return
        
    Message = await bot.send_message( chat_id, text_command[::-1])    


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    #try:
        # Send a copy of the received message
    await process_command(message.chat.id, message.text, message.from_user.full_name)
        #await message.answer(message)                
        #await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
        #Message = await bot.send_message(chat_id=message.chat.id, text= message.text[2:4])

    #TODO: catch exceptions later
    #except TypeError:
        # But not all the types is supported to be copied so need to handle it
    #    await message.answer("Something happened: wrong type!")


async def scheduler(delay: int):

    while True:
        for chat_id in all_chats:
            if all_chats[chat_id].cur_timer_on:
                if all_chats[chat_id].running:
                    cur_dt = datetime.now()
                    delta = cur_dt - all_chats[chat_id].cur_question_dt
                    if delta.total_seconds() >  all_chats[chat_id].cur_timer * 60 - 60 and delta.total_seconds() <= all_chats[chat_id].cur_timer  * 60 - 50 and  all_chats[chat_id].cur_timer > 0:                    
                        await bot.send_message( chat_id, "Поторопитесь! Осталось меньше минуты до истечения таймера") 
                                            
                    if delta.total_seconds() > all_chats[chat_id].cur_timer * 60:                    
                        await direct_send_answer(chat_id) 
                        all_chats[chat_id].running = False
                    
        await asyncio.sleep(delay=delay)  


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    #bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))    

    # And the run events dispatching    
    task = asyncio.create_task(coro=scheduler(delay=10))
    dp.include_router(start_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
