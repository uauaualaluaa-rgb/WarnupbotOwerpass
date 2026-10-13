import asyncio
import logging
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from telethon import TelegramClient, functions, types as tl_types
from telethon.errors import SessionPasswordNeededError, FloodWaitError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

BOT_TOKEN = "8862811439:AAGKNCDLKgfHnhxsKoTH3CuzaLfnPb659R4"
API_ID = 38387697
API_HASH = "e8fb7f7163498eb28231e45071fe92c0"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

os.makedirs("sessions", exist_ok=True)
os.makedirs("avatars", exist_ok=True)

# Тематические каналы для подписки
CHANNELS = [
    "@durov",
    "@telegram",
    "@tginfo",
    "@telegramtips",
    "@contest",
]

# Имена для аккаунтов
FIRST_NAMES = ["Алексей", "Дмитрий", "Сергей", "Андрей", "Максим", "Иван", "Никита", "Артём"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Попов", "Волков"]
USERNAME_PREFIX = ["user", "acc", "real", "person", "human", "tg", "man"]

# Описания
BIOS = [
    "Люблю путешествия ✈️",
    "Просто человек 🌍",
    "Фотограф 📸",
    "Программист 💻",
    "Спорт и здоровье 💪",
    "Книги и кофе ☕",
    "Музыка 🎵",
    "Жизнь прекрасна ✨",
    "Друзья и общение 👥",
    "Учусь новому 📚",
]

# Аватарки-заглушки (цветные квадраты)
def generate_avatar(name: str):
    """Генерация простой аватарки с буквой"""
    from PIL import Image, ImageDraw, ImageFont
    import random
    
    colors = [
        (255, 87, 87), (87, 178, 255), (87, 255, 135),
        (255, 200, 87), (200, 87, 255), (87, 255, 235),
        (255, 135, 87), (135, 87, 255),
    ]
    
    color = random.choice(colors)
    img = Image.new('RGB', (512, 512), color)
    draw = ImageDraw.Draw(img)
    
    letter = name[0].upper() if name else "U"
    
    try:
        font = ImageFont.truetype("arial.ttf", 300)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((512-w)/2, (512-h)/2 - 30), letter, fill=(255, 255, 255), font=font)
    
    path = f"avatars/{name}_{random.randint(1000, 9999)}.jpg"
    img.save(path)
    return path

async def get_country(client: TelegramClient):
    """Определение страны аккаунта"""
    try:
        me = await client.get_me()
        phone = me.phone or ""
        
        # По коду номера
        codes = {
            "7": "Россия/Казахстан",
            "375": "Беларусь",
            "380": "Украина",
            "77": "Казахстан",
            "996": "Киргизия",
            "998": "Узбекистан",
            "994": "Азербайджан",
            "995": "Грузия",
            "373": "Молдова",
            "371": "Латвия",
            "370": "Литва",
            "372": "Эстония",
            "48": "Польша",
            "49": "Германия",
            "1": "США/Канада",
            "44": "Великобритания",
            "90": "Турция",
        }
        
        for code, country in sorted(codes.items(), key=lambda x: -len(x[0])):
            if phone.startswith("+" + code):
                return country
        
        return "Неизвестно"
    except:
        return "Неизвестно"

async def setup_profile(client: TelegramClient):
    """Настройка профиля аккаунта"""
    try:
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Установка имени
        await client(functions.account.UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name
        ))
        await asyncio.sleep(1)
        
        # Установка био
        bio = random.choice(BIOS)
        await client(functions.account.UpdateProfileRequest(
            about=bio
        ))
        await asyncio.sleep(1)
        
        # Установка аватарки
        avatar_path = generate_avatar(first_name)
        try:
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file(avatar_path)
            ))
            os.remove(avatar_path)
        except Exception as e:
            logging.warning(f"Аватар не установлен: {e}")
        
        await asyncio.sleep(1)
        
        # Установка юзернейма
        for _ in range(5):
            username = f"{random.choice(USERNAME_PREFIX)}{random.randint(10000, 999999)}"
            try:
                await client(functions.account.UpdateUsernameRequest(username=username))
                return first_name, last_name, username, bio
            except Exception as e:
                if "USERNAME_OCCUPIED" in str(e) or "USERNAME_INVALID" in str(e):
                    continue
                else:
                    break
        
        return first_name, last_name, None, bio
    except Exception as e:
        logging.error(f"Ошибка настройки: {e}")
        return None, None, None, None

async def subscribe_channels(client: TelegramClient):
    """Подписка на каналы"""
    subscribed = 0
    for channel in CHANNELS:
        try:
            await client(functions.channels.JoinChannelRequest(channel=channel))
            subscribed += 1
            await asyncio.sleep(random.randint(3, 7))
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except:
            pass
    return subscribed

async def view_channels(client: TelegramClient):
    """Просмотр каналов (имитация активности)"""
    try:
        dialogs = await client.get_dialogs(limit=10)
        for dialog in dialogs:
            try:
                await client.get_messages(dialog.id, limit=5)
                await asyncio.sleep(random.randint(2, 5))
            except:
                pass
    except:
        pass

async def warmup_account(session_path: str):
    """Прогрев одного аккаунта"""
    session_name = session_path.replace(".session", "")
    client = TelegramClient(session_name, API_ID, API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            return None
        
        me = await client.get_me()
        country = await get_country(client)
        
        # Настройка профиля
        first_name, last_name, username, bio = await setup_profile(client)
        
        # Подписка на каналы
        subs = await subscribe_channels(client)
        
        # Просмотр каналов
        await view_channels(client)
        
        await asyncio.sleep(random.randint(5, 10))
        
        result = {
            "phone": me.phone,
            "user_id": me.id,
            "first_name": first_name or me.first_name,
            "last_name": last_name or "",
            "username": username,
            "country": country,
            "subscriptions": subs,
        }
        
        await client.disconnect()
        return result
    
    except Exception as e:
        logging.error(f"Ошибка {session_name}: {e}")
        try:
            await client.disconnect()
        except:
            pass
        return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔥 ПРОГРЕТЬ ВСЕ", callback_data="warmup_all"),
        InlineKeyboardButton(text="📊 СТАТИСТИКА", callback_data="stats"),
    )
    
    await message.answer(
        "<b>🔥 Account Warmer Bot</b>\n\n"
        "Прогрев Telegram аккаунтов:\n"
        "• Установка аватарок\n"
        "• Установка имён и био\n"
        "• Подписка на каналы\n"
        "• Имитация активности\n\n"
        "<b>Как использовать:</b>\n"
        "1. Отправь .session файлы\n"
        "2. Нажми «ПРОГРЕТЬ ВСЕ»\n"
        "3. Получи отчёт\n\n"
        "📁 Сессий загружено: <b>{}</b>".format(len(os.listdir("sessions"))),
        reply_markup=builder.as_markup()
    )

@dp.message(F.document)
async def handle_session(message: types.Message):
    """Загрузка .session файлов"""
    doc = message.document
    
    if not doc.file_name.endswith(".session"):
        return await message.reply("❌ Только .session файлы")
    
    file_path = f"sessions/{doc.file_name}"
    await bot.download(doc, file_path)
    
    count = len(os.listdir("sessions"))
    
    await message.reply(
        f"✅ <b>{doc.file_name}</b> загружен\n"
        f"📁 Всего сессий: <b>{count}</b>\n\n"
        f"Нажми /warmup чтобы начать прогрев",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("warmup"))
async def cmd_warmup(message: types.Message):
    await start_warmup(message.chat.id)

@dp.callback_query(F.data == "warmup_all")
async def warmup_callback(callback: types.CallbackQuery):
    await callback.answer()
    await start_warmup(callback.message.chat.id)

async def start_warmup(chat_id: int):
    sessions = [f for f in os.listdir("sessions") if f.endswith(".session")]
    
    if not sessions:
        return await bot.send_message(chat_id, "❌ Нет сессий. Загрузи .session файлы.")
    
    status_msg = await bot.send_message(
        chat_id,
        f"🔥 <b>Начинаю прогрев...</b>\n\n"
        f"📁 Сессий: {len(sessions)}\n"
        f"⏱ Примерное время: {len(sessions) * 30} сек",
        parse_mode=ParseMode.HTML
    )
    
    results = []
    success = 0
    failed = 0
    
    for i, session_file in enumerate(sessions, 1):
        session_path = f"sessions/{session_file}"
        
        try:
            await status_msg.edit_text(
                f"🔥 <b>Прогрев {i}/{len(sessions)}</b>\n\n"
                f"📁 {session_file}\n"
                f"⏳ Обрабатывается...",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        
        result = await warmup_account(session_path)
        
        if result:
            results.append(result)
            success += 1
        else:
            failed += 1
    
    # Формируем отчёт
    report = "<b>✅ ПРОГРЕВ ЗАВЕРШЁН!</b>\n\n"
    report += f"📊 Успешно: <b>{success}</b>\n"
    report += f"❌ Ошибок: <b>{failed}</b>\n\n"
    
    # Группируем по странам
    countries = {}
    for r in results:
        c = r["country"]
        if c not in countries:
            countries[c] = []
        countries[c].append(r)
    
    report += "<b>🌍 По странам:</b>\n"
    for country, accs in sorted(countries.items(), key=lambda x: -len(x[1])):
        report += f"\n<b>{country}</b> — {len(accs)} акк.\n"
        for acc in accs[:5]:  # Первые 5
            username = f"@{acc['username']}" if acc["username"] else "без юзернейма"
            report += f"  • {acc['first_name']} {acc['last_name']} | {username}\n"
        if len(accs) > 5:
            report += f"  <i>...и ещё {len(accs) - 5}</i>\n"
    
    report += f"\n<b>💀 Успешно прогрето: {success} аккаунтов</b>"
    
    # Отправляем
    if len(report) > 4000:
        parts = [report[i:i+4000] for i in range(0, len(report), 4000)]
        for part in parts:
            await bot.send_message(chat_id, part, parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id, report, parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "stats")
async def stats_callback(callback: types.CallbackQuery):
    sessions = [f for f in os.listdir("sessions") if f.endswith(".session")]
    
    await callback.message.edit_text(
        f"<b>📊 Статистика</b>\n\n"
        f"📁 Сессий в базе: {len(sessions)}\n"
        f"🌍 Каналов для подписки: {len(CHANNELS)}\n"
        f"👤 Имён: {len(FIRST_NAMES)}\n"
        f"📝 Био: {len(BIOS)}",
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    for f in os.listdir("sessions"):
        os.remove(f"sessions/{f}")
    await message.reply("🗑 Все сессии удалены")

@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    sessions = os.listdir("sessions")
    if not sessions:
        return await message.reply("📁 Нет сессий")
    
    text = f"<b>📁 Сессии ({len(sessions)})</b>\n\n"
    for s in sessions[:30]:
        text += f"• {s}\n"
    
    await message.reply(text, parse_mode=ParseMode.HTML)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Account Warmer запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
