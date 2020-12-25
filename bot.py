from datetime import datetime, timedelta
import dateutil.parser
from discord.ext import tasks
import discord
import mechanize
import bs4
import json
import random
import wikipedia
import getopt
import shlex

'''
	created by Dominic Antigua
			   for
		Alipin Sagigilid
 '''

browser = mechanize.Browser()
subject_code = {"_2280_1" : ["Art Appreciation", 748465313208860682, "https://g.co/meet/5f8850e2-34f4-44c0-bfca-7809125285c4"], "_3718_1" : ["Theology 3", 748465443366240307, "https://g.co/meet/e96f8ad1-07a5-49a2-8ac0-9f42e33ef2f2"], "_3507_1" : ["Computer Animation Lab", 748465465843777557, "https://g.co/meet/626eacb2-4ac6-4000-9dfd-630095ee68d3"], "_3508_1" : ["Computing 3", 748465392485269558, "https://meet.google.com/ssb-kzea-qco"], "_3509_1" : ["Data Structure and Algorithm", 748465214877466685, ""], "_3510_1" : ["Digital Design Lab", 748465289838067713, "https://g.co/meet/8b97c53a-7a36-41c1-8c84-e6c381b18a69"], "_3511_1" : ["Digital Design Lec", 748465289838067713, "http://meet.google.com/jbm-joxc-mso"], "_3512_1" : ["Discrete Structures", 748465247718735872, ""], "_1904_1" : ["Physical Education", 748465551403384902, "https://zoom.us/j/96227717347?pwd=b0pJc1BmajltaE05WmFtMHVPbStOdz09"], "_1905_1" : ["Readings in Philippines History", 748465362668093451, ""], "_1906_1" : ["Contemporary World", 748465422072021012,"http://meet.google.com/vda-weoe-ctx"], "_812_1":["Student Orientation Course", 746914199116054610, ""]}
discord_token = 'DISCORD_TOKEN'

def retrieve_assignments(json):
	arr = dict()
	current_subject = ""
	item = []
	for x in range(0, len(json["results"])):
		if json["results"][x]["type"] == "GradebookColumn":
			if current_subject != json["results"][x]["calendarId"]:
				current_subject = json["results"][x]["calendarId"]
				item = []
			item.append(json["results"][x]["title"])
			item.append(json["results"][x]["end"])
			arr[current_subject] = item
	return arr

def retrieve_announcements(json):
	arr = dict()
	title = ""
	for x in range(0, len(json["results"])):
		title = json["results"][x]["title"]
		arr[str(json["results"][x]["created"])] = [title, str(json["results"][x]["body"])]
	return arr

def data_onDay(data):
	today_daydate = datetime.today()
	arr = dict()
	today_date = datetime.strptime(str(str(today_daydate.month) +"/"+str(int(today_daydate.day))+"/"+str(today_daydate.year)+ " "+str(today_daydate.hour)+":"+ str(today_daydate.minute)), "%m/%d/%Y %H:%M")
	for key in data:
		data_date = dateutil.parser.parse(str(key))
		data_date += timedelta(hours=8)
		data_date = datetime.strptime(str(str(data_date.month) +"/"+str(int(data_date.day))+"/"+str(data_date.year)+ " "+str(data_date.hour)+":"+ str(data_date.minute)), "%m/%d/%Y %H:%M")
		start = data_date-timedelta(minutes=3)
		end = data_date+timedelta(minutes=4)
		if start <= today_date and end >= today_date:
			arr[key] = data[key]
	return arr


def subject_to_code(subject):
	code = ""
	if subject == "computing":
		code = "_3508_1"
	elif subject == "art" or subject == "art app":
		code = "_2280_1"
	elif subject == "theology" or subject == "theo":
		code = "_3718_1" 
	elif subject == "animation" or subject == "computer animation":
		code = "_3507_1"
	elif subject == "dsa" or subject == "data structure":
		code = "_3509_1"
	elif subject == "ddlab"  or subject == "digital lab":
		code = "_3510_1"
	elif subject == "ddlec" or subject == "digital lec":
		code = "_3511_1"
	elif subject == "ds" or subject == "discrete structure":
		code = "_3512_1"
	elif subject == "rph" or subject == "reading in philippines history":
		code = "_1905_1"
	elif subject == "contemporary"  or subject == "contemporary world" or subject == "contempt" or subject == "contemp":
		code = "_1906_1"
	elif subject == "pe"  or subject == "physical education":
		code = "_1904_1" 
	else:
		code = ""
	return code
		

def bb_login(browser):
	browser.set_handle_robots(False)
	cookies = mechanize.CookieJar()
	browser.set_cookiejar(cookies)
	browser.set_handle_refresh(False)

	#Credentials
	url = 'https://adamson.blackboard.com'
	browser.open(url)
	browser.select_form(nr = 1)     
	browser.form['user_id'] = 'BLACKBOARD_USERID'
	browser.form['password'] = 'BLACKBOARD_PASSWORD'
	response = browser.submit()

def bb_data(api=""):
	resp = browser.open('https://adamson.blackboard.com/learn/api/public/v1/'+api)
	soup = bs4.BeautifulSoup(resp, "html.parser")
	data = json.loads(soup.text)
	return data

def embed_template(title="", fields = [], isFormA=False):
	embed = discord.Embed(title=title)
	for key in fields.keys():
		code_content = "```excel\n"
		for value in range(0, len(fields[key])):
			if value % 2 == 0:
				titleEmbed = str(fields[key][value])
				date = dateutil.parser.parse(key) if isFormA else dateutil.parser.parse(fields[key][value+1])
				date += timedelta(hours=8)
				timeformat = datetime.strptime(str(int(date.hour)) +":"+str(date.minute), "%H:%M")
				if isFormA:
					slice_content = str(fields[key][value+1])
					code_content +=  slice_content[0:500]+"\n"
				else:
					slice_content = fields[key][value]
					code_content += spacing_allignment(slice_content[0:30]) +"...\t"+ str(date.month)+"/"+str(date.day)+"/"+str(date.year) +" "+timeformat.strftime("%I:%M %p")+"\n"
		if isFormA:
			embed.add_field(name=str(":loudspeaker: "+fields[key][0]), value = code_content+"```\n", inline=False)
		else:
			embed.add_field(name=str(":pushpin: "+subject_code[key][0]), value = "["+code_content+"```](https://adamson.blackboard.com/ultra/courses/"+key+"/outline)\n",inline=False)
	return embed

def embed_error_template(error_string, color=0xfd0061):
	embedVar = discord.Embed()
	embedVar.colour = color
	embedVar.description = error_string
	return embedVar

def help_command(bot_name=""):
	embed = discord.Embed()
	embed.set_author(name=bot_name,icon_url="https://cdn.discordapp.com/avatars/759358801140383786/2143ec8b0356a847322837032259c5a2.webp?size=256")
	embed.description = bot_name+" is the easiest way to show the latest announcements, permanent online classroom links, and assignments from the Blackboard platform to your Discord server. Also, we add some other features like list randomizer and cheat search coming from the different webpage sources.\n"
	embed.add_field(name="Commands", value ="`;a`\t - shows all the assignments from Blackboard\n\n`;k \"subject\"`\t - shows all the announcement from the specific subject\n\n`;r [list]`\t - randomize the array list\n\n`;m \"subject\"`\t - shows the permanent link of the subject Google Meet/Zoom on a specific subject channel\n\n`;c \"keyword\"`\t - search the specific keyword and the bot will deliver it from internet to you\n\n`;h`\t - shows the help embed of this bot", inline=False)
	embed.add_field(name="Subject Keywords", value="`ddlab`\t - Digital Design Lab\n\n`ddlec`\t - Digital Design Lec\n\n`contemp`\t - The Contemporary World\n\n`art`\t - Art Appreciation\n\n`rph`\t - Reading in Philippine History\n\n`animation`\t - Computer Animation\n\n`computing`\t - Computing 3\n\n`theo`\t - Theology 3\n\n`dsa`\t - Data Structures and Algorithm\n\n`ds`\t - Discrete Mathematics\n\n")
	#embed.add_field(name="Our Motivation", value="We motivated to make this bot because of the fucking Blackboard is full of bugs, the platform is much hassle to use, ISP in the Philippines are shits, and the government is fucking us. So as a lazy student, I always ask for the latest assignments or announcements to my classmates, and sometimes, when someone asks me or not (It depends on the person), I share the meet links or assignments. So, to cope up with this raping of this government, I made a private server on my home to run this fucking bot 24/7 but the fucking PLDC makes my bot cunt sometimes because of the poor services they giving. I'm sorry if you have any experience with the delay. FUCKKKKKKKK.\n")
	embed.set_footer(text="Created by Mr.Yorph & Nam Do-San");
	return embed

def spacing_allignment(text="", limit=30):

	for i in range(len(text), limit):
		text+=" "
	return text
	

#------------------------------------------------------------------
bb_login(browser) 	# adamson blackboard initialization
client = discord.Client()	#discord

@tasks.loop(minutes=3, reconnect= True)
async def EveryAnnounce():
	for i in subject_code:
		channel = client.get_channel(subject_code[i][1])
		announcement_data = data_onDay(retrieve_announcements(bb_data(api="courses/"+i+"/announcements")))
		if bool(announcement_data):
			await channel.send(embed=embed_template(title=subject_code[i][0]+" Announcement",fields= announcement_data, isFormA=True))

EveryAnnounce.start()


@client.event
async def on_message(message):
	channel = message.channel
	if message.author == client.user:	return 

	#assignment
	if message.content.startswith(';assignment') or message.content == str(';a'):
		assignment = retrieve_assignments(bb_data("calendars/items"))
		if bool(len(assignment)):
			await channel.send(embed=embed_template(title="CS201 Blackboard Assignments", fields= assignment, isFormA=False))
		else:
			await channel.send(embed=embed_error_template("You doesn't have any available assignments today"))

	#announcement command
	if (message.content.startswith(';k')) or (message.content == str(';k')):
		split_str = message.content.split(' ');
		code= ""
		try:
			code = subject_to_code(((str(split_str[1])).lower())).strip()
			if bool(code):
				json_subj = bb_data("courses/"+code+"/announcements")
				if bool(json_subj["results"]):
					await channel.send(embed=embed_template(subject_code[code][0]+" Announcement", retrieve_announcements(json_subj), isFormA=True))
				else:
					await channel.send(embed=embed_error_template("No Announcement yet on this subject"))
			else:
				await channel.send(embed=embed_error_template("Invalid CS201 subject"))
		except IndexError as e:
			await channel.send(embed=embed_error_template("Must have a subject argument"))

	#meet command
	if(message.content.startswith(";meet")) or (message.content.startswith(";m")):
		message_split = shlex.split(message.content)
		code = subject_to_code(((str(message_split[1])).lower())).strip()
		if code in subject_code:
			if bool(subject_code[code][2]):
				await channel.send(embed=discord.Embed(title="You Summon The "+subject_code[code][0], colour=0xE5E242, description="Click this portal: [Sauce]("+subject_code[code][2]+")"))
			else:
				await channel.send(embed=embed_error_template("This subject doesn't have a permanent link for google meet."))
		else:
			await channel.send(embed=embed_error_template("This subject doesn't exist"))
			
		
	#random command
	if message.content.startswith(';random') or message.content.startswith(';r'):
		split_str = message.content.split(" ")
		try:
			name_list = split_str[1].rstrip().split(";")
			await channel.send(embed=discord.Embed(title="Russian Roulette", colour=0xE5E242, description=str(client.user.name)+" pick:```css\n"+random.choice(name_list)+"```"))
		except IndexError as e:
			await channel.send(embed=embed_error_template("No argument pass on this command"))

	if message.content.startswith(";cheat") or message.content.startswith(';c'):
		split_str = message.content.split(" ", 1)
		search_result  = []
		suggested_text = ""
		search_result  = wikipedia.search(split_str[1], results=10)
		for i in search_result:
			suggested_text += "\t\t 	`"+i+"`,  \t\t"
		try:
			if split_str[1].find('\"') == -1:
				await channel.send(embed=discord.Embed(title="Suggested Search", colour=0xE5E242, description=suggested_text))
			else:
				await channel.send(embed=discord.Embed(title="\""+split_str[1]+"\" Search :mag_right:", colour=0xE5E242, description=wikipedia.summary(split_str[1], sentences = 3)))
		except IndexError as e:
			print("error")
		except wikipedia.exceptions.DisambiguationError as e:
			await channel.send(embed=embed_error_template("\"***"+split_str[1]+"***\" have many exact words on the net, please use suggestion command to pick the desired word", color=0xfd0061))
		except wikipedia.exceptions.PageError as e:
			await channel.send(embed=embed_error_template("\"***"+split_str[1]+"***\" doesn't match any search pages", color=0xfd0061))


	#help command
	if message.content.startswith(';help') or message.content.startswith(";h"):
		await channel.send(embed=help_command(bot_name=client.user.name))


@client.event
async def on_ready():
    print(client.user.name+" is running ....")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=";help"))
    
client.run(discord_token)
