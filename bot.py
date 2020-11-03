import telebot
from telebot import types
import time
import emoji
import os
import numpy as np
from datetime import datetime as dt
from datetime import timedelta as td

TOKEN = '1231415215:AAEFlJrwoUtfcPSrRvgIGTC0PdEnJvHTPOs'

bot = telebot.TeleBot(TOKEN)

cw_id = 408101137
helper_id = 526586204
pax_id = 1231415215

def horario(hora):
    horarios = {'Morning' : [3, 4, 11, 12, 19, 20], 'Day' : [5, 6, 13, 14, 21, 22], 'Evening' : [7, 8, 15, 16, 23, 0], 'Night' : [9, 10, 17, 18, 1, 2]}
    
    for i in horarios:
        if(hora in horarios[i]):
            return(i)

def forward_from_cw(message):
    if(message.forward_from != None):
        return(message.forward_from.id == cw_id)
    
    return(False)

def clasificador(cid, ts):
    loot = {'Morning' : {'exp' : 0, 'gold' : 0}, 'Day' : {'exp' : 0, 'gold' : 0}, 'Evening' : {'exp' : 0, 'gold' : 0}, 'Night' : {'exp' : 0, 'gold' : 0}}
    full = {'exp' : 0, 'gold' : 0}
    loot_reg = {'Valley': loot, 'Swamp': loot, 'Forest': loot}
    
    file = open(str(cid) + '/' + 'forward_date.txt', 'r')
    names = file.readlines()
    file.close()
    names = np.array(names, dtype=np.int)
    names = names[names>ts]
    for i in names:
        h = horario(dt.fromtimestamp(i).hour)
        file = open(str(cid) + '/' + str(i), 'r')
        lines = file.readlines()
        for line in lines:
            if(line[:12] == 'You received'):
                loot[h]['exp'] += int(line.split()[2])
                if(len(line.split()) > 4):
                    loot[h]['gold'] += int(line.split()[5])
            elif(line[:6] == 'Earned'):
                key = line[8:line.find('(') - 1]
                cant = int(line.split()[-1][1:-1])
                if(key in loot[h].keys()):
                    loot[h][key] += cant
                else:
                    loot[h][key] = cant
    for i in loot:
        full['exp'] += loot[i]['exp']
        full['gold'] += loot[i]['gold']
        for j in loot[i]:
            if(j in full.keys()):
                full[j] += loot[i][j]
            else:
                full[j] = loot[i][j]
    loot['Full'] = full
    return(loot)

def listener(messages):
    
    for m in messages:
        cid = m.chat.id
        
        if(m.content_type == 'text'):
            if(cid > 0):
                mensaje = str(m.chat.first_name) + ' [' + str(cid) + '] ' + m.text
            else:
                mensaje = str(m.from_user.first_name) + ' [' + str(cid) + '] ' + m.text
        else:
            if(cid > 0):
                mensaje = str(m.chat.first_name) + ' [' + str(cid) + '] '
            else:
                mensaje = str(m.from_user.first_name) + ' [' + str(cid) + '] '

        f = open('log.txt', 'a')
        f.write(emoji.demojize(mensaje) + '\n')
        f.close()
        print(emoji.demojize(mensaje))
        #if(m.forward_from != None):
        #    print('\n' + str(m.forward_from.first_name) + ' ['+ str(m.forward_from.id) + ']\n')

bot.set_update_listener(listener)

@bot.message_handler(commands=['help'])
def command_help(m):
    HELP = 'you can using the follow command:\n\n/help - guide to use the bot'
    cid = m.chat.id
    bot.send_chat_action(cid, 'typing')
    time.sleep(1)
    bot.send_message(cid, HELP)

@bot.message_handler(commands=['loot'])
def command_loot(m):
    cid = m.chat.id
    text = m.text
    #now = dt.now()
    now = dt.fromtimestamp(m.date)
    
    if(len(text.split()) > 1) :
        t = int(text.split()[1])
    else:
        t = 24
    ts = dt.timestamp(now - td(hours = t))
    if(os.path.isfile(str(cid) + '/' + 'forward_date.txt')):
        loot = clasificador(cid, ts)
        
        #markup = types.ReplyKeyboardMarkup()
        #markup.add('a', 'v', 'd')
        keyboard = types.InlineKeyboardMarkup()
        morning_button = types.InlineKeyboardButton(text=emoji.emojize(':sun_with_face: Morning'), callback_data='Morning ' + str(t) + ' ' + 'Full')
        day_button = types.InlineKeyboardButton(text=emoji.emojize(':sun_with_face: Day'), callback_data='Day ' + str(t) + ' ' + 'Full')
        evening_button = types.InlineKeyboardButton(text=emoji.emojize(':crescent_moon: Evening'), callback_data='Evening ' + str(t) + ' ' + 'Full')
        night_button = types.InlineKeyboardButton(text=emoji.emojize(':crescent_moon: Night'), callback_data='Night ' + str(t) + ' ' + 'Full')
        full_button = types.InlineKeyboardButton(text=emoji.emojize('Full time'), callback_data='Full ' + str(t) + ' ' + 'Full')
        
        keyboard.row(morning_button, day_button, evening_button, night_button)
        keyboard.row(full_button)
        
        dummy = 'Loot in the last ' + str(t) + ' hours\n'
        for i in loot['Full']:
            dummy += '{0}: {1}\n'.format(i, loot['Full'][i])
        bot.send_message(cid, dummy, reply_markup=keyboard)
        #for i in loot:
        #    dummy = 'Loot in the ' + i + ' in the last ' + str(t) + ' horas\n'
        #    for j in loot[i]:
        #        dummy += '{0}: {1}\n'.format(j, loot[i][j])
        #    #print(dummy)
        #    bot.send_message(cid, dummy)
    else:
        bot.send_message(cid, 'Send at least one quest before using /loot')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if(call.message):
        if(call.data.split()[0] != call.data.split()[2]):
            cid = call.message.chat.id
            mid = call.message.message_id
            h = call.data.split()[0]
            now = dt.fromtimestamp(call.message.date)
            t = int(float(call.data.split()[1]))
            ts = dt.timestamp(now - td(hours = t))
            
            loot = clasificador(cid, ts)
            if(h != 'Full'):
                dummy = 'Loot in the ' + h + ' in the last ' + str(t) + ' horas\n'
            else:
                dummy = 'Loot in the last ' + str(t) + ' horas\n'
            for i in loot[h]:
                dummy += '{0}: {1}\n'.format(i, loot[h][i])
            
            keyboard = types.InlineKeyboardMarkup()
            morning_button = types.InlineKeyboardButton(text=emoji.emojize(':sun_with_face: Morning'), callback_data='Morning ' + str(t) + ' ' + h)
            day_button = types.InlineKeyboardButton(text=emoji.emojize(':sun_with_face: Day'), callback_data='Day ' + str(t) + ' ' + h)
            evening_button = types.InlineKeyboardButton(text=emoji.emojize(':crescent_moon: Evening'), callback_data='Evening ' + str(t) + ' ' + h)
            night_button = types.InlineKeyboardButton(text=emoji.emojize(':crescent_moon: Night'), callback_data='Night ' + str(t) + ' ' + h)
            full_button = types.InlineKeyboardButton(text=emoji.emojize('Full time'), callback_data='Full ' + str(t) + ' ' + 'Full')
            
            keyboard.row(morning_button, day_button, evening_button, night_button)
            keyboard.row(full_button)
            
            bot.edit_message_text(chat_id=cid, message_id=mid, text=dummy, reply_markup=keyboard)


@bot.message_handler(func=lambda message: forward_from_cw(message))
def cw(m):
    forward_date = m.forward_date
    cid = m.chat.id
    mid = m.message_id
    text = m.text
    #h = horario(dt.fromtimestamp(forward_date).hour)
    if(not os.path.isdir(str(cid))):
        os.mkdir(str(cid))
    if(not os.path.isfile(str(cid) + '/' + str(forward_date))):
        file = open(str(cid) + '/' + 'forward_date.txt', 'a')
        file.write(str(forward_date) + '\n')
        file.close()
        file = open(str(cid) + '/' + str(forward_date), 'w')
        file.write(emoji.demojize(text))
        file.close()
        bot.send_message(cid, emoji.emojize(':world_map: Done! Quest succesfully added to your statistics.'))
        #bot.forward_message(helper_id, m.from_user.id, mid)
    else:
        bot.send_message(cid, emoji.emojize(':world_map::cross_mark: This quest has already been added'))


bot.polling(none_stop=True)