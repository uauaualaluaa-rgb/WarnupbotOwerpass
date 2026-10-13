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
from telethon.tl.types import InputPeerChannel

logging.basicConfig(level=logging.WARNING)

BOT_TOKEN = "8862811439:AAGKNCDLKgfHnhxsKoTH3CuzaLfnPb659R4"
API_ID = 38387697
API_HASH = "e8fb7f7163498eb28231e45071fe92c0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(SESS_DIR, exist_ok=True)

# Восстановление сессий из base64 (для хостинга)
for key, value in os.environ.items():
    if key.startswith("SESSION_") and key.endswith("_B64"):
        name = key.replace("SESSION_", "").replace("_B64", "").lower()
        path = os.path.join(SESS_DIR, f"{name}.session")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(base64.b64decode(value))
            print(f"Восстановлена: {name}")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

CHANNELS = ["@durov", "@telegram", "@tginfo", "@telegramtips", "@contest", "@BotNews", "@TelegramEU"]

FIRST_NAMES = ["Алексей", "Дмитрий", "Сергей", "Андрей", "Максим", "Иван", "Никита", "Артём", "Кирилл", "Егор", "Роман", "Даниил"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Попов", "Волков", "Морозов", "Новиков", "Фёдоров"]
USERNAME_PREFIX = ["user", "acc", "real", "person", "human", "tg", "man", "prvt", "id", "prof"]

BIOS = [
    "Люблю путешествия ✈️", "Просто человек 🌍", "Фотограф 📸",
    "Программист 💻", "Спорт и здоровье 💪", "Книги и кофе ☕",
    "Музыка 🎵", "Жизнь прекрасна ✨", "Друзья и общение 👥",
    "Учусь новому 📚", "Мечтаю о лучшем 🌙", "Работаю над собой 🔥",
]

# Счётчик прогретых за сессию
warmup_stats = {"success": 0, "failed": 0, "results": []}

def get_country_from_phone(phone: str) -> str:
    codes = {
        "+7": "Россия/Казахстан", "+375": "Беларусь", "+380": "Украина",
        "+77": "Казахстан", "+996": "Киргизия", "+998": "Узбекистан",
        "+994": "Азербайджан", "+995": "Грузия", "+373": "Молдова",
        "+371": "Латвия", "+370": "Литва", "+372": "Эстония",
        "+48": "Польша", "+49": "Германия", "+1": "США/Канада",
        "+44": "Великобритания", "+90": "Турция", "+33": "Франция",
        "+39": "Италия", "+34": "Испания", "+31": "Нидерланды",
    }
    if not phone:
        return "Неизвестно"
    for code, country in sorted(codes.items(), key=lambda x: -len(x[0])):
        if phone.startswith(code):
            return country
    return "Неизвестно"

def generate_avatar(name: str) -> str:
    from PIL import Image, ImageDraw, ImageFont
    colors = [(255,87,87),(87,178,255),(87,255,135),(255,200,87),(200,87,255),(87,255,235),(255,135,87),(135,87,255)]
    color = random.choice(colors)
    img = Image.new('RGB', (512, 512), color)
    draw = ImageDraw.Draw(img)
    letter = name[0].upper() if name else "U"
    try:
        font = ImageFont.truetype("arial.ttf", 300)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((512-w)/2, (512-h)/2 - 30), letter, fill=(255,255,255), font=font)
    path = os.path.join(BASE_DIR, "avatars")
    os.makedirs(path, exist_ok=True)
    p = os.path.join(path, f"{name}_{random.randint(1000,9999)}.jpg")
    img.save(p)
    return p

async def setup_profile(client: TelegramClient):
    try:
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        await client(functions.account.UpdateProfileRequest(first_name=first_name, last_name=last_name))
        bio = random.choice(BIOS)
        await client(functions.account.UpdateProfileRequest(about=bio))
        try:
            avatar_path = generate_avatar(first_name)
            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(avatar_path)))
            os.remove(avatar_path)
        except:
            pass
        username = None
        for _ in range(5):
            u = f"{random.choice(USERNAME_PREFIX)}{random.randint(10000,999999)}"
            try:
                await client(functions.account.UpdateUsernameRequest(username=u))
                username = u
                break
            except:
                continue
        return first_name, last_name, username, bio
    except Exception as e:
        logging.error(f"Profile error: {e}")
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

async def warmup_account(session_name: str, msg: types.Message = None, idx: int = 0, total: int = 0):
    path = os.path.join(SESS_DIR, session_name)
    client = TelegramClient(path, API_ID, API_HASH)
    result = {"session": session_name, "success": False}
    try:
        await client.connect()
        if not await client.is_user_authorized():
            result["error"] = "NOT_AUTHORIZED"
            return result
        me = await client.get_me()
        country = get_country_from_phone(me.phone)
        fn, ln, un, bio = await setup_profile(client)
        subs = await subscribe_channels(client)
        result.update({
            "success": True, "phone": me.phone, "user_id": me.id,
            "first_name": fn or me.first_name, "last_name": ln or "",
            "username": un, "country": country, "subs": subs,
        })
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        try:
            await client.disconnect()
        except:
            pass
    return result

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
        f"⚡ Режим: параллельный\n"
        f"⏱ Примерно: {int(total * 0.7)} сек",
    )
    
    # Параллельно по 5 аккаунтов
    sem = asyncio.Semaphore(5)
    
    async def worker(session_file, i):
        async with sem:
            r = await warmup_account(session_file, status_msg, i, total)
            warmup_stats["results"].append(r)
            if r.get("success"):
                warmup_stats["success"] += 1
            else:
                warmup_stats["failed"] += 1
            try:
                await status_msg.edit_text(
                    f"🔥 <b>Прогрев {i}/{total}</b>\n\n"
                    f"{'✅' if r.get('success') else '❌'} {session_file}\n"
                    f"👤 {r.get('first_name', '—')} {r.get('last_name', '')}\n"
                    f"🌍 {r.get('country', '—')}\n"
                    f"🆔 @{r.get('username', '—')}\n\n"
                    f"✅ Успешно: {warmup_stats['success']}\n"
                    f"❌ Ошибок: {warmup_stats['failed']}"
                )
            except:
                pass
    
    await asyncio.gather(*[worker(s, i) for i, s in enumerate(sessions, 1)])
    
    # Финальный отчёт
    results = warmup_stats["results"]
    success = [r for r in results if r.get("success")]
    
    report = f"<b>✅ ПРОГРЕВ ЗАВЕРШЁН</b>\n\n"
    report += f"📊 Успешно: <b>{len(success)}</b>\n"
    report += f"❌ Ошибок: <b>{warmup_stats['failed']}</b>\n\n"
    
    if success:
        countries = {}
        for r in success:
            c = r["country"]
            countries.setdefault(c, []).append(r)
        
        report += "<b>🌍 По странам:</b>\n"
        for c, accs in sorted(countries.items(), key=lambda x: -len(x[1])):
            report += f"\n<b>{c}</b> — {len(accs)} акк.\n"
            for acc in accs:
                un = f"@{acc['username']}" if acc.get("username") else "без юза"
                report += f"  • {acc.get('first_name','')} {acc.get('last_name','')} | {un} | +{acc.get('phone','')}\n"
    
    failed = [r for r in results if not r.get("success")]
    if failed:
        report += "\n<b>❌ Ошибки:</b>\n"
        for r in failed[:10]:
            report += f"• {r['session']}: {r.get('error','?')[:80]}\n"
    
    # Разбиваем если длинно
    if len(report) > 4000:
        for i in range(0, len(report), 4000):
            await bot.send_message(chat_id, report[i:i+4000], parse_mode=ParseMode.HTML)
    else:
        await status_msg.edit_text(report)

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
        f"<b>🔥 Account Warmer</b>\n\n"
        f"📁 Сессий: <b>{count}</b>\n\n"
        f"<code>/warmup</code> — прогреть всё\n"
        f"<code>/list</code> — список\n"
        f"<code>/clear</code> — удалить сессии",
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
    await cb.message.edit_text(
        f"<b>📊 Статистика</b>\n\n"
        f"📁 Сессий: {len(sessions)}\n"
        f"🌍 Каналов: {len(CHANNELS)}\n"
        f"👤 Имён: {len(FIRST_NAMES)}\n"
        f"📝 Био: {len(BIOS)}"
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
    await bot.delete_webhook(drop_pending_updates=True)
    print("Account Warmer запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
