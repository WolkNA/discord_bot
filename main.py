from code import interact
from distutils.log import info
from poplib import POP3_SSL_PORT
from time import sleep
from turtle import delay
import discord
import asyncio
import yt_dlp as youtube_dl
from youtubesearchpython import VideosSearch
import os
from discord.ext import tasks, commands
from discord.utils import get
from discord.ui import Button, View
import json
import requests
import random
import datetime
from natsort import natsorted
import multiprocessing

TOKEN=''
bot = commands.Bot(command_prefix=['/', ':','-'], intents=discord.Intents.all())

global music_queue
music_queue = []
global info_queue
info_queue = []
global cur_info
cur_info = ''
global source
source = ''
global loop_mode
with open('./loop_mode.json', 'r+') as lm_file:
    loop_mode = json.load(lm_file)
global pause_mode
pause_mode = False
global videosSearch
videosSearch = []
global posts
posts = []
global auto_delay
with open('./auto_delay.json', 'r+') as ad_file:
    auto_delay = json.load(ad_file)
global idiots_list
with open('./idiots_list.json','r+') as il_file:
    idiots_list = json.load(il_file)



@tasks.loop(seconds = auto_delay)
async def auto_hentai():      
    channel = bot.get_channel(849373450589962301)
    #channel = bot.get_channel(999058592785240196)
    global posts
    global white_dict
    location = []
    prev = 0
    author=''
    for value in white_dict.values():
        if value[0]+value[1]>0: 
            prev = prev+value[0]+value[1]
        location.append(prev)
    max = location[-1]
    r = random.randint(0,max-1)
    c = 0
    for key in white_dict.keys():
        if r>=location[c]:
            c+=1
        else: 
            author = key
            l = len(posts[author])
            number = random.randint(0,l-1)
            await channel.send(posts[author][number]['file_url'])
            return


def sequential(calc, proc, posts, res_text, white_list):
    for i in range(calc):
        iter = 0
        l=0
        while True:
            try: response = requests.get(res_text+white_list[proc+int(multiprocessing.cpu_count()/2)*i]+'&pid='+str(iter))
            except: break
            try: 
                l += len(response.json())
                l1 = len(response.json())
            except: l = 0
            if l1<1000: break
            else:
                iter+=1
                posts[white_list[proc+int(multiprocessing.cpu_count()/2)*i]] += response.json()
        if l==0: pass
        else: posts[white_list[proc+int(multiprocessing.cpu_count()/2)*i]] += response.json()


#@tasks.loop(hours = 8.0)
async def auto_hentai_posts_update():
    #try: auto_hentai.cancel()
    #except: pass
    global posts
    manager = multiprocessing.Manager()
    posts = manager.dict()
    t1=datetime.datetime.now()
    print(str(datetime.datetime.now().strftime('%H:%M:%S'))+'\t'+'Bot start update rule34 posts')
    res_text = 'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&limit=1000&tags='
    global white_dict
    with open('./r34/white_list.json', 'r+') as wl_file:
        white_dict = json.load(wl_file)
    white_list = []
    for key in white_dict.keys():
        white_list.append(key)
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)

    if black_list:
        for tag in black_list:
            res_text+='-'+tag+' '  
    def processesed(procs, calc):
        processes = []
        for proc in range(procs):
            p = multiprocessing.Process(target=sequential, args=(calc, proc, posts, res_text, white_list))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
    n_proc = int(multiprocessing.cpu_count()/2)
    if len(white_list)%n_proc==0: calc=int(len(white_list)/n_proc)
    else: calc = int(len(white_list)/n_proc + 1)
    for tag in white_list:
        posts[tag]=list()
    print('Calculations: '+str(calc))
    processesed(n_proc, calc)
    l = 0
    for key, value in posts.items():
        if white_dict[key][0]!=len(value):
            white_dict[key][0] = len(value)
            print('Refresh: ', key)
        l+=len(value)
    with open('./r34/white_list.json', 'w+') as wl_file:
        json.dump(white_dict, wl_file)
    t2=datetime.datetime.now()
    print(str(datetime.datetime.now().strftime('%H:%M:%S'))+'\t'+'Bot end update rule34 posts')
    t3 = t2-t1
    print('Update time: '+str(t3))
    print('Total posts number: ' + str(l))
    try:
        await asyncio.sleep(1)
        auto_hentai.start()
    except:pass



@bot.command(pass_context=True, brief="[sec] Set rule34 auto send delay",description = "Set rule34 auto send delay;\naliases = r34_delay, auto_delay", aliases=['r34_delay','auto_delay'])
@commands.has_permissions(administrator=True)
async def delay(ctx, value):
    try: await ctx.message.delete()
    except: pass
    global idiots_list
    if ctx.message.author.id in idiots_list:
        return
    try: value = float(value)
    except: 
        await ctx.send('Incorrect value', delete_after = 3)
        return
    if value<1 or value>28800:
        await ctx.send('Incorrect value', delete_after = 3)
        return
    else:
        await ctx.send('Rule34 auto delay succesfully modified', delete_after = 3)
    with open('./auto_delay.json','w') as ad_file:
        json.dump(value, ad_file)
    global auto_delay
    auto_delay = value
    auto_hentai.cancel()
    await asyncio.sleep(1)
    auto_hentai.change_interval(seconds=auto_delay)
    auto_hentai.start()


@bot.slash_command(pass_context=True, description = 'Set rule34 auto send delay')
async def delay(ctx, value):
    try: value = float(value)
    except: 
        await ctx.respond('Incorrect value', delete_after = 3)
        return
    if value<1 or value>28800:
        await ctx.respond('Incorrect value', delete_after = 3)
        return
    else:
        await ctx.respond('Rule34 auto delay succesfully modified', delete_after = 3)
    with open('./auto_delay.json','w') as ad_file:
        json.dump(value, ad_file)
    global auto_delay
    auto_delay = value
    auto_hentai.cancel()
    await asyncio.sleep(1)
    auto_hentai.change_interval(seconds=auto_delay)
    auto_hentai.start()
    


@bot.event
async def on_ready():
    act = discord.Activity(name='в текстовые каналы', type=3)
    await bot.change_presence(status=discord.Status.online, activity=act)
    #try: auto_hentai_posts_update.start()
    #except: pass
    try: await auto_hentai_posts_update()
    except: pass


@bot.event
async def on_disconnect():
    print(datetime.datetime.now(), 'BOT WAS DISCONNECTED FROM DISCORD')


@bot.event
async def on_connect():
    print(datetime.datetime.now(), 'BOT WAS CONNECTED TO DISCORD')


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    guild = getattr(before.channel, 'guild', None)
    if guild is None:
        return
    voice = guild.voice_client
    if voice is None or not voice.is_connected():
        return
    if len(voice.channel.members) == 1:
        print('diconnect')
        global cur_info
        cur_info = ''
        global music_queue
        music_queue = []
        global info_queue
        info_queue = []
        await voice.disconnect()
        act = discord.Activity(name='в текстовые каналы', type=3)
        await bot.change_presence(status=discord.Status.online, activity=act)


@bot.event
async def on_message(message):
    if type(message.channel)==discord.DMChannel:
        if message.author==bot.user:
            return
        await message.author.send("I don't work here, baka")
        return
    now = datetime.datetime.now()
    str_date = str(now.year)+'#'+str(now.month)+'#'+str(now.day)+'.txt'
    filename = './logs/'+str(message.channel.name)+'/'+str_date
    print(str(now.strftime('%H:%M:%S'))+'\t'+str(message.channel.name)+ ': '+str(message.author.name) +' | ' + str(message.author.nick) +': ' + str(message.content))

    if os.path.exists(filename):
        with open(filename, 'a+', encoding='utf-8') as log_file:
            log_file.write('\n'+str(now.strftime('%H:%M:%S'))+'\t'+str(message.author.name) +' | ' + str(message.author.nick) +': ' + str(message.content))
            for a in message.attachments:
                log_file.write('\t'+str(a))
                print (a.url)
    else: 
        if os.path.exists('./logs/'+str(message.channel.name)): pass
        else: os.mkdir('./logs/'+str(message.channel.name))
        with open(filename, 'w+', encoding='utf-8') as log_file:
            log_file.write(str(now.strftime('%H:%M:%S'))+'\t'+str(message.author.name) +' | ' + str(message.author.nick) +': ' + str(message.content))
            for a in message.attachments:
                log_file.write('\t'+str(a))
                print (a.url)
    if message.author.bot: return
    with open('./messages/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    black_list = black_list.lower()
    full_message = message.content.lower()
    full_message = full_message.split()
    for msg in full_message:
        if msg in black_list:
            await message.delete()
            return
    await bot.process_commands(message)


@bot.event
async def on_message_edit(before, after):
    pass


@bot.event
async def on_message_delete(message):
    pass


@bot.event
async def on_bulk_message_delete(messages):
    pass


@bot.event
async def on_raw_reaction_add(payload):
    #print(payload.message_id, ' : ', payload.user_id, ' : ', payload.emoji)
    global posts
    global idiots_list
    if payload.user_id in idiots_list:
        return
    print(datetime.datetime.now(),'\t',payload.user_id, '\tAdd reaction: ', payload.emoji.name)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if not message.author.bot: return
    else: 
        url = message.content
        if 'https://api-cdn.rule34.xxx/images/' not in url: return
        else:
            for author in posts:
                for post in posts[author]:
                    if post['file_url']==url:
                        print(author)
                        if payload.emoji.name == 'SSS':
                            delta = 20
                        elif payload.emoji.name == 'SS':
                            delta = 15
                        elif payload.emoji.name == 'S_':
                            delta = 10
                        elif payload.emoji.name == 'A_':
                            delta = 5
                        elif payload.emoji.name == 'B_':
                            delta = 2
                        elif payload.emoji.name == 'C_':
                            delta = 0
                        elif payload.emoji.name == 'D_':
                            delta = -5
                        elif payload.emoji.name == 'E_':
                            delta = -10
                        elif payload.emoji.name == 'F_':
                            delta = -20
                        else: delta = 0
                        with open('./r34/white_list.json', 'r+') as wl_file:
                            white_dict = json.load(wl_file)
                        white_dict[author][1]+=delta
                        with open('./r34/white_list.json', 'w+') as wl_file:
                            json.dump(white_dict, wl_file)
                        break

            
@bot.event
async def on_raw_reaction_remove(payload):
    global posts
    global idiots_list
    if payload.user_id in idiots_list:
        return
    print(datetime.datetime.now(),'\t',payload.user_id, '\tRemove reaction: ', payload.emoji.name)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if not message.author.bot: return
    else: 
        url = message.content
        if 'https://api-cdn.rule34.xxx/images/' not in url: return
        else:
            for author in posts:
                for post in posts[author]:
                    if post['file_url']==url:
                        print(author)
                        if payload.emoji.name == 'SSS':
                            delta = -20
                        elif payload.emoji.name == 'SS':
                            delta = -15
                        elif payload.emoji.name == 'S_':
                            delta = -10
                        elif payload.emoji.name == 'A_':
                            delta = -5
                        elif payload.emoji.name == 'B_':
                            delta = -2
                        elif payload.emoji.name == 'C_':
                            delta = 0
                        elif payload.emoji.name == 'D_':
                            delta = 5
                        elif payload.emoji.name == 'E_':
                            delta = 10
                        elif payload.emoji.name == 'F_':
                            delta = 20
                        else: delta = 0
                        with open('./r34/white_list.json', 'r+') as wl_file:
                            white_dict = json.load(wl_file)
                        white_dict[author][1]+=delta
                        with open('./r34/white_list.json', 'w+') as wl_file:
                            json.dump(white_dict, wl_file)
                        break
        



async def preparation(ctx, voice, channel):
    if len(music_queue)>0:
        await ctx.send("Music added to queue", delete_after = 3)
    else:
        if not channel:
            await ctx.send("You are not connected to a voice channel", delete_after = 3)
            return
        if voice and voice.is_connected():
            pass
        else:
            voice = await channel.connect()
            await ctx.send(f"Joined {channel}", delete_after = 3)
            await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{channel}'))
        if voice.is_playing()==False: await ctx.send("Getting everything ready, playing audio soon", delete_after = 3)
        else: await ctx.send("Music added to queue", delete_after = 3)
        print("Someone wants to play music let me get that ready for them...")
    return voice


async def loop_change(interaction):
    global loop_mode
    global loop_message
    if loop_mode == False: 
        loop_button = Button(custom_id='button1', label='Loop mode enabled', style=discord.ButtonStyle.green)
        loop_mode = True
        with open('./loop_mode.json','w') as lm_file:
            json.dump(loop_mode, lm_file)
    elif loop_mode == True: 
        loop_button = Button(custom_id='button1', label='Loop mode disabled', style=discord.ButtonStyle.red)
        loop_mode = False
        with open('./loop_mode.json','w') as lm_file:
            json.dump(loop_mode, lm_file)
    if pause_mode == True:
        pause_button = Button(custom_id='button2', label = '►', style=discord.ButtonStyle.green)
    else:
        pause_button = Button(custom_id='button2', label = '▌▌', style=discord.ButtonStyle.green)
    voice = get(bot.voice_clients)
    if voice and voice.is_playing():
        if music_queue:
            if music_queue[-1]!=source:
                info_queue.append(cur_info)
                music_queue.append(source)
        elif not music_queue:
            info_queue.append(cur_info)
            music_queue.append(source)
    back_button = Button(custom_id='button3', label = '◄◄', style=discord.ButtonStyle.green)
    forward_button = Button(custom_id='button4', label = '►►', style=discord.ButtonStyle.green)
    stop_button = Button(custom_id='button5', label = '▇', style=discord.ButtonStyle.green)
    stop_button.callback = stop_b
    back_button.callback = back
    forward_button.callback = forward
    loop_button.callback = loop_change
    pause_button.callback = pause_change
    await interaction.response.edit_message(view=View(loop_button,back_button, pause_button, stop_button, forward_button))


async def pause_change(interaction):
    global pause_mode
    voice = get(bot.voice_clients)
    if loop_mode == True: 
        loop_button = Button(custom_id='button1', label='Loop mode enabled', style=discord.ButtonStyle.green)
    else:
        loop_button = Button(custom_id='button1', label='Loop mode disabled', style=discord.ButtonStyle.red)
    if pause_mode == True:
        pause_mode = False
        pause_button = Button(custom_id='button2', label = '▌▌', style=discord.ButtonStyle.green)
        voice.resume()
    else:
        pause_mode = True
        pause_button = Button(custom_id='button2', label = '►', style=discord.ButtonStyle.green)
        voice.pause()
    back_button = Button(custom_id='button3', label = '◄◄', style=discord.ButtonStyle.green)
    forward_button = Button(custom_id='button4', label = '►►', style=discord.ButtonStyle.green)
    stop_button = Button(custom_id='button5', label = '▇', style=discord.ButtonStyle.green)
    stop_button.callback = stop_b
    back_button.callback = back
    forward_button.callback = forward
    pause_button.callback = pause_change
    loop_button.callback = loop_change
    await interaction.response.edit_message(view=View(loop_button,back_button, pause_button, stop_button, forward_button))


async def forward(interaction):
    voice = get(bot.voice_clients)
    voice.stop()
    if voice.is_playing() == True: play_next(interaction)

async def back(interaction):
    count = len(music_queue)-1
    if loop_mode == True:
        while count>1:
            music_queue.append(music_queue.pop(0))
            info_queue.append(info_queue.pop(0))
            count-=1
    else:
        while count>1:
            music_queue.pop(0)
            info_queue.pop(0)
            count-=1
    voice = get(bot.voice_clients)
    voice.stop()
    if voice.is_playing() == True: play_next(interaction)


async def stop_b(interaction):
    voice = get(bot.voice_clients)
    global cur_info
    cur_info = ''
    global music_queue
    music_queue = []
    global info_queue
    info_queue = []
    voice.stop()


async def send_message(ctx, cur_info):
    global cur_message
    cur_message = await ctx.send(cur_info)
    global loop_message
    global pause_mode
    if loop_mode == True: 
        loop_button = Button(custom_id='button1', label='Loop mode enabled', style=discord.ButtonStyle.green)
    else:
        loop_button = Button(custom_id='button1', label='Loop mode disabled', style=discord.ButtonStyle.red)
    if pause_mode == True:
        pause_button = Button(custom_id='button2', label = '►', style=discord.ButtonStyle.green)
    else:
        pause_button = Button(custom_id='button2', label = '▌▌', style=discord.ButtonStyle.green)
    back_button = Button(custom_id='button3', label = '◄◄', style=discord.ButtonStyle.green)
    forward_button = Button(custom_id='button4', label = '►►', style=discord.ButtonStyle.green)
    stop_button = Button(custom_id='button5', label = '▇', style=discord.ButtonStyle.green)
    stop_button.callback = stop_b
    back_button.callback = back
    forward_button.callback = forward
    pause_button.callback = pause_change
    loop_button.callback = loop_change
    loop_message = await ctx.send(view=View(loop_button,back_button, pause_button, stop_button, forward_button))
    global skip_message
    await skip_menu(ctx)
    


async def check_voice(ctx, voice, last = False):
    res = True
    if len(music_queue)==0 and last == True:
        try:
            msg = await ctx.channel.fetch_message(cur_message.id)
            await msg.delete()
            loop_msg = await ctx.channel.fetch_message(loop_message.id)
            await loop_msg.delete()
            skip_msg = await ctx.channel.fetch_message(skip_message.id)
            await skip_msg.delete()
        except: pass
        return
    if voice.is_playing() == True: 
        members = ctx.guild.members
        if len(members) == 1:
            await leave(ctx)
            await ctx.send('Failed to find users in the channel\nIf you are on a voice channel, please re-enter', delete_after = 10)
            res = False
    if res == True: 
        try:
            msg = await ctx.channel.fetch_message(cur_message.id)
            await msg.delete()
            loop_msg = await ctx.channel.fetch_message(loop_message.id)
            await loop_msg.delete()
            skip_msg = await ctx.channel.fetch_message(skip_message.id)
            await skip_msg.delete()
        except: pass
        await send_message(ctx,cur_info)

def play_next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if len(music_queue)>0:
        global source
        try: source = music_queue.pop(0)
        except: pass
        global cur_info
        try: cur_info = info_queue.pop(0)
        except: cur_info = ''
        if loop_mode == True: 
            music_queue.append(source)
            info_queue.append(cur_info)
        try:
            voice.play(discord.FFmpegPCMAudio(source = source), after = lambda e: play_next(ctx)) 
            asyncio.run_coroutine_threadsafe(check_voice(ctx, voice), bot.loop)
        except: pass
    else: asyncio.run_coroutine_threadsafe(check_voice(ctx, voice, True), bot.loop)


@bot.command(pass_context=True, brief="[N] - Clear [N] message from channel", description = "Clear [N](default 100) message from channel;\naliases = clr", aliases=['clr'])
@commands.has_permissions(administrator=True)
async def clear(ctx, amount = 100):
    try: await ctx.message.delete()
    except: pass
    try: value = int(amount)
    except: 
        await ctx.send('Incorrect value', delete_after = 3)
        return
    if value<1:
        await ctx.send('Incorrect value', delete_after = 3)
        return
    else:
        try: 
            await ctx.channel.purge(limit = value)
            await ctx.send('Success', delete_after = 3)
        except: await ctx.send('Something went wrong', delete_after = 3)


@bot.slash_command(pass_context=True, description = 'Clear [N] messages from channel')
async def clear(ctx, amount:int):
    if amount<1:
        await ctx.respond('Incorrect value', delete_after = 3)
        return
    else:
        try: 
            await ctx.channel.purge(limit = amount)
            await ctx.respond('Success', delete_after = 3)
        except: await ctx.respond('Something went wrong', delete_after = 3)


@bot.command(pass_context=True, brief="Show random meme",description = "Show random meme", aliases=[])
async def meme(ctx):
    try: await ctx.message.delete()
    except: pass
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    await ctx.send(json_data['image'])


@bot.slash_command(pass_context=True, description = 'Show random meme')
async def meme(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    await ctx.send(json_data['image'])
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="Show random wink anime gif",description = "Show random wink anime gif", aliases=[])
async def wink(ctx): 
    try: await ctx.message.delete()
    except: pass
    response = requests.get('https://some-random-api.ml/animu/wink')
    json_data = json.loads(response.text)
    await ctx.send(json_data['link'])


@bot.slash_command(pass_context=True, description = 'Show random wink anime gif')
async def wink(ctx):
    response = requests.get('https://some-random-api.ml/animu/wink')
    json_data = json.loads(response.text)
    await ctx.send(json_data['link'])
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="Show random pet anime gif",description = "Show random pet anime gif", aliases=[])
async def pet(ctx): 
    try: await ctx.message.delete()
    except: pass
    response = requests.get('https://some-random-api.ml/animu/pat')
    json_data = json.loads(response.text)
    await ctx.send(json_data['link'])


@bot.slash_command(pass_context=True, description = 'Show random pet anime gif')
async def pet(ctx):
    response = requests.get('https://some-random-api.ml/animu/pat')
    json_data = json.loads(response.text)
    await ctx.send(json_data['link'])
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="Show random hug anime gif",description = "Show random hug anime gif", aliases=[])
async def hug(ctx):
    try: await ctx.message.delete()
    except: pass 
    response = requests.get('https://some-random-api.ml/animu/hug')
    json_data = json.loads(response.text)
    await ctx.send(json_data['link'])


@bot.slash_command(pass_context=True, description = 'Show random hug anime gif')
async def hug(ctx):
    response = requests.get('https://some-random-api.ml/animu/hug')
    json_data = json.loads(response.text)
    await ctx.send(json_data['link'])
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="What is this?",description = "What is this?;\naliases = ", aliases=['trap','трап'])
async def what(ctx):
    try: await ctx.message.delete()
    except: pass
    res_text = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=1000&tags=trap%20-disney%20-cartoon_network%20-troll%20-no_humans'
    response = requests.get(res_text)
    posts = response.json()
    l = len(posts)
    number = random.randint(0,l-1)
    await ctx.send('https://safebooru.org//images/'+str(posts[number]['directory'])+'/'+str(posts[number]['image']))



@bot.command(pass_context=True, brief="[tag] - Show random image from rule34 by [tag]",description = "Show random image from rule34 by [tag];\naliases = 34, r34, hentai", aliases=['r34','34','hentai'])
@commands.has_permissions(administrator=True)
async def rule34(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    res_text = 'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&limit=1000&tags='
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    if not tags:
        global posts
        global white_dict
        location = []
        prev = 0
        author=''
        for value in white_dict.values():
            if value[0]+value[1]>0: 
                prev = prev+value[0]+value[1]
            location.append(prev)
        max = location[-1]
        r = random.randint(0,max-1)
        c = 0
        for key in white_dict.keys():
            if r>=location[c]:
                c+=1
            else: 
                author = key
                l = len(posts[author])
                number = random.randint(0,l-1)
                await ctx.send(posts[author][number]['file_url'])
                return
    else:
        for tag in tags:
            res_text+=tag+'%20'
        for tag in black_list:
            res_text+='-'+tag+'%20'
        response = requests.get(res_text)
        try: posts1 = response.json()
        except: posts1 = []
        try: l = len(posts1)
        except: l = 0
        if l == 0:
            await ctx.send("Can't find any picture", delete_after = 3)
            return
        number = random.randint(0,l-1)
        await ctx.send(posts1[number]['file_url'])

@bot.command(pass_context=True, brief="view rule34 tag blacklist",description = "view rule34 tag blacklist;\naliases = 34_bl, r34_bl, hentai_bl", aliases=['r34_bl','34_bl','hentai_bl'])
@commands.has_permissions(administrator=True)
async def rule34_blacklist(ctx):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    i=1
    msg=''
    for tag in black_list:
        msg+=str(i)+'. '+tag
        i+=1
        if len(msg)>1300: 
            await ctx.send(msg, delete_after=60)
            msg=''
    await ctx.send(msg, delete_after = 60)


@bot.command(pass_context=True, brief="[tag] - add rule34 [tag] to blacklist",description = "[tag] - add rule34 [tag] to blacklist;\naliases = 34_bla, r34_bla, hentai_bla", aliases=['r34_bla','34_bla','hentai_bla'])
@commands.has_permissions(administrator=True)
async def rule34_blacklist_add(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    black_list = set(black_list)
    if tags:
        for tag in tags:
            black_list.add(tag)
        black_list = list(black_list)
        with open('./r34/black_list.json','w+') as bl_file:
            json.dump(black_list, bl_file)
        await ctx.send('Tags succesfully added to blacklist', delete_after = 3)
    else: await ctx.send('Tags not found', delete_after = 3)

@bot.command(pass_context=True, brief="[tag] - remove rule34 [tag] from blacklist",description = "[tag] - remove rule34 [tag] from blacklist;\naliases = 34_blr, r34_blr, hentai_blr", aliases=['r34_blr','34_blr','hentai_blr'])
@commands.has_permissions(administrator=True)
async def rule34_blacklist_remove(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    if tags:
        for tag in tags:
            if tag in black_list: black_list.remove(tag)
        with open('./r34/black_list.json','w+') as bl_file:
            json.dump(black_list, bl_file)
        await ctx.send('Tags succesfully removed from blacklist', delete_after = 3)
    else: await ctx.send('Tags not found', delete_after = 3)

@bot.command(pass_context=True, brief="view rule34 tag whitelist",description = "view rule34 tag whitelist;\naliases = 34_wl, r34_wl, hentai_wl", aliases=['r34_wl','34_wl','hentai_wl'])
@commands.has_permissions(administrator=True)
async def rule34_whitelist(ctx):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/white_list.json', 'r+') as wl_file:
        white_list = json.load(wl_file)
    i=1
    msg=''
    for tag in white_list.keys():
        msg+=str(i)+'. '+tag
        i+=1
        if len(msg)>1300: 
            await ctx.send(msg, delete_after=60)
            msg=''
    await ctx.send(msg, delete_after = 60)


@bot.command(pass_context=True, brief="[tag] - add rule34 [tag] to whitelist",description = "[tag] - add rule34 [tag] to whitelist;\naliases = 34_wla, r34_wla, hentai_wla", aliases=['r34_wla','34_wla','hentai_wla'])
@commands.has_permissions(administrator=True)
async def rule34_whitelist_add(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/white_list.json', 'r+') as wl_file:
        white_list = json.load(wl_file)
    if tags:
        for tag in tags:
            if tag not in white_list.keys():
                white_list[tag]=[0,0]
        with open('./r34/white_list.json','w+') as wl_file:
            json.dump(white_list, wl_file)
        await ctx.send('Tags succesfully added to whitelist', delete_after = 3)
    else: await ctx.send('Tags not found', delete_after = 3)


@bot.command(pass_context=True, brief="[tag] - remove rule34 [tag] from whitelist",description = "[tag] - remove rule34 [tag] from whitelist;\naliases = 34_wlr, r34_wlr, hentai_wlr", aliases=['r34_wlr','34_wlr','hentai_wlr'])
@commands.has_permissions(administrator=True)
async def rule34_whitelist_remove(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/white_list.json', 'r+') as wl_file:
        white_list = json.load(wl_file)
    if tags:
        for tag in tags:
            if tag in white_list.keys(): white_list.pop(tag)
        with open('./r34/white_list.json','w+') as wl_file:
            json.dump(white_list, wl_file)
        await ctx.send('Tags succesfully removed from whitelist', delete_after = 3)
    else: await ctx.send('Tags not found', delete_after = 3)


@bot.command(pass_context=True, brief="Bot join to your channel",description = "Bot join to your channel;\naliases = j, jo", aliases=['j', 'jo'])
async def join(ctx):
    try: await ctx.message.delete()
    except: pass
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel", delete_after = 3)
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.send(f"Joined {channel}", delete_after = 3)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{channel}'))


@bot.slash_command(pass_context=True, description = 'Bot join to your channel')
async def join(ctx):
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.respond("You are not connected to a voice channel", delete_after = 3)
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.respond('Success', delete_after = 3)
    await ctx.send(f"Joined {channel}", delete_after = 3)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{channel}'))
    


@bot.command(pass_context=True, brief="(url) - Play a song by (url)",description = "Play a song by (url);\naliases = p, pl", aliases=['pl', 'p'])
async def play(ctx, url: str):
    try: await ctx.message.delete()
    except: pass
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice = await preparation(ctx, voice, channel)

    if voice.is_playing() == False:
        for file in natsorted(os.listdir("./music/")):
            if file.endswith(".webm"):
                os.remove('./music/'+file)
    url = url.rsplit('&')[0]
    videosSearch = VideosSearch(url, limit = 1)
    def fname_gen(i):
        fname = './music/'+str(i)+'.webm'
        if os.path.isfile(fname) == False: return fname
        else: return fname_gen(i+1)
    fname = fname_gen(1)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': fname
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    music_queue.append(fname)
    res = videosSearch.result()['result'][0]
    playing_string = "Now playing: "+  str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_queue.append(playing_string)
    if voice.is_playing() == False: play_next(ctx)
    else: 
        global skip_message
        await skip_message.delete()
        await skip_menu(ctx)


@bot.command(pass_context=True, brief="Bot leave channel",description = "Bot leave channel;\naliases = l, le, lea", aliases=['l', 'le', 'lea'])
async def leave(ctx):
    try: await ctx.message.delete()
    except: pass
    try: channel = ctx.message.author.voice.channel
    except: channel = 'channel'
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        global cur_info
        cur_info = ''
        global music_queue
        music_queue = []
        global info_queue
        info_queue = []
        await voice.disconnect()
        await ctx.send(f"Left {channel}", delete_after = 3)
        act = discord.Activity(name='в текстовые каналы', type=3)
        await bot.change_presence(status=discord.Status.online, activity=act)
    else:
        await ctx.send("Don't think I am in a voice channel", delete_after = 3)

@bot.command(pass_context=True, brief="Stop the music",description = "Stop the music;\naliases = s, st, break", aliases=['s', 'st', 'break'])
async def stop(ctx):
    try: await ctx.message.delete()
    except: pass
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        global cur_info
        cur_info = ''
        global music_queue
        music_queue = []
        global info_queue
        info_queue = []
        await ctx.send('Music Stopped', delete_after = 3)
        voice.stop()
    else:
        await ctx.send("Don't think I am in a voice channel", delete_after = 3)

@bot.command(pass_context=True, brief="Pause the music",description = "Pause the music;\naliases = pau, hold", aliases=['pau','hold'])
async def pause(ctx):
    try: await ctx.message.delete()
    except: pass
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await ctx.send('Music Paused', delete_after = 3)
        voice.pause()
    else:
        await ctx.send("Don't think I am in a voice channel", delete_after = 3)

@bot.command(pass_context=True, brief="Resume the music",description = "Resume the music;\naliases = r, res, continue", aliases=['r', 'res', 'continue'])
async def resume(ctx):
    try: await ctx.message.delete()
    except: pass
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await ctx.send('Music Resumed', delete_after = 3)
        voice.resume()
    else:
        await ctx.send("Don't think I am in a voice channel", delete_after = 3)

@bot.command(pass_context=True, brief="(song name) - Bot plays the first found music",description = "Bot plays the first found music;\naliases = pf, sf, playf", aliases=['sf', 'pf', 'playf'])
async def playfirst(ctx, *args):
    try: await ctx.message.delete()
    except: pass
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice = await preparation(ctx, voice, channel)

    if voice.is_playing() == False: 
        for file in natsorted(os.listdir("./music/")):
            if file.endswith(".webm"):
                os.remove('./music/'+file)
    message = ''
    for arg in args:
        message+=str(arg)+' '
    videosSearch = VideosSearch(message, limit = 1)
    url = videosSearch.result()['result'][0]['link']
    
    def fname_gen(i):
        fname = './music/'+str(i)+'.webm'
        if os.path.isfile(fname) == False: return fname
        else: return fname_gen(i+1)
    fname = fname_gen(1)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': fname
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except:
        await ctx.send("Can't download song", delete_after = 3)
        return
    music_queue.append(fname)
    res = videosSearch.result()['result'][0]
    playing_string = "Now playing: "+  str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_queue.append(playing_string)
    if voice.is_playing() == False: play_next(ctx)
    else: 
        global skip_message
        await skip_message.delete()
        await skip_menu(ctx)


@bot.command(pass_context=True, brief="Skip current song",description = "Skip current song;\naliases = pass", aliases=['pass'])
async def skip(ctx, count = '1'):
    try: await ctx.message.delete()
    except: pass
    if count == 'all':
        count = len(music_queue)+1
    try: count = int(count)
    except: 
        await ctx.send('Wrong argument',delete_after = 3)
        return
    c1 = count
    if loop_mode==True:
        while count>1:
            music_queue.append(music_queue.pop(0))
            info_queue.append(info_queue.pop(0))
            count-=1
    elif loop_mode==False:
        if count>len(music_queue)+1:
            count = len(music_queue)+1
            c1 = count
        while count>1:
            music_queue.pop(0)
            info_queue.pop(0)
            count-=1
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    if voice.is_playing() == True: play_next(ctx)
    await ctx.send('Music Skipped ' + str(c1) + ' times', delete_after = 3)


@bot.slash_command(pass_context=True, description = 'Skip current song')
async def skip(ctx, count:str):
    if count == 'all':
        count = len(music_queue)+1
    try: count = int(count)
    except: 
        await ctx.send('Wrong argument',delete_after = 3)
        return
    c1 = count
    if loop_mode==True:
        while count>1:
            music_queue.append(music_queue.pop(0))
            info_queue.append(info_queue.pop(0))
            count-=1
    elif loop_mode==False:
        if count>len(music_queue)+1:
            count = len(music_queue)+1
            c1 = count
        while count>1:
            music_queue.pop(0)
            info_queue.pop(0)
            count-=1
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    if voice.is_playing() == True: play_next(ctx)
    await ctx.send('Music Skipped ' + str(c1) + ' times', delete_after = 3)
    await ctx.respond('Success', delete_after = 3)



async def skip_menu(ctx):
    global skip_message
    opt = []
    opt.append(discord.SelectOption(label = '1.'+cur_info.split('Now playing: ')[1].split(';')[0][:97], description='; '.join(cur_info.split('Now playing: ')[1].split('\n')[0].split(';')[-2:])[:99], default = True))
    i=2
    for song in info_queue:
        opt.append(discord.SelectOption(label = str(i)+'.'+song.split('Now playing: ')[1].split(';')[0][:97], description='; '.join(song.split('Now playing: ')[1].split('\n')[0].split(';')[-2:])[:99]))
        i+=1
        if i>25: break
    select = discord.ui.Select(
        placeholder='Choose',
        options =opt
    )
    async def my_callback(interaction):
        await skip(ctx, int(select.values[0].split('.')[0])-1)
    select.callback = my_callback
    view = View()
    view.add_item(select)
    skip_message = await ctx.send(view=view)


@bot.command(pass_context=True, brief="Delete current song from queue",description = "Delete current song from queue;\naliases = q_del, del", aliases=['q_del','del'])
async def delete(ctx, number = '1'):
    try: await ctx.message.delete()
    except: pass
    try: number = int(number)
    except: number=1
    if number>len(info_queue)+1 or number<1:
        await ctx.send('The number is out of range', delete_after = 3)
        return
    if number==1:
        if loop_mode == True:
            music_queue.pop(-1)
            info_queue.pop(-1)
        await skip(ctx)
    else:
        music_queue.pop(number-2)
        info_queue.pop(number-2)
    await ctx.send('The song deleted successfully', delete_after=3)


@bot.slash_command(pass_context=True, description = 'Delete current song from queue')
async def delete(ctx, number:int):
    if number>len(info_queue)+1 or number<1:
        await ctx.send('The number is out of range', delete_after = 3)
        return
    if number==1:
        if loop_mode == True:
            music_queue.pop(-1)
            info_queue.pop(-1)
        await skip(ctx)
    else:
        music_queue.pop(number-2)
        info_queue.pop(number-2)
    await ctx.send('The song deleted successfully', delete_after=3)
    await ctx.respond('Success', delete_after = 3)



@bot.command(pass_context=True, brief="Output current song",description = "Output current song;\naliases = ?", aliases=['?'])
async def now(ctx):
    try: await ctx.message.delete()
    except: pass
    try: await ctx.send(cur_info, delete_after = 60)
    except: await ctx.send('Music is not playing', delete_after = 3)


@bot.slash_command(pass_context=True, description = 'Output current song')
async def now(ctx, playlistname:str):
    try: await ctx.send(cur_info, delete_after = 60)
    except: await ctx.send('Music is not playing', delete_after = 3)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="Enable/Disable loop mode",description = "Enable/Disable loop mode;\naliases = cycle", aliases=['cycle'])
async def loop(ctx):
    global loop_mode
    global loop_message
    try: await ctx.message.delete()
    except: pass
    if loop_mode == True: 
        loop_mode = False
        with open('./loop_mode.json','w') as lm_file:
            json.dump(loop_mode, lm_file)
        button = Button(custom_id='button1', label='Loop mode disabled', style=discord.ButtonStyle.red)
    elif loop_mode == False: 
        loop_mode = True
        with open('./loop_mode.json','w') as lm_file:
            json.dump(loop_mode, lm_file)
        button = Button(custom_id='button1', label='Loop mode enabled', style=discord.ButtonStyle.green)
    button.callback = loop_change
    try: await loop_message.edit(view=View(button))
    except: pass
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        if music_queue:
            if music_queue[-1]!=source:
                info_queue.append(cur_info)
                music_queue.append(source)
        elif not music_queue:
            info_queue.append(cur_info)
            music_queue.append(source)


@bot.slash_command(pass_context=True, description = 'Enable/Disable loop mode')
async def loop(ctx):
    global loop_mode
    global loop_message
    if loop_mode == True: 
        loop_mode = False
        with open('./loop_mode.json','w') as lm_file:
            json.dump(loop_mode, lm_file)
        button = Button(custom_id='button1', label='Loop mode disabled', style=discord.ButtonStyle.red)
    elif loop_mode == False: 
        loop_mode = True
        with open('./loop_mode.json','w') as lm_file:
            json.dump(loop_mode, lm_file)
        button = Button(custom_id='button1', label='Loop mode enabled', style=discord.ButtonStyle.green)
    button.callback = loop_change
    try: await loop_message.edit(view=View(button))
    except: pass
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        if music_queue:
            if music_queue[-1]!=source:
                info_queue.append(cur_info)
                music_queue.append(source)
        elif not music_queue:
            info_queue.append(cur_info)
            music_queue.append(source)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="(name) - Create playlist named (name)",description = "Create playlist named (name);\naliases = pl_create, create_playlist", aliases=['pl_create','create_playlist'])
@commands.has_permissions(administrator=True)
async def playlist_create(ctx, playlistname):
    try: await ctx.message.delete()
    except: pass
    if os.path.exists('./playlists/'+str(playlistname)):
        await ctx.send('A playlist with the same name already exists', delete_after = 3)
    else:
        try: 
            os.mkdir('./playlists/'+str(playlistname))
            await ctx.send('Playlist created successfully', delete_after = 3)
        except:
            await ctx.send('Failed to create playlist', delete_after = 3)


@bot.slash_command(pass_context=True, description = 'Create playlist named (name)')
async def playlist_create(ctx, playlistname:str):
    if os.path.exists('./playlists/'+str(playlistname)):
        await ctx.send('A playlist with the same name already exists', delete_after = 3)
    else:
        try: 
            os.mkdir('./playlists/'+str(playlistname))
            await ctx.send('Playlist created successfully', delete_after = 3)
        except:
            await ctx.send('Failed to create playlist', delete_after = 3)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="Show playlists",description = "Show playlists;\naliases = pls, pl_list", aliases=['pls','pl_list'])
async def playlists(ctx):
    try: await ctx.message.delete()
    except: pass
    dirname = './playlists'
    dirs = natsorted(os.listdir(dirname))
    out_string = 'Current playlist count: ' + str(len(dirs))
    for dir in dirs:
        out_string+='\n'+str(dir)
    await ctx.send(out_string, delete_after = 60)


@bot.slash_command(pass_context=True, description = 'Show playlists')
async def playlists(ctx):
    dirname = './playlists'
    dirs = natsorted(os.listdir(dirname))
    out_string = 'Current playlist count: ' + str(len(dirs))
    for dir in dirs:
        out_string+='\n'+str(dir)
    await ctx.send(out_string, delete_after = 60)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="(name) (url) - Add song by (url) to playlist",description = "Add song by (url) to playlist named (name);\naliases = pl_add", aliases=['pl_add'])
@commands.has_permissions(administrator=True)
async def playlist_add(ctx, playlist, url):
    try: await ctx.message.delete()
    except: pass
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    url = url.rsplit('&')[0]
    videosSearch = VideosSearch(url, limit = 1)
    def fname_gen(i):
        fname = './playlists/'+str(playlist)+'/'+str(i)+'.webm'
        fname1 = './playlists/'+str(playlist)+'/'+str(i)+'.info'
        if os.path.isfile(fname) == False: return [fname, fname1]
        else: return fname_gen(i+1)
    fnames = fname_gen(1)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': fnames[0]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    res = videosSearch.result()['result'][0]
    playing_string = str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_file = open(fnames[1], 'w+', encoding="utf-8")
    info_file.write(playing_string)
    info_file.close()


@bot.slash_command(pass_context=True, description = 'Add song by (url) to playlist')
async def playlist_add(ctx, playlist:str, url:str):
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    url = url.rsplit('&')[0]
    videosSearch = VideosSearch(url, limit = 1)
    def fname_gen(i):
        fname = './playlists/'+str(playlist)+'/'+str(i)+'.webm'
        fname1 = './playlists/'+str(playlist)+'/'+str(i)+'.info'
        if os.path.isfile(fname) == False: return [fname, fname1]
        else: return fname_gen(i+1)
    fnames = fname_gen(1)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': fnames[0]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    res = videosSearch.result()['result'][0]
    playing_string = str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_file = open(fnames[1], 'w+', encoding="utf-8")
    info_file.write(playing_string)
    info_file.close()
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="(playlist) (number) - Remove song from playlist",description = "Remove song by (number) from playlist named (playlist);\naliases = pl_rm_s", aliases=['pl_rm_s'])
@commands.has_permissions(administrator=True)
async def playlist_remove_song(ctx, playlist, number):
    try: await ctx.message.delete()
    except: pass
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    filename = './playlists/'+str(playlist) + '/'+str(number) + '.webm'
    filename1 = './playlists/'+str(playlist) + '/'+str(number) + '.info'
    if os.path.isfile(filename): os.remove(filename)
    if os.path.isfile(filename1):os.remove(filename1)
    for file in natsorted(os.listdir('./playlists/'+str(playlist))):
        filename = file.rsplit('.')[0]
        fileext = file.rsplit('.')[1]
        if int(filename)>int(number):
            os.rename('./playlists/'+str(playlist)+'/'+filename+'.'+fileext, './playlists/'+str(playlist)+'/'+str(int(filename)-1)+'.'+fileext)


@bot.slash_command(pass_context=True, description = 'Remove song from playlist')
async def playlist_remove_song(ctx, playlist:str, number:int):
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    filename = './playlists/'+str(playlist) + '/'+str(number) + '.webm'
    filename1 = './playlists/'+str(playlist) + '/'+str(number) + '.info'
    if os.path.isfile(filename): os.remove(filename)
    if os.path.isfile(filename1):os.remove(filename1)
    for file in natsorted(os.listdir('./playlists/'+str(playlist))):
        filename = file.rsplit('.')[0]
        fileext = file.rsplit('.')[1]
        if int(filename)>int(number):
            os.rename('./playlists/'+str(playlist)+'/'+filename+'.'+fileext, './playlists/'+str(playlist)+'/'+str(int(filename)-1)+'.'+fileext)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="(name) - Show info about playlist named (name)",description = "Show info about playlist named (name);\naliases = pl_i, pl_info", aliases=['pl_i','pl_info'])
async def playlist_info(ctx, playlist, arg = 'not'):
    try: await ctx.message.delete()
    except: pass
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    out_string =''
    info = ''
    for file in natsorted(os.listdir('./playlists/'+str(playlist))):
        if file.endswith(".info"):
            with open('./playlists/'+str(playlist)+'/'+file,'r', encoding="utf-8") as file:
                fname = os.path.splitext(file.name)[0].rsplit('/')[-1]
                if arg == 'all' or arg == 'full': 
                    out_string = fname +'. ' + file.read()
                    await ctx.send(out_string, delete_after = 60)
                else: 
                    out_string = fname +'. ' + file.read().split('\n')[0]
                    info+=out_string+'\n'
                    if len(info)>1300: 
                        await ctx.send(info, delete_after = 60)
                        info = ''
    if arg!='all' and arg!='full':
        try: await ctx.send(info,delete_after = 60)
        except: pass


@bot.slash_command(pass_context=True, description = 'Show info about playlist named')
async def playlist_info(ctx, playlist:str, arg = 'not'):
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    out_string =''
    info = ''
    for file in natsorted(os.listdir('./playlists/'+str(playlist))):
        if file.endswith(".info"):
            with open('./playlists/'+str(playlist)+'/'+file,'r', encoding="utf-8") as file:
                fname = os.path.splitext(file.name)[0].rsplit('/')[-1]
                if arg == 'all' or arg == 'full': 
                    out_string = fname +'. ' + file.read()
                    await ctx.send(out_string, delete_after = 60)
                else: 
                    out_string = fname +'. ' + file.read().split('\n')[0]
                    info+=out_string+'\n'
                    if len(info)>1300: 
                        await ctx.send(info, delete_after = 60)
                        info = ''
    if arg!='all' and arg!='full':
        try: await ctx.send(info,delete_after = 60)
        except: pass
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="(name) - Move playlist named (name) to queue",description = "Move playlist named (name) to queue;\naliases = pl_p", aliases=['pl_p'])
async def playlist_play(ctx, playlist):
    try: await ctx.message.delete()
    except: pass
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice = await preparation(ctx, voice, channel)
    
    dir = './playlists/'+playlist+'/'
    files = natsorted(os.listdir(dir))
    for file in files:
        if file.endswith('.info'):
            with open(dir+file,'r', encoding="utf-8") as f:
                playing_string = 'Now playing: '+f.read()
                info_queue.append(playing_string)
        elif file.endswith('.webm'):
            music_queue.append(dir+str(file))
    if voice.is_playing() == False: play_next(ctx)
    else: 
        global skip_message
        await skip_message.delete()
        await skip_menu(ctx)


@bot.slash_command(pass_context=True, description = 'Move playlist named (name) to queue')
async def playlist_play(ctx, playlist:str):
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice = await preparation(ctx, voice, channel)
    
    dir = './playlists/'+playlist+'/'
    files = natsorted(os.listdir(dir))
    for file in files:
        if file.endswith('.info'):
            with open(dir+file,'r', encoding="utf-8") as f:
                playing_string = 'Now playing: '+f.read()
                info_queue.append(playing_string)
        elif file.endswith('.webm'):
            music_queue.append(dir+str(file))
    if voice.is_playing() == False: play_next(ctx)
    else: 
        global skip_message
        await skip_message.delete()
        await skip_menu(ctx)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="[all] Displays current songs in queue",description = "Displays current songs in queue. If you need to show full info: use queue all/full;\naliases = q", aliases=['q'])
async def queue(ctx, arg = 'True'):
    try: await ctx.message.delete()
    except: pass
    if arg == 'all' or arg =='full': param = False
    else:param = True
    all_info =''
    if cur_info: 
        try: 
            if param == False: await ctx.send('1. '+cur_info.split('Now playing: ')[1]+'\n',delete_after =120)
            else: all_info+='1. '+cur_info.split('Now playing: ')[1].split('\n')[0]+'\n'
        except: 
            await ctx.send('Music is not playing', delete_after = 3)
            return
    else:
        await ctx.send('Music is not playing', delete_after = 3)
        return
    
    if param == False:
        i = 2
        for info in info_queue:
            info = str(i) + '. ' + info.split('Now playing: ')[1]
            i+=1
            await ctx.send(info, delete_after = 120)
    elif param == True: 
        i = 2
        for info in info_queue:
            info = str(i) + '. ' + info.split('Now playing: ')[1].split('\n')[0]+'\n'
            i+=1
            all_info+=info
            if len(all_info)>1700:
                await ctx.send(all_info, delete_after = 120)
                all_info = ''
        await ctx.send(all_info, delete_after = 120)


@bot.slash_command(pass_context=True, description = 'Displays current songs in queue')
async def queue(ctx, arg:str='not_all'):
    if arg == 'all' or arg =='full': param = False
    else:param = True
    all_info =''
    if cur_info: 
        try: 
            if param == False: await ctx.send('1. '+cur_info.split('Now playing: ')[1]+'\n',delete_after =120)
            else: all_info+='1. '+cur_info.split('Now playing: ')[1].split('\n')[0]+'\n'
        except: 
            await ctx.send('Music is not playing', delete_after = 3)
            return
    else:
        await ctx.send('Music is not playing', delete_after = 3)
        return
    
    if param == False:
        i = 2
        for info in info_queue:
            info = str(i) + '. ' + info.split('Now playing: ')[1]
            i+=1
            await ctx.send(info, delete_after = 120)
    elif param == True: 
        i = 2
        for info in info_queue:
            info = str(i) + '. ' + info.split('Now playing: ')[1].split('\n')[0]+'\n'
            i+=1
            all_info+=info
            if len(all_info)>1700:
                await ctx.send(all_info, delete_after = 120)
                all_info = ''
        await ctx.send(all_info, delete_after = 120)
    await ctx.respond('Success', delete_after = 3)




@bot.command(pass_context=True, brief="(name) - Bot searchs music by (name)",description = "Bot searchs music by (name);\naliases = se, find", aliases=['se', 'find'])
async def search(ctx, *args):
    try: await ctx.message.delete()
    except: pass
    message = ''
    for arg in args:
        message+=str(arg)+' '
    l = 5
    global videosSearch
    videosSearch = VideosSearch(message, limit = l)
    for i in range (0,l):
        res = videosSearch.result()['result'][i]
        await ctx.send(str(i+1) + ". "+ str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(res['link']), delete_after = 60)


@bot.slash_command(pass_context=True, description = 'Bot searchs music')
async def search(ctx, response:str):
    l = 5
    global videosSearch
    videosSearch = VideosSearch(response, limit = l)
    for i in range (0,l):
        res = videosSearch.result()['result'][i]
        await ctx.send(str(i+1) + ". "+ str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(res['link']), delete_after = 60)
    await ctx.respond('Success', delete_after = 3)


@bot.command(pass_context=True, brief="Choose searched music", aliases=['-'])
async def choose(ctx, choosed):
    try: await ctx.message.delete()
    except: pass
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice = await preparation(ctx, voice, channel)

    if voice.is_playing() == False: 
        for file in natsorted(os.listdir("./music/")):
            if file.endswith(".webm"):
                os.remove('./music/'+file)
    global videosSearch
    url = videosSearch.result()['result'][int(choosed)-1]['link']
    def fname_gen(i):
        fname = './music/'+str(i)+'.webm'
        if os.path.isfile(fname) == False: return fname
        else: return fname_gen(i+1)
    fname = fname_gen(1)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': fname
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    music_queue.append(fname)
    res = videosSearch.result()['result'][int(choosed)-1]
    playing_string = "Now playing: "+  str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_queue.append(playing_string)
    if voice.is_playing() == False: play_next(ctx)
    else: 
        global skip_message
        await skip_message.delete()
        await skip_menu(ctx)


@bot.command(pass_context=True, brief="Fix some problems", aliases=['repair'])
async def fix(ctx):
    try: await ctx.message.delete()
    except: pass
    global cur_info
    global source
    global info_queue
    global music_queue
    if cur_info and source:
        info_queue.insert(0,cur_info)
        music_queue.insert(0,source)
    old_info_queue = info_queue
    old_music_queue = music_queue
    try:
        msg = await ctx.channel.fetch_message(cur_message.id)
        await msg.delete()
        loop_msg = await ctx.channel.fetch_message(loop_message.id)
        await loop_msg.delete()
        skip_msg = await ctx.channel.fetch_message(skip_message.id)
        await skip_msg.delete()
    except: pass
    try: 
        await stop(ctx)
        await leave(ctx)
        await join(ctx)
    except: pass
    try: 
        await join(ctx)
        await stop(ctx)
    except: pass
    music_queue = old_music_queue
    info_queue = old_info_queue
    play_next(ctx)


@bot.slash_command(pass_context=True, description = 'Fix some problems')
async def fix(ctx):
    global cur_info
    global source
    global info_queue
    global music_queue
    if cur_info and source:
        info_queue.insert(0,cur_info)
        music_queue.insert(0,source)
    old_info_queue = info_queue
    old_music_queue = music_queue
    try:
        msg = await ctx.channel.fetch_message(cur_message.id)
        await msg.delete()
        loop_msg = await ctx.channel.fetch_message(loop_message.id)
        await loop_msg.delete()
        skip_msg = await ctx.channel.fetch_message(skip_message.id)
        await skip_msg.delete()
    except: pass
    try: 
        await stop(ctx)
        await leave(ctx)
        await join(ctx)
    except: pass
    try: 
        await join(ctx)
        await stop(ctx)
    except: pass
    music_queue = old_music_queue
    info_queue = old_info_queue
    play_next(ctx)
    await ctx.respond('Success', delete_after = 3)


if __name__=="__main__":
    bot.run(TOKEN)
