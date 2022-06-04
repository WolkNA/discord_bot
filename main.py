import discord
import time
import asyncio
import yt_dlp as youtube_dl
from youtubesearchpython import VideosSearch
import os
from os import system
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import json
import requests
from bs4 import BeautifulSoup
import random

TOKEN = 'OTc5MDg1MTAxNzMwMjUwODAy.GVXGAr.NGovEQieNeE1tTR5xVVEbyIfo1jfSDR5bXOr60'
bot = commands.Bot(command_prefix=['ебанат: ', 'бот: ','-'])

#@commands.has_permissions(administrator=True) - для использования команд только админом

global music_queue
music_queue = []
global info_queue
info_queue = []
global cur_info
cur_info = ''
global source
source = ''
global loop_mode
loop_mode = False



@bot.command(pass_context=True, brief="[N] - Clear [N] message from channel", description = "Clear [N](default 100) message from channel;\naliases = clr", aliases=['clr'])
@commands.has_permissions(administrator=True)
async def clear(ctx, amount = 100):
    try: await ctx.message.delete()
    except: pass
    try: await ctx.channel.purge(limit = int(amount))
    except: await ctx.send('something went wrong', delete_after = 3)

@bot.command(pass_context=True, brief="Show random meme",description = "Show random meme", aliases=[])
async def meme(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xff9900, title = 'Random Meme')
    embed.set_image(url = json_data['image'])
    await ctx.send(embed = embed)

@bot.command(pass_context=True, brief="Show random wink anime gif",description = "Show random wink anime gif", aliases=[])
async def wink(ctx): 
    response = requests.get('https://some-random-api.ml/animu/wink')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xff9900, title = 'Wink')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@bot.command(pass_context=True, brief="Show random pet anime gif",description = "Show random pet anime gif", aliases=[])
async def pet(ctx): 
    response = requests.get('https://some-random-api.ml/animu/pat')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xff9900, title = 'Pet')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@bot.command(pass_context=True, brief="Show random hug anime gif",description = "Show random hug anime gif", aliases=[])
async def hug(ctx): 
    response = requests.get('https://some-random-api.ml/animu/hug')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xff9900, title = 'Hug')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@bot.command(pass_context=True, brief="[tag] - Show random image from rule34 by [tag]",description = "Show random image from rule34 by [tag];\naliases = 34, r34, hentai", aliases=['r34','34','hentai'])
@commands.has_permissions(administrator=True)
async def rule34(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    res_text = 'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&limit=1000&tags='
    with open('./r34/white_list.json', 'r+') as wl_file:
        white_list = json.load(wl_file)
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    if not tags:
        if white_list: tags = white_list[random.randint(0,len(white_list)-1)]
        else: tags = ''
        tags+=' '+ black_list
        res_text+=tags
    else:
        for tag in tags:
            res_text+=tag+'%20'
        res_text+=black_list
    print(res_text)
    response = requests.get(res_text)
    posts = response.json()
    l = len(posts)
    if l == 0:
        await ctx.send("Can't find any picture", delete_after = 3)
        return
    number = random.randint(0,l-1)
    await ctx.send(posts[number]['file_url'])

@bot.command(pass_context=True, brief="view rule34 tag blacklist",description = "view rule34 tag blacklist;\naliases = 34_bl, r34_bl, hentai_bl", aliases=['r34_bl','34_bl','hentai_bl'])
@commands.has_permissions(administrator=True)
async def rule34_blacklist(ctx):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    i=1
    black_list = black_list.replace(' ','')
    black_list = black_list.split('-')
    for tag in black_list:
        if tag:
            await ctx.send(str(i)+'. '+tag, delete_after = 60)
            i+=1

@bot.command(pass_context=True, brief="[tag] - add rule34 [tag] to blacklist",description = "[tag] - add rule34 [tag] to blacklist;\naliases = 34_bla, r34_bla, hentai_bla", aliases=['r34_bla','34_bla','hentai_bla'])
@commands.has_permissions(administrator=True)
async def rule34_blacklist_add(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/black_list.json', 'r+') as bl_file:
        black_list = json.load(bl_file)
    if tags:
        for tag in tags:
            if tag in black_list: pass
            else: black_list+=' -'+tag
        with open('./r34/black_list.json','r+') as bl_file:
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
            if (' -'+tag) in black_list: black_list = black_list.replace(' -'+tag,'')
            elif ('-'+tag) in black_list: black_list = black_list.replace('-'+tag,'')
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
    for tag in white_list:
        await ctx.send(str(i)+'. '+tag, delete_after = 60)
        i+=1


@bot.command(pass_context=True, brief="[tag] - add rule34 [tag] to whitelist",description = "[tag] - add rule34 [tag] to whitelist;\naliases = 34_wla, r34_wla, hentai_wla", aliases=['r34_wla','34_wla','hentai_wla'])
@commands.has_permissions(administrator=True)
async def rule34_whitelist_add(ctx, *tags):
    try: await ctx.message.delete()
    except: pass
    with open('./r34/white_list.json', 'r+') as wl_file:
        white_list = json.load(wl_file)
    if tags:
        for tag in tags:
            if tag in white_list: pass
            else: white_list.append(' '+tag)
        with open('./r34/white_list.json','r+') as wl_file:
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
            if (' '+tag) in white_list: white_list.remove(' '+tag,'')
            elif (tag) in white_list: white_list.remove(tag,'')
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

@bot.command(pass_context=True, brief="(url) - Play a song by (url)",description = "Play a song by (url);\naliases = p, pl", aliases=['pl', 'p'])
async def play(ctx, url: str):
    try: await ctx.message.delete()
    except: pass
    if len(music_queue)>0:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
        await ctx.send("Music added to queue", delete_after = 3)
    else:
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel", delete_after = 3)
            return
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            pass
        else:
            voice = await channel.connect()
            await ctx.send(f"Joined {channel}", delete_after = 3)
        if voice.is_playing()==False: await ctx.send("Getting everything ready, playing audio soon", delete_after = 3)
        else: await ctx.send("Music added to queue", delete_after = 3)
        print("Someone wants to play music let me get that ready for them...")
    if voice.is_playing() == False: 
        for file in os.listdir("./music/"):
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
    print (music_queue)
    print('playing...\n')
    res = videosSearch.result()['result'][0]
    playing_string = "Now playing: "+  str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_queue.append(playing_string)
    def play_next():
        if len(music_queue)>0:
            source = music_queue.pop(0)
            global cur_info
            cur_info = info_queue.pop(0)
            if loop_mode == True: 
                music_queue.append(source)
                info_queue.append(cur_info)
            voice = get(bot.voice_clients, guild=ctx.guild)
            try:
                voice.play(discord.FFmpegPCMAudio(source = source), after = lambda e: play_next())
                asyncio.run_coroutine_threadsafe(send_message(ctx,cur_info), bot.loop)
            except: pass
    if voice.is_playing() == False: play_next()

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

async def send_message(ctx, cur_info):
    await ctx.send(cur_info, delete_after = 60)

@bot.command(pass_context=True, brief="(song name) - Bot plays the first found music",description = "Bot plays the first found music;\naliases = pf, sf, playf", aliases=['sf', 'pf', 'playf'])
async def playfirst(ctx, *args):
    try: await ctx.message.delete()
    except: pass
    if len(music_queue)>0:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
        await ctx.send("Music added to queue", delete_after = 3)
    else:
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel", delete_after = 3)
            return
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            pass
        else:
            voice = await channel.connect()
            await ctx.send(f"Joined {channel}", delete_after = 3)
        if voice.is_playing()==False: await ctx.send("Getting everything ready, playing audio soon", delete_after = 3)
        else: await ctx.send("Music added to queue", delete_after = 3)
        print("Someone wants to play music let me get that ready for them...")
    if voice.is_playing() == False: 
        for file in os.listdir("./music/"):
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
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    music_queue.append(fname)
    print (music_queue)
    print('playing...\n')
    res = videosSearch.result()['result'][0]
    playing_string = "Now playing: "+  str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
    info_queue.append(playing_string)

    def play_next():
        if len(music_queue)>0:
            source = music_queue.pop(0)
            global cur_info
            cur_info = info_queue.pop(0)
            if loop_mode == True: 
                music_queue.append(source)
                info_queue.append(cur_info)
            voice = get(bot.voice_clients, guild=ctx.guild)
            try:
                voice.play(discord.FFmpegPCMAudio(source = source), after = lambda e: play_next())
                asyncio.run_coroutine_threadsafe(send_message(ctx,cur_info), bot.loop)
            except: pass
    if voice.is_playing() == False: play_next()

@bot.command(pass_context=True, brief="Skip current song",description = "Skip current song;\naliases = pass", aliases=['pass'])
async def skip(ctx):
    try: await ctx.message.delete()
    except: pass
    if len(music_queue)>0:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
    def play_next():
        if len(music_queue)>0:
            source = music_queue.pop(0)
            global cur_info
            cur_info = info_queue.pop(0)
            if loop_mode == True: 
                music_queue.append(source)
                info_queue.append(cur_info)
            voice = get(bot.voice_clients, guild=ctx.guild)
            try:
                voice.stop()
                voice.play(discord.FFmpegPCMAudio(source = source), after = lambda e: play_next())
                asyncio.run_coroutine_threadsafe(send_message(ctx,cur_info), bot.loop)
            except: pass
        else: voice.pause()
    if voice.is_playing() == True: play_next()
    await ctx.send('Music Skipped', delete_after = 3)

@bot.command(pass_context=True, brief="Output current song",description = "Output current song;\naliases = ?", aliases=['?'])
async def now(ctx, *args):
    try: await ctx.message.delete()
    except: pass
    try: await ctx.send(cur_info, delete_after = 60)
    except: await ctx.send('Music is not playing', delete_after = 3)

@bot.command(pass_context=True, brief="Enable/Disable loop mode",description = "Enable/Disable loop mode;\naliases = cycle", aliases=['cycle'])
async def loop(ctx, *args):
    global loop_mode
    try: await ctx.message.delete()
    except: pass
    if loop_mode == True: 
        loop_mode = False
        await ctx.send('Loop mode has been disabled', delete_after = 3)
    elif loop_mode == False: 
        loop_mode = True
        await ctx.send('Loop mode has been enabled', delete_after = 3)

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

@bot.command(pass_context=True, brief="Show playlists",description = "Show playlists;\naliases = pls, pl_list", aliases=['pls','pl_list'])
async def playlists(ctx):
    try: await ctx.message.delete()
    except: pass
    dirname = './playlists'
    dirs = os.listdir(dirname)
    out_string = 'Current playlist count: ' + str(len(dirs))
    for dir in dirs:
        out_string+='\n'+str(dir)
    await ctx.send(out_string, delete_after = 60)
    pass

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
    for file in os.listdir('./playlists/'+str(playlist)):
        filename = file.rsplit('.')[0]
        fileext = file.rsplit('.')[1]
        if int(filename)>int(number):
            os.rename('./playlists/'+str(playlist)+'/'+filename+'.'+fileext, './playlists/'+str(playlist)+'/'+str(int(filename)-1)+'.'+fileext)

@bot.command(pass_context=True, brief="(name) - Show info about playlist named (name)",description = "Show info about playlist named (name);\naliases = pl_i, pl_info", aliases=['pl_i','pl_info'])
async def playlist_info(ctx, playlist):
    try: await ctx.message.delete()
    except: pass
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    out_string =''
    for file in os.listdir('./playlists/'+str(playlist)):
        if file.endswith(".info"):
            with open('./playlists/'+str(playlist)+'/'+file,'r', encoding="utf-8") as file:
                fname = os.path.splitext(file.name)[0].rsplit('/')[-1]
                out_string = fname +'. ' + file.read()
                await ctx.send(out_string, delete_after = 60)

@bot.command(pass_context=True, brief="(name) - Move playlist named (name) to queue",description = "Move playlist named (name) to queue;\naliases = pl_p", aliases=['pl_p'])
async def playlist_play(ctx, playlist):
    try: await ctx.message.delete()
    except: pass
    if not os.path.exists('./playlists/'+str(playlist)):
        await ctx.send("Playlist doesn't exist", delete_after = 3)
        return
    if len(music_queue)>0:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
        await ctx.send("Music added to queue", delete_after = 3)
    else:
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel", delete_after = 3)
            return
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            pass
        else:
            voice = await channel.connect()
            await ctx.send(f"Joined {channel}", delete_after = 3)
        if voice.is_playing()==False: await ctx.send("Getting everything ready, playing audio soon", delete_after = 3)
        else: await ctx.send("Music added to queue", delete_after = 3)
        print("Someone wants to play music let me get that ready for them...")
    dir = './playlists/'+playlist+'/'
    files = os.listdir(dir)
    for file in files:
        if file.endswith('.info'):
            with open(dir+file,'r', encoding="utf-8") as f:
                playing_string = 'Now playing: '+f.read()
                info_queue.append(playing_string)
        elif file.endswith('.webm'):
            music_queue.append(dir+str(file))
    def play_next():
        if len(music_queue)>0:
            source = music_queue.pop(0)
            global cur_info
            cur_info = info_queue.pop(0)
            if loop_mode == True: 
                music_queue.append(source)
                info_queue.append(cur_info)
            voice = get(bot.voice_clients, guild=ctx.guild)
            try:
                voice.play(discord.FFmpegPCMAudio(source = source), after = lambda e: play_next())
                asyncio.run_coroutine_threadsafe(send_message(ctx,cur_info), bot.loop)
            except: pass
    if voice.is_playing() == False: play_next()

@bot.command(pass_context=True, brief="Displays current songs in queue",description = "Displays current songs in queue;\naliases = q", aliases=['q'])
async def queue(ctx):
    try: await ctx.message.delete()
    except: pass
    if cur_info: 
        try: await ctx.send('1. '+cur_info.lstrip('Now playing: '), delete_after = 60)
        except: 
            await ctx.send('Music is not playing', delete_after = 3)
            return
    else:
        await ctx.send('Music is not playing', delete_after = 3)
    i = 2
    for info in info_queue:
        info = str(i) + '. ' + info.lstrip('Now playing: ')
        await ctx.send(info, delete_after = 60)
        i+=1

@bot.command(pass_context=True, brief="(name) - Bot searchs music by (name)",description = "Bot searchs music by (name);\naliases = se, find", aliases=['se', 'find'])
async def search(ctx, *args):
    try: await ctx.message.delete()
    except: pass
    message = ''
    for arg in args:
        message+=str(arg)+' '
    l = 5
    videosSearch = VideosSearch(message, limit = l)
    for i in range (0,l):
        res = videosSearch.result()['result'][i]
        await ctx.send(str(i+1) + ". "+ str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(res['link']), delete_after = 60)
        
    @bot.command(pass_context=True, brief="Choose searched music", aliases=['-'])
    async def choose(ctx, choosed):
        if len(music_queue)>0:
            channel = ctx.message.author.voice.channel
            voice = get(bot.voice_clients, guild=ctx.guild)
            await ctx.send("Music added to queue", delete_after = 3)
        else:
            channel = ctx.message.author.voice.channel
            if not channel:
                await ctx.send("You are not connected to a voice channel", delete_after = 3)
                return
            voice = get(bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                pass
            else:
                voice = await channel.connect()
                await ctx.send(f"Joined {channel}", delete_after = 3)
            if voice.is_playing()==False: await ctx.send("Getting everything ready, playing audio soon", delete_after = 3)
            else: await ctx.send("Music added to queue", delete_after = 3)
            print("Someone wants to play music let me get that ready for them...")
        if voice.is_playing() == False: 
            for file in os.listdir("./music/"):
                if file.endswith(".webm"):
                    os.remove('./music/'+file)
        
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

        print (music_queue)
        print('playing...\n')
        res = videosSearch.result()['result'][int(choosed)-1]
        playing_string = "Now playing: "+  str(res['title'])+';\t'+ str(res['duration'])+';\t'+ str(res['viewCount']['text']) +'\n'+ str(url)
        info_queue.append(playing_string)

        def play_next():
            if len(music_queue)>0:
                source = music_queue.pop(0)
                global cur_info
                cur_info = info_queue.pop(0)
                if loop_mode == True: 
                    music_queue.append(source)
                    info_queue.append(cur_info)
                voice = get(bot.voice_clients, guild=ctx.guild)
                try:
                    voice.play(discord.FFmpegPCMAudio(source = source), after = lambda e: play_next())
                    asyncio.run_coroutine_threadsafe(send_message(ctx,cur_info), bot.loop)
                except: pass
        if voice.is_playing() == False: play_next()

bot.run(TOKEN)