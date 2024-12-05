from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.session.aiohttp import AiohttpSession
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import re
import os

TOKEN = os.environ.get('TOKEN')
CATAPI = os.environ.get('CATAPI')
DOGAPI = os.environ.get('CATAPI')

cat_url = f"https://api.thecatapi.com/v1/images/search?limit=1&api_key={CATAPI}"
dog_url = f"https://api.thedogapi.com/v1/images/search?limit=1&api_key={DOGAPI}"
cat_beng_url = f"https://api.thecatapi.com/v1/images/search?limit=1&breed_ids=beng&api_key={CATAPI}"

women_gif_id="CgACAgIAAxkBAAEttaNm5z4Bb4USY3rl1VvxCs6j6uZJ9gAC7lgAAl1rOEtbEWcpoPlGiTYE"
mrpenis_gif_id="CAACAgIAAxkBAAIGjGaqRa866MFM7_2dE8YXCy3FHpxSAAKCMwACd7pgSlDQiqr55dnGNQQ"

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer('Привіт, я створений щоб скидувати фото котів. Напиши /help щоб побачити на що я здатен.')

command_list = [
    "/start або /hello- Почати роботу з ботом",
    "/help - Показати список доступних команд",
    "/cat - Отримати фото котика з текстом, якщо він є",
    "/gif - Отримати гіфку котика з текстом, якщо він є",
    "/bengalcat - Отримати фото бенгалського котика з текстом, якщо він є",
    "/today - Отримати який ти котик сьогодні",
    "/селисьзаїбав - нагадати @V_Vladyslavv, щоб він поселився",
    "/mrpenis - Отримаити стікер Mr penis",
    "/women - Отримати прекрасну гіфку",
]
command_text = "\n".join(
    [f"{i+1}. {command}" for i, command in enumerate(command_list)])

@dp.message(Command("help", prefix="!/"))
async def help(message: types.Message):
    await message.answer(f"Ось доступні команди:\n{command_text}", parse_mode='HTML')

async def fetch_image_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            cat_url = data[0]["url"]
            return cat_url

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

async def addTextOnPhoto(url, text):
    # Download the image from the URL
    response = await fetch_image(url)
    img = Image.open(BytesIO(response))
    draw = ImageDraw.Draw(img)

    # Set the font and initial font size
    font_path = "font.ttf"  # Change this to your font file path if needed
    text_width, text_height = img.size

    # start font size
    fontSize = 10
    max_text_width = 0.8 * img.width
    max_text_height = 0.3 * img.height
    jumpsize = 75

    while jumpsize > 1:
        font = ImageFont.truetype(font_path,int(round(fontSize)))
        _, _,  text_width, text_height = draw.textbbox((0, 0), text, font=font)

        if text_width > max_text_width or text_height > max_text_height:
            fontSize -= jumpsize
            jumpsize = jumpsize // 2  # Gradual decrease
        else:
            fontSize += jumpsize
        if jumpsize <= 1:  # Stop resizing if change is too small
            break
        if (fontSize < 10):
           fontSize = 10
           break

    font = ImageFont.truetype(font_path, fontSize)
    _, _,  text_width, text_height = draw.textbbox((0, 0), text, font=font)

    position = ((img.width - text_width) // 2, img.height - text_height - 20)

    # Add text to the image
    draw.text(position, text, fill="white", font=font, stroke_width=1, stroke_fill="black")

    # Save the image to a BytesIO buffer
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    return img_buffer.getvalue()

@dp.message(Command("cat", prefix="/"))
async def getCat(message: types.Message):
    text = message.text.replace("/cat", "", 1).strip()
    try:
        url = await fetch_image_url(cat_url)
    except Exception as e:
        print(e)
        await message.reply('Коти втомилися (помилка API), підіть теж відпочиньте.')
        return

    try:
        if not text:
            await bot.send_photo(chat_id=message.chat.id, photo=url)
        else:
            img_buffer = await addTextOnPhoto(url, text)
            await bot.send_photo(chat_id=message.chat.id, photo=types.BufferedInputFile(file=img_buffer, filename='cat'))
    except Exception as e:
        print(e)
        await message.reply('Ну піздець і де котик...')

@dp.message(Command("bengalcat", prefix="/"))
async def getBengalCat(message: types.Message):
    text = message.text.replace("/bengalcat", "", 1).strip()
    try:
        url = await fetch_image_url(cat_beng_url)
    except Exception as e:
        print(e)
        await message.reply('Коти втомилися (помилка API), підіть теж відпочиньте.')
        return

    try:
        if not text:
            await bot.send_photo(chat_id=message.chat.id, photo=url)
        else:
            img_buffer = await addTextOnPhoto(url, text)
            await bot.send_photo(chat_id=message.chat.id, photo=types.BufferedInputFile(file=img_buffer, filename='cat'))
    except Exception as e:
        print(e)
        await message.reply("Сталася помилка,хмм.. це щось новеньке. Може наступив кінець світу?")

@dp.message(Command("gif", prefix="/"))
async def getGifCat(message: types.Message):
    text = message.text.replace("/gif", "", 1).strip()
    try:
        if not text:
            response = await fetch_image(url='https://cataas.com/cat/gif?type=square')
            await bot.send_animation(chat_id=message.chat.id, animation=types.BufferedInputFile(file=response, filename='cat.gif'))
        else:
            response = await fetch_image(url=f'https://cataas.com/cat/gif/says/{text}?type=square&fontColor=white')
            await bot.send_animation(chat_id=message.chat.id, animation=types.BufferedInputFile(file=response, filename='cat.gif'))
    except Exception as e:
        error = str(e)
        print(error)
        if "Flood control exceeded" in error:
            matches = re.search(r'(\d+)\s*seconds', error)
            await message.reply(f'А не дофіга гіфок? В тг є обмеження, почекай {int(matches.group(1))} секунд')
        else:
            await message.reply('Пу пу пу, гіфки не буде. Бот прийняв іслам')

@dp.message(Command("today", prefix="/"))
async def todayCat(message: types.Message):
    url = await fetch_image_url(cat_url)

    try:
        text = f'{message.from_user.first_name} сьогодні'
        img_buffer = await addTextOnPhoto(url, text)
        await bot.send_photo(chat_id=message.chat.id, photo=types.BufferedInputFile(file=img_buffer, filename='cat'))
    except Exception as e:
        print(e)
        await message.reply('Ти супер котик, але фотки не буде ):')

@dp.message(Command("CAT", prefix="/"))
async def getCAT(message: types.Message):
    try:
        url = await fetch_image_url(cat_url)
        url2 = await fetch_image_url(cat_url)
        await message.reply('Не ори на мене. Тримай двох котів!')
        await bot.send_photo(chat_id=message.chat.id, photo=url)
        await bot.send_photo(chat_id=message.chat.id, photo=url2)
    except Exception as e:
        print(e)
        await message.reply('А нєхуй орати на мене, кота не буде.')

@dp.message(Command("селисьзаїбав", prefix="/"))
async def selys(message: types.Message):
    url = await fetch_image_url(cat_url)
    try:
        text = '@V_Vladyslavv селись заїбав'
        img_buffer = await addTextOnPhoto(url, text)
        await bot.send_message(chat_id=message.chat.id, text='@V_Vladyslavv селись заїбав!')
        await bot.send_photo(chat_id=message.chat.id, photo=types.BufferedInputFile(file=img_buffer, filename='cat'))
    except Exception as e:
        print(e)
        await message.reply('кота не буде, але @V_Vladyslavv селись заїбав')

@dp.message(Command("Hund", prefix="/"))
async def getHund(message: types.Message):
    text = message.text.replace("/Hund", "", 1).strip()
    try:
        url = await fetch_image_url(dog_url)
    except Exception as e:
        print(e)
        await message.reply('Собачки пішли спати (помилка API), підіть теж відпочиньте.')
        return

    try:
        if not text:
            await bot.send_photo(chat_id=message.chat.id, photo=url)
        else:
            img_buffer = await addTextOnPhoto(url, text)
            await bot.send_photo(chat_id=message.chat.id, photo=types.BufferedInputFile(file=img_buffer, filename='hund'))       
    except Exception as e:
        print(e)
        await message.reply('Ну піздець і де песик...')

@dp.message(Command("women", prefix="/"))
async def women(message: types.Message):
    try:
        await bot.send_animation(chat_id=message.chat.id, animation=women_gif_id)
    except Exception as e:
        print(e)
        await message.reply('Мда, жінка зламала бота')
        
@dp.message(Command("mrpenis", prefix="/"))
async def mrpenis(message: types.Message):
    try:
        await bot.send_sticker(chat_id=message.chat.id, sticker=mrpenis_gif_id)
    except Exception as e:
        print(e)
        await message.reply("Містера Пеніса вже не існує 🕯️")

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
