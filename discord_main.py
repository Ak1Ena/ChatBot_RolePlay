import discord
from discord.ext import commands
from chatbot import ChatBot
from configparser import ConfigParser
import re
import json

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

# Load the token from a secure config file or environment variable
with open('token.txt','r',encoding='utf-8')as file:
    token = file.read()
    Token = re.search(r'token\s*:\s*"([^"]+)"',token)
    if Token:
        toKen = Token.group(1)
    else:
        toKen = None
TOKEN = toKen

# เปิดไฟล์และอ่านข้อมูล

with open('role.txt', 'r', encoding='utf-8') as file:
    data = file.read()
    # ใช้ regular expression เพื่อค้นหาข้อมูล Name, Game, Detail_Character, และ Setting
    name_match = re.search(r'Name\s*:\s*"([^"]+)"', data)
    game_match = re.search(r'Game\s*:\s*"([^"]+)"', data)
    detail_match = re.search(r'Detail_Character\s*:\s*"([^"]+)"', data, re.DOTALL)
    setting_match = re.search(r'Setting\s*:\s*"([^"]+)"', data, re.DOTALL)

# แยกเก็บเป็นตัวแปร
if name_match:
    name = name_match.group(1)
else:
    name = None

if game_match:
    game = game_match.group(1)
else:
    game = None

if setting_match:
    setting = setting_match.group(1).strip()
else:
    setting = None

if detail_match:
    detail_character = detail_match.group(1).strip()
else:
    detail_character = None

"""Function to interact with Gemini AI."""
config = ConfigParser()
config.read('credentials.txt')

if 'gemini_ai' in config and 'API_KEY' in config['gemini_ai']:
    api_key = config['gemini_ai']['API_KEY']
else:
    raise KeyError("API_KEY is missing in the config file.")

chatbot = ChatBot(api_key=api_key)
chatbot.start_conversation()
chatbot.send_prompt(
    f'ช่วย role play เป็น {name} จาก {game} หน่อย!และนี่คือ setting ของโลก {setting}! และนี่คือรายละเอียดของตัวละครที่จะต้องสวมบทบาท {detail_character}ถ้าต้องการใส่อารมณ์ความรู้สึกท่าทางให้เว้นบรรทัดและใช้()ในการบอกอารมณ์หรือท่าทางของตัวละคร! ห้ามบอกว่าตัวเองเป็น AI เด็ดขาด! และห้ามหลุดจาก Character ด้วย !! ห้ามตอบในนามของAI แต่ตอบในนามของตัวละครที่สวมบทบาท และความสัมพันธ์ของตัวละครกับผู้ใช้ ในตอนแรกให้แสดงเหมือนคนแปลกหน้ากัน ไม่จำเป็นต้องสนใจผู้เล่นก็ได้ และก็ช่วยเป็นผู้บรรยาายเนื้อเรื่องด้วย โดยถ้าเป็นผู้บรรยายเนื้อเรื่องให้ใช้ [] ถ้าเกิดเนื้อเรื่องดูไปต่อไม่ได้ให้พูดว่า"จบ"เลย และให้พูดอย่างเป็นธรรมชาติที่สุดเท่าที่ทำได้ ห้ามถามซ้ำยกเว้นต้องการย้ำเตือน สถานที่ให้เริ่มที่เมือง'
)
chatbot.send_prompt("ขอภาษาไทยนะ")

def extract_text_from_json(response):
    """Function to extract text from a JSON string."""
    try:
        data = json.loads(response)
        if isinstance(data, list):
            # If it's a list, join into a single line string
            return ' '.join(data)
        return data.get('text', '')
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")  # Debug information
        return response


def remove_word_from_response(response, word_to_remove):
    """Function to remove unwanted words from the response."""
    pattern = r'\b{}\b'.format(re.escape(word_to_remove))
    cleaned_response = re.sub(pattern, '', response).strip()
    return cleaned_response


def gemini(text):
    response = chatbot.send_prompt(text)
    word = extract_text_from_json(response)
    word = remove_word_from_response(word, 'text')
    word = word.replace("{", "").replace("}", "").replace('"', "")

    return word

# Event for when the bot is ready
@bot.event
async def on_ready():
    print("Bot is ready and connected!")

# Event for handling messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages sent by the bot itself

    mes = message.content
    text = gemini(mes)
    await message.channel.send(text)  # Send the chatbot's response back to the channel


# Run the bot using the provided token
bot.run(TOKEN)
