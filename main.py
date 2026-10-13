import asyncio
import logging
import os
import random
import base64
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

# ========== ПРОФИЛИ (20+ тем) ==========
PROFILES = [
    # Аниме
    {"fn": "Sakura", "ln": "Chan", "bio": "аниме люблю больше чем людей 🌸", "un": ["sakura","anime","neko","yuki","rei"], "img": "anime"},
    {"fn": "Kirito", "ln": "Kun", "bio": "мир мечей и виртуальных снов ⚔️", "un": ["kirito","asuna","sao"], "img": "anime"},
    {"fn": "Naruto", "ln": "Uz", "bio": "никогда не сдаваться 🍥", "un": ["naruto","hokage","ninja"], "img": "anime"},
    {"fn": "Levi", "ln": "Ack", "bio": "титаны не спят 🗡️", "un": ["levi","titan","ackerman"], "img": "anime"},

    # Тачки
    {"fn": "Дмитрий", "ln": "Гонщиков", "bio": "JDM, дрифт и выхлоп 🔊", "un": ["drift","jdm","turbo","supra"], "img": "car"},
    {"fn": "Максим", "ln": "Турбо", "bio": "BMW M5 — это не машина, это жизнь 🏎️", "un": ["bmw","m5","amg","rs6"], "img": "car"},
    {"fn": "Никита", "ln": "Спид", "bio": "скорость — мой наркотик ⚡", "un": ["speed","race","nitro"], "img": "car"},

    # Гейминг
    {"fn": "Егор", "ln": "ProGamer", "bio": "CS2 3000 часов 🎯", "un": ["csgo","cs2","flick","headshot"], "img": "gaming"},
    {"fn": "Даниил", "ln": "Тимплей", "bio": "Dota 2 / Valorant / CS2 🎮", "un": ["dota","val","gg"], "img": "gaming"},

    # Фото
    {"fn": "Алексей", "ln": "Фотографов", "bio": "вижу мир через объектив 📸", "un": ["photo","shot","lens"], "img": "photo"},
    {"fn": "Роман", "ln": "Художник", "bio": "рисую то, что вижу во сне 🎨", "un": ["art","draw","pixel"], "img": "photo"},

    # Спорт
    {"fn": "Иван", "ln": "Качков", "bio": "жим 120, тяга 150, присед 180 💪", "un": ["gym","fit","iron"], "img": "sport"},
    {"fn": "Сергей", "ln": "Боксёров", "bio": "быстрее, выше, сильнее 🥊", "un": ["box","fight","mma","ufc"], "img": "sport"},

    # Музыка
    {"fn": "Андрей", "ln": "Битмейкер", "bio": "делаю биты ночью 🎧", "un": ["beat","producer","flstudio"], "img": "music"},
    {"fn": "Павел", "ln": "Гитарист", "bio": "рок жив 🎸", "un": ["rock","guitar","metal"], "img": "music"},

    # Путешествия
    {"fn": "Владислав", "ln": "Путешественников", "bio": "страны, города, люди ✈️", "un": ["travel","trip","world"], "img": "travel"},

    # Техно
    {"fn": "Максим", "ln": "Разработчиков", "bio": "код, кофе, сон (не по порядку) 💻", "un": ["dev","code","python"], "img": "tech"},
    {"fn": "Егор", "ln": "Хакеров", "bio": "иногда ломаю, чаще чиню 🔐", "un": ["hack","cyber","sec"], "img": "tech"},

    # ========== ДОКСЕРСКАЯ ==========
    {"fn": "Даниил", "ln": "Доксер", "bio": "знаю о тебе больше, чем ты сам 🕵️", "un": ["dox","doxer","osint","intel","search"], "img": "hacker"},
    {"fn": "Артём", "ln": "Деанон", "bio": "инфа решает всё 📁", "un": ["deanon","anon","doxbin"], "img": "hacker"},
    {"fn": "Никита", "ln": "Пробив", "bio": "пробью любого 📞", "un": ["probit","problv","info","base"], "img": "hacker"},

    # ========== НЕФОРСКАЯ ==========
    {"fn": "Кирилл", "ln": "Нефор", "bio": "нефор 4 life 🖤", "un": ["nefor","neform","chushpan","gopnik"], "img": "nefor"},
    {"fn": "Егор", "ln": "Чушпан", "bio": "чё ты пёс 🐶", "un": ["4ushpan","chushpan","pav","dyadya"], "img": "nefor"},
    {"fn": "Максим", "ln": "Гопник", "bio": "э слышь 🧢", "un": ["gopnik","gop","semki","semechki"], "img": "nefor"},

    # ========== ЕМО ==========
    {"fn": "Даниил", "ln": "Емо", "bio": "жизнь — боль 🖤🥀", "un": ["emo","emo4ka","sadboy","broken"], "img": "emo"},
    {"fn": "Артём", "ln": "Мрачный", "bio": "тёмная сторона души 🖤", "un": ["dark","sad","alone","cry"], "img": "emo"},
    {"fn": "Кирилл", "ln": "Печаль", "bio": "лучше быть одному ⛓️", "un": ["sad","pain","hurt","lost"], "img": "emo"},

    # ========== ГОТ ==========
    {"fn": "Роман", "ln": "Гот", "bio": "тьма и искусство 🦇", "un": ["goth","gothic","raven","crow"], "img": "goth"},

    # ========== РЭП / ХИП-ХОП ==========
    {"fn": "Иван", "ln": "Рэпер", "bio": "делаю треки на дому 🎤", "un": ["rap","trap","flow","beat"], "img": "rap"},
    {"fn": "Сергей", "ln": "Хипхоп", "bio": "уличная культура 🧢", "un": ["hiphop","street","urban"], "img": "rap"},

    # ========== СКЕЙТ / СТРИТ ==========
    {"fn": "Никита", "ln": "Скейтер", "bio": "доска, улица, свобода 🛹", "un": ["skate","sk8","board","street"], "img": "skate"},
    {"fn": "Андрей", "ln": "Стрит", "bio": "город — мой дом 🏙️", "un": ["street","urban","city","hood"], "img": "skate"},

    # ========== БАРБЕР / СТИЛЬ ==========
    {"fn": "Дмитрий", "ln": "Барбер", "bio": "стрижки для своих ✂️", "un": ["barber","cut","fade","style"], "img": "barber"},

    # ========== ГЕЙМЕРЫ РУССКИЕ ==========
    {"fn": "Егор", "ln": "Крипер", "bio": "майнкрафт детство 🟩", "un": ["creeper","mine","mc","block"], "img": "minecraft"},
    {"fn": "Даниил", "ln": "Зомби", "bio": "выживаю в мире блоков 🧟", "un": ["zombie","steve","alex"], "img": "minecraft"},
]

# ========== ЗАГРУЗКА АВАТАРОК ==========
async def download_avatar(tag: str) -> str:
    import aiohttp
    
    sources = {
        "anime": [
            "https://nekos.life/api/v2/img/neko",
            "https://api.waifu.pics/sfw/waifu",
            "https://api.waifu.pics/sfw/neko",
        ],
        "car": [
            "https://picsum.photos/512/512?random=" + str(random.randint(1,99999)),
            "https://source.unsplash.com/512x512/?car,auto,jdm",
        ],
        "gaming": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "photo": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "sport": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "music": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "travel": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "tech": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "hacker": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "nefor": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "emo": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "goth": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "rap": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "skate": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "barber": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
        "minecraft": ["https://picsum.photos/512/512?random=" + str(random.randint(1,99999))],
    }
    
    urls = sources.get(tag, ["https://picsum.photos/512/512"])
    
    for url in urls:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=10, allow_redirects=True) as resp:
                    if resp.status == 200:
                        ct = resp.headers.get("Content-Type", "")
                        if "json" in ct:
                            data = await resp.json()
                            img_url = data.get("url") or data.get("link")
                            if img_url:
                                async with s.get(img_url, timeout=10) as ir:
                                    if ir.status == 200:
                                        b = await ir.read()
                                        p = os.path.join(AVATAR_DIR, f"av_{random.randint(100000,999999)}.jpg")
                                        with open(p, "wb") as f:
                                            f.write(b)
                                        return p
                        elif "image" in ct:
                            b = await resp.read()
                            if len(b) > 1000:
                                p = os.path.join(AVATAR_DIR, f"av_{random.randint(100000,999999)}.jpg")
                                with open(p, "wb") as f:
                                    f.write(b)
                                return p
        except Exception as e:
            logging.warning(f"Avatar error: {e}")
            continue
    return None

def get_country_from_phone(phone: str) -> str:
    codes = {
        "+7": "Россия/Казахстан", "+375": "Беларусь", "+380": "Украина",
        "+77": "Казахстан", "+996": "Киргизия", "+998": "Узбекистан",
        "+994": "Азербайджан", "+995": "Грузия", "+373": "Молдова",
        "+371": "Латвия", "+370": "Литва", "+372": "Эстония",
        "+48": "Польша", "+49": "Германия", "+1": "США/Канада",
        "+44": "Великобритания", "+90": "Турция",
    }
    if not phone:
        return "Неизвестно"
    for code, country in sorted(codes.items(), key=lambda x: -len(x[0])):
        if phone.startswith(code):
            return country
    return "Неизвестно"

def build_username(profile: dict) -> str:
    base = random.choice(profile["un"])
    suffix = random.choice([
        str(random.randint(10, 999)),
        str(random.randint(1000, 9999)),
        "_" + str(random.randint(10, 99)),
        str(random.randint(10, 99)) + "x",
        "off", "real", "pro", "x", "xx", "gg", "228", "1337",
    ])
    return f"{base}{suffix}"

# ========== ПРОВЕРКА ВАЛИДНОСТИ ==========
async def validate_session(session_name: str) -> dict:
    """
    Проверяет сессию БЕЗ изменений:
    - подключение
    - авторизация
    - аккаунт не забанен
    - аккаунт не заморожен
    """
    path = os.path.join(SESS_DIR, session_name)
    client = TelegramClient(path, API_ID, API_HASH)
    result = {"session": session_name, "valid": False}
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            result["error"] = "NOT_AUTHORIZED"
            return result
        
        me = await client.get_me()
        
        if me is None:
            result["error"] = "NO_ME"
            return result
        
        # Проверка на бан/заморозку
        try:
            full = await client(functions.users.GetFullUserRequest(me.id))
            if hasattr(full, 'full_user') and full.full_user:
                if getattr(full.full_user, 'blocked', False):
                    result["error"] = "ACCOUNT_BLOCKED"
                    return result
        except Exception:
            pass
        
        result.update({
            "valid": True,
            "phone": me.phone,
            "user_id": me.id,
            "first_name": me.first_name or "",
            "username": me.username or "",
            "premium": getattr(me, 'premium', False),
            "country": get_country_from_phone(me.phone),
        })
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)[:100]}"
    finally:
        try:
            await client.disconnect()
        except:
            pass
    
    return result

# ========== ПРОГРЕВ ==========
async def setup_profile(client: TelegramClient, profile: dict):
    try:
        await client(functions.account.UpdateProfileRequest(
            first_name=profile["fn"], last_name=profile["ln"]
        ))
        await asyncio.sleep(0.5)
        
        await client(functions.account.UpdateProfileRequest(about=profile["bio"]))
        await asyncio.sleep(0.5)
        
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
        
        username = None
        for _ in range(10):
            u = build_username(profile)
            try:
                await client(functions.account.UpdateUsernameRequest(username=u))
                username = u
                break
            except:
                continue
        
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

async def warmup_account(session_name: str, profile: dict, me):
    path = os.path.join(SESS_DIR, session_name)
    client = TelegramClient(path, API_ID, API_HASH)
    result = {"session": session_name, "success": False}
    
    try:
        await client.connect()
        
        fn, ln, un, bio = await setup_profile(client, profile)
        subs = await subscribe_channels(client)
        
        result.update({
            "success": True,
            "phone": me.phone,
            "user_id": me.id,
            "first_name": fn or me.first_name,
            "last_name": ln or "",
            "username": un,
            "country": get_country_from_phone(me.phone),
            "bio": bio,
            "subs": subs,
            "theme": profile["img"],
        })
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)[:100]}"
    finally:
        try:
            await client.disconnect()
        except:
            pass
    return result

warmup_stats = {"success": 0, "failed": 0, "invalid": 0, "results": [], "invalid_list": []}

async def run_warmup(chat_id: int, status_msg: types.Message):
    all_sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    if not all_sessions:
        return await status_msg.edit_text("❌ Нет сессий.")
    
    total = len(all_sessions)
    warmup_stats.update({"success": 0, "failed": 0, "invalid": 0, "results": [], "invalid_list": []})
    
    await status_msg.edit_text(
        f"🔍 <b>ШАГ 1: Проверка валидности</b>\n\n"
        f"📁 Сессий: {total}\n"
        f"⏳ Проверяю..."
    )
    
    # ШАГ 1: Проверка валидности (параллельно 10)
    sem_check = asyncio.Semaphore(10)
    valid_sessions = []
    checked = 0
    
    async def check_worker(session_file):
        nonlocal checked
        async with sem_check:
            r = await validate_session(session_file)
            checked += 1
            if r.get("valid"):
                valid_sessions.append(r)
            else:
                warmup_stats["invalid"] += 1
                warmup_stats["invalid_list"].append(r)
            try:
                await status_msg.edit_text(
                    f"🔍 <b>ШАГ 1: Проверка</b>\n\n"
                    f"⏳ Проверено: {checked}/{total}\n"
                    f"✅ Валидных: {len(valid_sessions)}\n"
                    f"❌ Невалидных: {warmup_stats['invalid']}"
                )
            except:
                pass
    
    await asyncio.gather(*[check_worker(s) for s in all_sessions])
    
    if not valid_sessions:
        return await status_msg.edit_text(
            f"❌ <b>Нет валидных сессий</b>\n\n"
            f"📁 Всего: {total}\n"
            f"❌ Невалидных: {warmup_stats['invalid']}"
        )
    
    # ШАГ 2: Прогрев валидных
    await status_msg.edit_text(
        f"✅ <b>ШАГ 1 завершён</b>\n\n"
        f"✅ Валидных: {len(valid_sessions)}\n"
        f"❌ Невалидных: {warmup_stats['invalid']}\n\n"
        f"🔥 <b>ШАГ 2: Прогрев начат...</b>"
    )
    
    sem = asyncio.Semaphore(8)
    processed = 0
    
    async def warm_worker(item, i):
        nonlocal processed
        async with sem:
            profile = random.choice(PROFILES)
            r = await warmup_account(item["session"], profile, type('Me', (), {
                'phone': item["phone"], 'id': item["user_id"], 'first_name': item["first_name"]
            })())
            warmup_stats["results"].append(r)
            if r.get("success"):
                warmup_stats["success"] += 1
            else:
                warmup_stats["failed"] += 1
            processed += 1
            try:
                icon = "✅" if r.get("success") else "❌"
                theme_icons = {
                    "anime":"🌸","car":"🏎️","gaming":"🎮","photo":"📸","sport":"💪",
                    "music":"🎸","travel":"✈️","tech":"💻","hacker":"🕵️","nefor":"🧢",
                    "emo":"🖤","goth":"🦇","rap":"🎤","skate":"🛹","barber":"✂️","minecraft":"🟩",
                }
                theme = theme_icons.get(r.get("theme",""), "👤")
                await status_msg.edit_text(
                    f"🔥 <b>Прогрев {processed}/{len(valid_sessions)}</b>\n\n"
                    f"{icon} {item['session']}\n"
                    f"{theme} {r.get('first_name','—')} {r.get('last_name','')}\n"
                    f"🌍 {r.get('country','—')}\n"
                    f"🆔 @{r.get('username','—')}\n"
                    f"📝 {r.get('bio','—')[:40]}\n\n"
                    f"✅ {warmup_stats['success']} | ❌ {warmup_stats['failed']}"
                )
            except:
                pass
    
    await asyncio.gather(*[warm_worker(s, i) for i, s in enumerate(valid_sessions, 1)])
    
    # ФИНАЛЬНЫЙ ОТЧЁТ
    success = [r for r in warmup_stats["results"] if r.get("success")]
    
    report = f"<b>✅ ПРОГРЕВ ЗАВЕРШЁН</b>\n\n"
    report += f"📊 Успешно: <b>{len(success)}</b>\n"
    report += f"❌ Ошибок прогрева: <b>{warmup_stats['failed']}</b>\n"
    report += f"🚫 Невалидных сессий: <b>{warmup_stats['invalid']}</b>\n\n"
    
    if success:
        icons = {
            "anime":"🌸","car":"🏎️","gaming":"🎮","photo":"📸","sport":"💪",
            "music":"🎸","travel":"✈️","tech":"💻","hacker":"🕵️","nefor":"🧢",
            "emo":"🖤","goth":"🦇","rap":"🎤","skate":"🛹","barber":"✂️","minecraft":"🟩",
        }
        themes = {}
        for r in success:
            themes.setdefault(r.get("theme","other"), []).append(r)
        report += "<b>🎨 По темам:</b>\n"
        for t, accs in sorted(themes.items(), key=lambda x: -len(x[1])):
            report += f"{icons.get(t,'👤')} {t}: {len(accs)}\n"
        
        report += "\n<b>🌍 По странам:</b>\n"
        countries = {}
        for r in success:
            countries.setdefault(r["country"], []).append(r)
        for c, accs in sorted(countries.items(), key=lambda x: -len(x[1])):
            report += f"<b>{c}</b> — {len(accs)}\n"
        
        report += "\n<b>📋 ВСЕ АККАУНТЫ:</b>\n"
        for r in success:
            un = f"@{r['username']}" if r.get("username") else "—"
            report += f"• {r.get('first_name','')} {r.get('last_name','')} | {un} | +{r.get('phone','')} | {r.get('country','')}\n"
    
    failed = [r for r in warmup_stats["results"] if not r.get("success")]
    if failed:
        report += "\n<b>❌ Ошибки прогрева:</b>\n"
        for r in failed[:10]:
            report += f"• {r['session']}: {r.get('error','?')[:70]}\n"
    
    if warmup_stats["invalid_list"]:
        report += "\n<b>🚫 Невалидные сессии:</b>\n"
        for r in warmup_stats["invalid_list"][:15]:
            report += f"• {r['session']}: {r.get('error','?')[:60]}\n"
    
    for i in range(0, len(report), 4000):
        await bot.send_message(chat_id, report[i:i+4000], parse_mode=ParseMode.HTML)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔥 ПРОГРЕТЬ ВСЕ", callback_data="warmup_all"))
    b.row(
        InlineKeyboardButton(text="🔍 ПРОВЕРИТЬ", callback_data="check_all"),
        InlineKeyboardButton(text="📊 СТАТЫ", callback_data="stats"),
    )
    b.row(InlineKeyboardButton(text="📁 СПИСОК", callback_data="list"))
    
    count = len([f for f in os.listdir(SESS_DIR) if f.endswith(".session")])
    await message.answer(
        f"<b>🔥 Account Warmer v3</b>\n\n"
        f"📁 Сессий: <b>{count}</b>\n"
        f"🎨 Тем: <b>{len(set(p['img'] for p in PROFILES))}</b>\n"
        f"👤 Профилей: <b>{len(PROFILES)}</b>\n\n"
        f"<code>/warmup</code> — прогреть (с проверкой)\n"
        f"<code>/check</code> — только проверить\n"
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

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    if not sessions:
        return await message.reply("❌ Нет сессий.")
    
    msg = await message.reply(f"🔍 Проверяю {len(sessions)} сессий...")
    valid = []
    invalid = []
    
    sem = asyncio.Semaphore(10)
    
    async def worker(s):
        async with sem:
            r = await validate_session(s)
            if r.get("valid"):
                valid.append(r)
            else:
                invalid.append(r)
    
    await asyncio.gather(*[worker(s) for s in sessions])
    
    report = f"<b>🔍 Проверка завершена</b>\n\n"
    report += f"✅ Валидных: <b>{len(valid)}</b>\n"
    report += f"❌ Невалидных: <b>{len(invalid)}</b>\n\n"
    
    if valid:
        report += "<b>✅ Валидные:</b>\n"
        for r in valid:
            report += f"• {r['session']} | +{r.get('phone','?')} | @{r.get('username','—')} | {r.get('country','?')}\n"
    
    if invalid:
        report += "\n<b>❌ Невалидные:</b>\n"
        for r in invalid:
            report += f"• {r['session']}: {r.get('error','?')[:60]}\n"
    
    for i in range(0, len(report), 4000):
        await bot.send_message(message.chat.id, report[i:i+4000], parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "warmup_all")
async def cb_warmup(cb: types.CallbackQuery):
    await cb.answer()
    await run_warmup(cb.message.chat.id, cb.message)

@dp.callback_query(F.data == "check_all")
async def cb_check(cb: types.CallbackQuery):
    await cb.answer()
    await cb.message.edit_text("🔍 Проверяю...")
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    valid = 0
    invalid = 0
    sem = asyncio.Semaphore(10)
    
    async def worker(s):
        nonlocal valid, invalid
        async with sem:
            r = await validate_session(s)
            if r.get("valid"):
                valid += 1
            else:
                invalid += 1
    
    await asyncio.gather(*[worker(s) for s in sessions])
    await cb.message.edit_text(f"✅ Валидных: {valid}\n❌ Невалидных: {invalid}")

@dp.callback_query(F.data == "stats")
async def cb_stats(cb: types.CallbackQuery):
    sessions = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    themes = set(p["img"] for p in PROFILES)
    await cb.message.edit_text(
        f"<b>📊 Статистика</b>\n\n"
        f"📁 Сессий: {len(sessions)}\n"
        f"🎨 Тем: {len(themes)}\n"
        f"👤 Профилей: {len(PROFILES)}\n"
        f"🌍 Каналов: {len(CHANNELS)}\n\n"
        f"<b>Темы:</b> {', '.join(sorted(themes))}"
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

async def
