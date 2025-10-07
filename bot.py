import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError

# ---------- ENVIRONMENT ----------
API_ID   = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE    = os.getenv('PHONE')
client = TelegramClient('session', API_ID, API_HASH)
TARGETS  = [int(x) for x in os.getenv('TARGETS', '').split(',') if x]  # çoklu grup

# ---------- RESİMLER (repo kökünde) ----------
IMG1 = "Rek1.jpg"
IMG2 = "Rek.jpg"

# ---------- GÖNDERİM SAATLERİ ----------
SEND_TIMES = [(8, 15), (15, 15), (23, 15)]

# ---------- SON MESAJ ID SAKLAMA ----------
last_msg_ids = []


async def main():
    print("🤖 Telegram 7/24 Çoklu-Grup Resim Botu")
    print("=" * 50)
    print(f"📁 Resim 1: {IMG1}")
    print(f"📁 Resim 2: {IMG2}")
    print(f"🎯 Hedef gruplar: {len(TARGETS)} adet")
    print(f"⏰ Saatler: {', '.join(f'{h:02d}:{m:02d}' for h, m in SEND_TIMES)}")
    print("=" * 50)

    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(phone=PHONE)
    print("✓ Telegram’a giriş yapıldı")

    # Resim var mı?
    for p in (IMG1, IMG2):
        if not os.path.exists(p):
            print(f"❌ Resim bulunamadı: {p}")
            return
        print(f"✓ {p} bulundu – boyut: {os.path.getsize(p) / 1024:.1f} KB")

    last_sent_time = None
    while True:
        now = datetime.now()
        if now.second == 0:
            print(f"🕒 {now.strftime('%H:%M:%S')}  "
                  f"Son gönderim: {last_sent_time or 'Yok'}")

        for hh, mm in SEND_TIMES:
            if (now.hour, now.minute) == (hh, mm) and last_sent_time != f"{hh:02d}:{mm:02d}":
                print(f"\n🎯 {hh:02d}:{mm:02d}!  "
                      f"{len(TARGETS)} gruba 2’şer resim gönderiliyor...")

                # Önceki mesajları sil (her grup için)
                if last_msg_ids:
                    for gid in TARGETS:
                        try:
                            await client.delete_messages(gid, last_msg_ids)
                        except Exception as e:
                            print("⚠️  Silme hatası:", e)
                    last_msg_ids.clear()

                # Her gruba yeni resimleri gönder
                success = 0
                for gid in TARGETS:
                    try:
                        msg1 = await client.send_file(gid, IMG1)
                        msg2 = await client.send_file(gid, IMG2)
                        last_msg_ids.extend([msg1.id, msg2.id])
                        print(f"✓ {gid} grubuna gönderildi")
                        await asyncio.sleep(3)      # flood koruması
                        success += 1
                    except FloodWaitError as f:
                        print(f"⏳ Flood wait {f.seconds} sn")
                        await asyncio.sleep(f.seconds)
                    except Exception as e:
                        print(f"❌ {gid} hatası:", e)

                last_sent_time = f"{hh:02d}:{mm:02d}"
                print(f"✓ Gönderim tamamlandı – Başarılı: {success}/{len(TARGETS)}")
                break

        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Durduruldu")
        
