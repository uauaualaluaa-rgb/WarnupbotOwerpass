import asyncio
import os
from telethon import TelegramClient

API_ID = 8694433490
API_HASH = "e8fb7f7163498eb28231e45071fe92c0"

async def main():
    # Абсолютный путь к папке сессий
    BASE = os.path.dirname(os.path.abspath(__file__))
    SESS = os.path.join(BASE, "sessions")
    print(f"Папка сессий: {SESS}")
    print(f"Файлы: {os.listdir(SESS)}")
    print()
    
    for f in os.listdir(SESS):
        if not f.endswith(".session"):
            continue
        
        name = f.replace(".session", "")
        path = os.path.join(SESS, name)
        
        client = TelegramClient(path, API_ID, API_HASH)
        try:
            await client.connect()
            auth = await client.is_user_authorized()
            
            if auth:
                me = await client.get_me()
                print(f"✅ {name}: {me.phone} | {me.first_name} | id={me.id}")
            else:
                print(f"❌ {name}: НЕ АВТОРИЗОВАН")
        except Exception as e:
            print(f"⚠️ {name}: {type(e).__name__}: {e}")
        finally:
            await client.disconnect()

asyncio.run(main())
