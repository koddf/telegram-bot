import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# ---------- ENVIRONMENT ----------
api_id   = int(os.getenv('API_ID', 29907288))
api_hash = os.getenv('API_HASH', '9357df73238efe8d42aeefc9547cb699')
phone    = os.getenv('PHONE', '+375259075099')

# ---------- RESİMLER ----------
image_path1 = "Rek1.jpg"   # repo kökünde olmalı
image_path2 = "Rek.jpg"    # repo kökünde olmalı

# ---------- GÖNDERİM SAATLERİ ----------
SEND_TIMES = [(8, 15), (15, 15), (23, 15)]

# ---------- SON MESAJ ID SAKLAMA ----------
last_message_ids = {}


async def choose_groups_interactively(client):
    """Kullanıcıya grupları listeler ve seçim yaptırır"""
    print("🔍 Tüm gruplar listeleniyor...")
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            groups.append(dialog)
            print(f"{len(groups)}. {dialog.name}")

    print(f"\n📋 Toplam {len(groups)} grup bulundu")
    if not groups:
        print("❌ Hiç grup bulunamadı!")
        return []

    choices = input("✅ Gönderim yapılacak grup numaralarını girin (örn: 1,3,5): ")
    selected = []
    for choice in choices.split(','):
        try:
            index = int(choice.strip()) - 1
            if 0 <= index < len(groups):
                selected.append({
                    'entity': groups[index].entity,
                    'name': groups[index].name,
                    'id': groups[index].id
                })
                print(f"✓ Seçildi: {groups[index].name}")
            else:
                print(f"❌ Geçersiz numara: {choice}")
        except ValueError:
            print(f"❌ Geçersiz giriş: {choice}")
    return selected


async def delete_previous_messages(client, group):
    """Sadece bir önceki gönderilen mesajları siler"""
    try:
        group_id = group['id']
        if group_id in last_message_ids and last_message_ids[group_id]:
            print(f"🗑️  {group['name']} grubundaki önceki mesajlar siliniyor...")
            for msg_id in last_message_ids[group_id]:
                try:
                    await client.delete_messages(group['entity'], msg_id)
                    print(f"   ✅ Mesaj silindi: {msg_id}")
                except Exception as e:
                    print(f"   ❌ Mesaj silinemedi {msg_id}: {e}")
            last_message_ids[group_id] = []
            return True
    except Exception as e:
        print(f"❌ Silme hatası ({group['name']}): {e}")
    return False


async def send_telegram_message():
    client = TelegramClient(f'session_{phone}', api_id, api_hash,
                          timeout=60, connection_retries=5)
    try:
        await client.start()
        print("✓ Telegram client başlatıldı")

        if not await client.is_user_authorized():
            print("⚠️ Oturum açılmamış. Doğrulama yapılacak...")
            await client.send_code_request(phone)
            code = input('✅ Telefonunuza gelen kodu girin: ')
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                password = input('🔐 İki faktörlü şifrenizi girin: ')
                await client.sign_in(password=password)

        print("✓ Giriş başarılı")
        selected_groups = await choose_groups_interactively(client)
        if not selected_groups:
            print("❌ Hiç grup seçilmedi!")
            return

        print("📸 Resimler kontrol ediliyor...")
        for p in (image_path1, image_path2):
            if not os.path.exists(p):
                print(f"❌ Resim bulunamadı: {p}")
                return
            print(f"✓ {p} bulundu - Boyut: {os.path.getsize(p)/1024:.1f} KB")

        print("🗑️  HER GÖNDERİMDEN ÖNCE BİR ÖNCEKİ MESAJ SİLİNECEK")
        last_sent_time = None

        while True:
            now = datetime.now()
            if now.second == 0:
                print(f"🕒 {now.strftime('%H:%M:%S')}  "
                      f"Son gönderim: {last_sent_time or 'Henüz yok'}")

            for send_hour, send_minute in SEND_TIMES:
                if (now.hour == send_hour and now.minute == send_minute and
                    now.second < 10 and last_sent_time != f"{send_hour:02d}:{send_minute:02d}"):

                    print(f"\n🎯 {send_hour:02d}:{send_minute:02d}!  "
                          f"{len(selected_groups)} gruba 2'şer resim gönderiliyor...")
                    success = 0
                    for i, g in enumerate(selected_groups, 1):
                        print(f"📤 {i}. gruba: {g['name']}")
                        try:
                            if last_sent_time:
                                await delete_previous_messages(client, g)
                            msg1 = await client.send_file(g['entity'], image_path1)
                            msg2 = await client.send_file(g['entity'], image_path2)
                            last_message_ids[g['id']] = [msg1.id, msg2.id]
                            success += 1
                            if i < len(selected_groups):
                                await asyncio.sleep(3)   # flood koruması
                        except FloodWaitError as e:
                            print(f"⏳ Flood wait: {e.seconds} sn")
                            await asyncio.sleep(e.seconds)
                        except Exception as e:
                            print(f"❌ Gönderim hatası: {e}")
                    last_sent_time = f"{send_hour:02d}:{send_minute:02d}"
                    print(f"✓ Gönderim tamamlandı - Başarılı: {success}/{len(selected_groups)}")
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Program hatası: {e}")
    finally:
        await client.disconnect()
        print("🔌 Bağlantı kesildi")


if __name__ == "__main__":
    print("🤖 Telegram Otomatik Reklam Gönderici (ZİNCİR SİLMELİ)")
    print("=====================================")
    print(f"📁 1. Resim: {image_path1}")
    print(f"📁 2. Resim: {image_path2}")
    print("👥 Hedef gruplar: INTERAKTİF SEÇİM")
    print("⏰ Gönderim saatleri: 08:15, 15:15, 23:15")
    print("=====================================")
    try:
        asyncio.run(send_telegram_message())
    except KeyboardInterrupt:
        print("\n⏹️  Program durduruldu")
             
