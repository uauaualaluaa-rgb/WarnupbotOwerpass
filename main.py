import asyncio
import logging
import os
import random
import base64
import hashlib
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from telethon import TelegramClient, functions
from telethon.errors import FloodWaitError

logging.basicConfig(level=logging.WARNING)

BOT_TOKEN = "8862811439:AAGKNCDLKgfHnhxsKoTH3CuzaLfnPb659R4"
API_ID = 38387697
API_HASH = "e8fb7f7163498eb28231e45071fe92c0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESS_DIR = os.path.join(BASE_DIR, "sessions")
AVATAR_DIR = os.path.join(BASE_DIR, "avatars")
os.makedirs(SESS_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

for key, value in os.environ.items():
    if key.startswith("SESSION_") and key.endswith("_B64"):
        name = key.replace("SESSION_", "").replace("_B64", "").lower()
        path = os.path.join(SESS_DIR, f"{name}.session")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(base64.b64decode(value))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

CHANNELS = ["@durov", "@telegram", "@tginfo", "@telegramtips", "@contest", "@BotNews"]

# ========== КРЕАТИВНЫЕ ПРОФИЛИ ==========
# Каждая тема: имя, фамилия, био, юзер-паттерн, теги картинок
PROFILES = [
    # Аниме
    {"fn": "Sakura", "ln": "Chan", "bio": "аниме люблю больше чем людей 🌸", "un": ["sakura", "anime", "neko", "yuki", "rei"], "img": "anime"},
    {"fn": "Kirito", "ln": "Kun", "bio": "мир мечей и виртуальных снов ⚔️", "un": ["kirito", "asuna", "sao", "kirito"], "img": "anime"},
    {"fn": "Naruto", "ln": "Uz", "bio": "никогда не сдаваться 🍥", "un": ["naruto", "hokage", "uzumaki", "ninja"], "img": "anime"},
    {"fn": "Levi", "ln": "Ack", "bio": "титаны не спят 🗡️", "un": ["levi", "titan", "ackerman"], "img": "anime"},
    # Тачки
    {"fn": "Дмитрий", "ln": "Гонщиков", "bio": "JDM, дрифт и выхлоп 🔊", "un": ["drift", "jdm", "turbo", "gt86", "supra"], "img": "car"},
    {"fn": "Максим", "ln": "Турбо", "bio": "BMW M5 — это не машина, это жизнь 🏎️", "un": ["bmw", "m5", "amg", "rs6"], "img": "car"},
    {"fn": "Никита", "ln": "Спид", "bio": "скорость — мой наркотик ⚡", "un": ["speed", "race", "nitro"], "img": "car"},
    {"fn": "Артём", "ln": "Дрифт", "bio": "ночная трасса, красный свет, ты 🌃", "un": ["night", "racer", "drive"], "img": "car"},
    # Киберспорт
    {"fn": "Егор", "ln": "ProGamer", "bio": "CS2 3000 часов 🎯", "un": ["csgo", "cs2", "flick", "ez4", "headshot"], "img": "gaming"},
    {"fn": "Даниил", "ln": "Тимплей", "bio": "Dota 2 / Valorant / CS2 🎮", "un": ["dota", "val", "valor", "gg"], "img": "gaming"},
    {"fn": "Кирилл", "ln": "Комбо", "bio": "фармлю ммр и нервы 🧠", "un": ["mmr", "rank", "top1"], "img": "gaming"},
    # Фото/творчество
    {"fn": "Алексей", "ln": "Фотографов", "bio": "вижу мир через объектив 📸", "un": ["photo", "shot", "lens", "foto"], "img": "photo"},
    {"fn": "Роман", "ln": "Художник", "bio": "рисую то, что вижу во сне 🎨", "un": ["art", "draw", "pixel", "sketch"], "img": "photo"},
    # Спорт
    {"fn": "Иван", "ln": "Качков", "bio": "жим 120, тяга 150, присед 180 💪", "un": ["gym", "fit", "iron", "power"], "img": "sport"},
    {"fn": "Сергей", "ln": "Боксёров", "bio": "быстрее, выше, сильнее 🥊", "un": ["box", "fight", "mma", "ufc"], "img": "sport"},
    # Музыка
    {"fn": "Андрей", "ln": "Битмейкер", "bio": "делаю биты ночью 🎧", "un": ["beat", "producer", "flstudio", "ableton"], "img": "music"},
    {"fn": "Павел", "ln": "Гитарист", "bio": "рок жив 🎸", "un": ["rock", "guitar", "metal", "punk"], "img": "music"},
    # Путешествия
    {"fn": "Владислав", "ln": "Путешественников", "bio": "страны, города, люди ✈️", "un": ["travel", "trip", "world", "map"], "img": "travel"},
    # Технологии
    {"fn": "Максим", "ln": "Разработчиков", "bio": "код, кофе, сон (не по порядку) 💻", "un": ["dev", "code", "python", "js"], "img": "tech"},
    {"fn": "Егор", "ln": "Хакеров", "bio": "иногда ломаю, чаще чиню 🔐", "un": ["hack", "cyber", "sec", "net"], "img": "tech"},
]

# ========== ЗАГРУЗКА АВАТАРОК С ИНТЕРНЕТА ==========
async def download_avatar(tag: str) -> str:
    """
    Скачивает случайную картинку с бесплатных источников.
    Возвращает путь к локальному файлу.
    """
    import aiohttp
    
    # Источники по тегам
    sources = {
        "anime": [
            "https://nekos.life/api/v2/img/neko",
            "https://api.waifu.pics/sfw/waifu",
            "https://api.waifu.pics/sfw/neko",
        ],
        "car": [
            "https://api.unsplash.com/photos/random?query=car&client_id=demo",
            "https://source.unsplash.com/512x512/?car,auto",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
        "gaming": [
            "https://source.unsplash.com/512x512/?gaming,esports",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
        "photo": [
            "https://source.unsplash.com/512x512/?photography,camera",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
        "sport": [
            "https://source.unsplash.com/512x512/?sport,gym",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
        "music": [
            "https://source.unsplash.com/512x512/?music,guitar",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
        "travel": [
            "https://source.unsplash.com/512x512/?travel,landscape",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
        "tech": [
            "https://source.unsplash.com/512x512/?technology,computer",
            "https://picsum.photos/512/512?random=" + str(random.randint(1,9999)),
        ],
    }
    
    urls = sources.get(tag, ["https://picsum.photos/512/512"])
    
    for url in urls:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=10, allow_redirects=True) as resp:
                    if resp.status == 200:
                        content_type = resp.headers.get("Content-Type", "")
                        if "json" in content_type:
                            # JSON API (waifu, neko)
                            data = await resp.json()
                            img_url = data.get("url") or data.get("link")
                            if img_url:
                                async with s.get(img_url, timeout=10) as img_resp:
                                    if img_resp.status == 200:
                                        data_bytes = await img_resp.read()
                                        path = os.path.join(AVATAR_DIR, f"av_{random.randint(100000,999999)}.jpg")
                                        with open(path, "wb") as f:
                                            f.write(data_bytes)
                                        return path
                        elif "image" in content_type:
                            data_bytes = await resp.read()
                            if len(data_bytes) > 1000:
                                path = os.path.join(AVATAR_DIR, f"av_{random.randint(100000,999999)}.jpg")
                                with open(path, "wb") as f:
                                    f.write(data_bytes)
                                return path
        except Exception as e:
            logging.warning(f"Avatar download error ({url}): {e}")
            continue
    
    return None

def get_country_from_phone(phone: str) -> str:
    codes = {
        "+7": "Россия/Казахстан", "+375": "Беларусь", "+380": "Украина",
        "+77": "Казахстан", "+996": "Киргизия", "+998": "Узбекистан",
        "+994": "Азербайджан", "+995": "Грузия", "+373": "Молдова",
        "+371": "Латвия", "+370": "Литва", "+372": "Эстония",
        "+48": "Польша", "+49": "Германия", "+1": "США/Канада",
        "+44": "Великобритания", "+90": "Турция", "+33": "Франция",
    }
    if not phone:
        return "Неизвестно"
    for code, country in sorted(codes.items(), key=lambda x: -len(x[0])):
        if phone.startswith(code):
            return country
    return "Неизвестно"

def build_username(profile: dict) -> str:
    """Собирает креативный юзернейм"""
    base = random.choice(profile["un"])
    suffix = random.choice([
        str(random.randint(10, 999)),
        str(random.randint(1000, 9999)),
        "_" + str(random.randint(10, 99)),
        str(random.randint(10, 99)) + "x",
        "off", "real", "pro", "x", "xx",
    ])
    return f"{base}{suffix}"

async def setup_profile(client: TelegramClient, profile: dict):
    try:
        # Имя/фамилия
        await client(functions.account.UpdateProfileRequest(
            first_name=profile["fn"],
            last_name=profile["ln"]
        ))
        await asyncio.sleep(0.5)
        
        # Био
        await client(functions.account.UpdateProfileRequest(about=profile["bio"]))
        await asyncio.sleep(0.5)
        
        # Аватарка
        avatar_path = await download_avatar(profile["img"])
        if avatar_path and os.path.exists(avatar_path):
            try:
                await client(functions.photos.UploadProfilePhotoRequest(
                    file=await client.upload_file(avatar_path)
                ))
            except Exception as e:
                logging.warning(f"Avatar upload: {e}")
            finally:
                try:
                    os.remove(avatar_path)
                except:
                    pass
        
        # Юзернейм
        username = None
        for _ in range(10):
            u = build_username(profile)
            try:
                await client(functions.account.UpdateUsernameRequest(username=u))
                username = u
                break
            except Exception as e:
                if "USERNAME_OCCUPIED" in str(e) or "USERNAME_INVALID" in str(e):
                    continue
                break
        
        return profile["fn"], profile["ln"], username, profile["bio"]
    except Exception as e:
        logging.error(f"Setup error: {e}")
        return None, None, None, None

async def subscribe_channels(client: TelegramClient):
    count = 0
    for ch in CHANNELS:
        try:
            await client(functions.channels.JoinChannelRequest(channel=ch))
            count += 1
            await asyncio.sleep(random.randint(1, 3))
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except:
            pass
    return count

async def warmup_account(session_name: str):
    path = os.path.join(SESS_DIR, session_name)
    client = TelegramClient(path, API_ID, API_HASH)
    result = {"session": session_name, "success": False}
    
    profile = random.choice(PROFILES)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            result["error"] = "NOT_AUTHORIZED"
            return result
        
        me = await client.get_me()
        country = get_country_from_phone(me.phone)
        
        fn, ln, un, bio = await setup_profile(client, profile)
        subs = await subscribe_channels(client)
        
        result.update({
            "success": True,
            "phone": me.phone,
            "user_id": me.id,
            "first_name": fn or me.first_name,
            "last_name": ln or "",
            "username": un,
            "country": country,
            "bio": bio,
            "subs": subs,
            "theme": profile["img"],
        })
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        try:
            await client.disconnect()
        except:
            pass
    return result

warmup_stats = {"success": 0, "failed": 0, "results": []}

async def run_warmup(chat_id: int, status_msg: types.Message):
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    if not sessions:
        return await status_msg.edit_text("❌ Нет сессий.")
    
    total = len(sessions)
    warmup_stats["success"] = 0
    warmup_stats["failed"] = 0
    warmup_stats["results"] = []
    
    await status_msg.edit_text(
        f"🔥 <b>Прогрев запущен</b>\n\n"
        f"📁 Сессий: {total}\n"
        f"⚡ Параллельно: 8\n"
        f"🎨 Темы: аниме, тачки, гейминг, спорт, музыка, фото, путешествия, техно"
    )
    
    sem = asyncio.Semaphore(8)
    
    async def worker(session_file, i):
        async with sem:
            r = await warmup_account(session_file)
            warmup_stats["results"].append(r)
            if r.get("success"):
                warmup_stats["success"] += 1
            else:
                warmup_stats["failed"] += 1
            try:
                icon = "✅" if r.get("success") else "❌"
                theme_icons = {"anime":"🌸","car":"🏎️","gaming":"🎮","photo":"📸","sport":"💪","music":"🎸","travel":"✈️","tech":"💻"}
                theme = theme_icons.get(r.get("theme",""), "👤")
                await status_msg.edit_text(
                    f"🔥 <b>Прогрев {i}/{total}</b>\n\n"
                    f"{icon} {session_file}\n"
                    f"{theme} {r.get('first_name','—')} {r.get('last_name','')}\n"
                    f"🌍 {r.get('country','—')}\n"
                    f"🆔 @{r.get('username','—')}\n"
                    f"📝 {r.get('bio','—')[:40]}\n\n"
                    f"✅ Успешно: {warmup_stats['success']} | ❌ Ошибок: {warmup_stats['failed']}"
                )
            except:
                pass
    
    await asyncio.gather(*[worker(s, i) for i, s in enumerate(sessions, 1)])
    
    results = warmup_stats["results"]
    success = [r for r in results if r.get("success")]
    
    report = f"<b>✅ ПРОГРЕВ ЗАВЕРШЁН</b>\n\n"
    report += f"📊 Успешно: <b>{len(success)}</b>\n"
    report += f"❌ Ошибок: <b>{warmup_stats['failed']}</b>\n\n"
    
    if success:
        # По темам
        themes = {}
        for r in success:
            themes.setdefault(r.get("theme", "other"), []).append(r)
        
        icons = {"anime":"🌸","car":"🏎️","gaming":"🎮","photo":"📸","sport":"💪","music":"🎸","travel":"✈️","tech":"💻"}
        report += "<b>🎨 По темам:</b>\n"
        for t, accs in themes.items():
            report += f"{icons.get(t,'👤')} {t}: {len(accs)}\n"
        
        report += "\n<b>🌍 По странам:</b>\n"
        countries = {}
        for r in success:
            countries.setdefault(r["country"], []).append(r)
        for c, accs in sorted(countries.items(), key=lambda x: -len(x[1])):
            report += f"<b>{c}</b> — {len(accs)}\n"
        
        # Полный список
        report += "\n<b>📋 ВСЕ АККАУНТЫ:</b>\n"
        for r in success:
            un = f"@{r['username']}" if r.get("username") else "—"
            report += f"• {r.get('first_name','')} {r.get('last_name','')} | {un} | +{r.get('phone','')} | {r.get('country','')}\n"
    
    failed = [r for r in results if not r.get("success")]
    if failed:
        report += "\n<b>❌ Ошибки:</b>\n"
        for r in failed[:10]:
            report += f"• {r['session']}: {r.get('error','?')[:70]}\n"
    
    for i in range(0, len(report), 4000):
        await bot.send_message(chat_id, report[i:i+4000], parse_mode=ParseMode.HTML)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔥 ПРОГРЕТЬ ВСЕ", callback_data="warmup_all"))
    b.row(
        InlineKeyboardButton(text="📊 СТАТЫ", callback_data="stats"),
        InlineKeyboardButton(text="📁 СПИСОК", callback_data="list"),
    )
    count = len([f for f in os.listdir(SESS_DIR) if f.endswith(".session")])
    await message.answer(
        f"<b>🔥 Account Warmer v2</b>\n\n"
        f"📁 Сессий: <b>{count}</b>\n"
        f"🎨 Темы: аниме, тачки, гейминг, спорт, музыка, фото, путешествия, техно\n"
        f"🖼 Аватарки: с интернета\n\n"
        f"<code>/warmup</code> — прогреть\n"
        f"<code>/list</code> — список\n"
        f"<code>/clear</code> — очистить",
        reply_markup=b.as_markup()
    )

@dp.message(F.document)
async def handle_session(message: types.Message):
    doc = message.document
    if not doc.file_name.endswith(".session"):
        return await message.reply("❌ Только .session")
    await bot.download(doc, os.path.join(SESS_DIR, doc.file_name))
    count = len([f for f in os.listdir(SESS_DIR) if f.endswith(".session")])
    await message.reply(f"✅ {doc.file_name} загружен\n📁 Всего: {count}")

@dp.message(Command("warmup"))
async def cmd_warmup(message: types.Message):
    msg = await message.reply("🔥 Запускаю...")
    await run_warmup(message.chat.id, msg)

@dp.callback_query(F.data == "warmup_all")
async def cb_warmup(cb: types.CallbackQuery):
    await cb.answer()
    await run_warmup(cb.message.chat.id, cb.message)

@dp.callback_query(F.data == "stats")
async def cb_stats(cb: types.CallbackQuery):
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    themes = set(p["img"] for p in PROFILES)
    await cb.message.edit_text(
        f"<b>📊 Статистика</b>\n\n"
        f"📁 Сессий: {len(sessions)}\n"
        f"🎨 Тем: {len(themes)} ({', '.join(themes)})\n"
        f"👤 Профилей: {len(PROFILES)}\n"
        f"🌍 Каналов: {len(CHANNELS)}"
    )
    await cb.answer()

@dp.callback_query(F.data == "list")
async def cb_list(cb: types.CallbackQuery):
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    if not sessions:
        return await cb.message.edit_text("📁 Нет сессий")
    text = f"<b>📁 Сессии ({len(sessions)})</b>\n\n"
    for s in sessions[:40]:
        text += f"• <code>{s}</code>\n"
    await cb.message.edit_text(text)
    await cb.answer()

@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    if not sessions:
        return await message.reply("📁 Нет сессий")
    text = f"<b>📁 Сессии ({len(sessions)})</b>\n\n"
    for s in sessions[:40]:
        text += f"• <code>{s}</code>\n"
    await message.reply(text)

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    for f in os.listdir(SESS_DIR):
        os.remove(os.path.join(SESS_DIR, f))
    await message.reply("🗑 Сессии удалены")

async def main():
    print("Account Warmer v2 запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
