import asyncio, os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# ENVIRONMENT değişkenleri
api_id   = int(os.getenv('API_ID', 29907288))
api_hash = os.getenv('API_HASH', '9357df73238efe8d42aeefc9547cb699')
phone    = os.getenv('PHONE', '+375259075099')

image_path1 = "/storage/emulated/0/Pictures/Rek1.jpg"
image_path2 = "/storage/emulated/0/Pictures/Rek.jpg"

SEND_TIMES = [(8, 15), (15, 15), (23, 15)]
last_message_ids = {}

# ----- Aşağısı senin kodunla aynı ----- #
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
    
    # Kullanıcıdan grup seçimi
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
            
            # Silinen mesaj ID'lerini temizle (artık bir sonraki silme için)
            last_message_ids[group_id] = []
            return True
    except Exception as e:
        print(f"❌ Silme hatası ({group['name']}): {e}")
    return False

async def send_telegram_message():
    client = TelegramClient(f'session_{phone}', api_id, api_hash, timeout=60, connection_retries=5)
    
    try:
        await client.start()
        print("✓ Telegram client başlatıldı")
        
        if not await client.is_user_authorized():
            print("⚠️ Oturum açılmamış. Doğrulama yapılacak...")
            await client.send_code_request(phone)
            print("📱 Telefonunuza kod gönderildi...")
            
            code = input('✅ Lütfen telefonunuza gelen kodu girin: ')
            
            try:
                await client.sign_in(phone, code)
                print("✓ Kod doğrulandı")
            except SessionPasswordNeededError:
                print("🔐 İki faktörlü doğrulama gerekli")
                password = input('✅ Lütfen iki faktörlü doğrulama şifrenizi girin: ')
                await client.sign_in(password=password)
                print("✓ İki faktörlü doğrulama başarılı")
        else:
            print("✓ Zaten oturum açılmış")
        
        print("✓ Giriş başarılı")
        
        # Grupları interaktif seç
        selected_groups = await choose_groups_interactively(client)
        
        if not selected_groups:
            print("❌ Hiç grup seçilmedi!")
            return
        
        print(f"✓ {len(selected_groups)} grup seçildi")
        
        # İki resmi de kontrol et
        print("📸 Resimler kontrol ediliyor...")
        
        # 1. Resmi kontrol et
        print(f"🔍 1. Resim: {image_path1}")
        if not os.path.exists(image_path1):
            print(f"❌ 1. Resim dosyası bulunamadı: {image_path1}")
            return
        size1 = os.path.getsize(image_path1) / 1024
        print(f"✓ 1. Resim bulundu - Boyut: {size1:.1f} KB")
        
        # 2. Resmi kontrol et
        print(f"🔍 2. Resim: {image_path2}")
        if not os.path.exists(image_path2):
            print(f"❌ 2. Resim dosyası bulunamadı: {image_path2}")
            return
        size2 = os.path.getsize(image_path2) / 1024
        print(f"✓ 2. Resim bulundu - Boyut: {size2:.1f} KB")
        
        print("✓ İki farklı resim gönderilecek")
        print("🗑️  HER GÖNDERİMDEN ÖNCE BİR ÖNCEKİ MESAJ SİLİNECEK")
        print(f"⏰ Belirlenen saatlerde {len(selected_groups)} gruba gönderme başlatılıyor...")
        print("⏎ Çıkmak için Pydroid'de 'Stop' butonuna basın\n")
        
        last_sent_time = None
        
        while True:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            current_second = now.second
            
            # Her dakika bilgisini göster
            if current_second == 0:
                print(f"🕒 Şu anki zaman: {now.strftime('%H:%M:%S')} - Son gönderim: {last_sent_time if last_sent_time else 'Henüz yok'}")
            
            # Belirlenen saatlerde kontrol et
            for send_hour, send_minute in SEND_TIMES:
                if (current_hour == send_hour and current_minute == send_minute and 
                    current_second < 10 and last_sent_time != f"{send_hour:02d}:{send_minute:02d}"):
                    
                    print(f"\n🎯 Saat {send_hour:02d}:{send_minute:02d}! - {len(selected_groups)} gruba 2'şer resim gönderiliyor...")
                    
                    try:
                        # Her grup için ayrı ayrı gönder
                        success_count = 0
                        for i, group in enumerate(selected_groups, 1):
                            print(f"📤 {i}. gruba gönderiliyor: {group['name']}")
                            
                            try:
                                # ÖNCE BİR ÖNCEKİ MESAJLARI SİL (eğer varsa)
                                if last_sent_time:  # İlk gönderimde silme yapma
                                    await delete_previous_messages(client, group)
                                
                                # İki FARKLI resmi gönder ve ID'lerini kaydet
                                message1 = await client.send_file(group['entity'], image_path1)
                                print(f"   ✅ 1. Resim gönderildi (ID: {message1.id})")
                                
                                message2 = await client.send_file(group['entity'], image_path2)
                                print(f"   ✅ 2. Resim gönderildi (ID: {message2.id})")
                                
                                # Yeni mesaj ID'lerini kaydet (bir sonraki silme için)
                                last_message_ids[group['id']] = [message1.id, message2.id]
                                print(f"   💾 Mesaj ID'leri kaydedildi (sonra silinecek)")
                                
                                success_count += 1
                                
                            except Exception as e:
                                print(f"   ❌ {group['name']} grubuna gönderim hatası: {e}")
                            
                            # Gruplar arasında 3 saniye bekle (Flood koruması için)
                            if i < len(selected_groups):
                                await asyncio.sleep(3)
                        
                        last_sent_time = f"{send_hour:02d}:{send_minute:02d}"
                        print(f"✓ Gönderim tamamlandı - Başarılı: {success_count}/{len(selected_groups)} grup")
                        print(f"💾 Mesajlar kaydedildi, bir sonraki gönderimde silinecek")
                        
                    except FloodWaitError as e:
                        print(f"⏳ Flood wait hatası: {e.seconds} saniye beklemem gerekiyor")
                        await asyncio.sleep(e.seconds)
                        
                    except Exception as e:
                        print(f"❌ Genel gönderme hatası: {e}")
                        await asyncio.sleep(30)
            
            await asyncio.sleep(1)
                
    except Exception as e:
        print(f"❌ Program hatası: {e}")
    finally:
        try:
            await client.disconnect()
            print("🔌 Bağlantı kesildi")
        except:
            pass

if __name__ == "__main__":
    print("🤖 Telegram Otomatik Reklam Gönderici (ZİNCİR SİLMELİ)")
    print("=====================================")
    print(f"📁 1. Resim: {image_path1}")
    print(f"📁 2. Resim: {image_path2}")
    print("👥 Hedef gruplar: INTERAKTİF SEÇİM")
    print("🗑️  SİLME MANTIĞI:")
    print("   08:15 → Mesaj gönder (ilk gönderim, silme yok)")
    print("   15:15 → 08:15 mesajını sil → Yeni mesaj gönder")
    print("   23:15 → 15:15 mesajını sil → Yeni mesaj gönder")
    print("   08:15 → 23:15 mesajını sil → Yeni mesaj gönder")
    print("⏰ Gönderim saatleri: 08:15, 15:15, 23:15")
    print("=====================================")
    
    try:
        asyncio.run(send_telegram_message())
    except asyncio.CancelledError:
        print("\n⏹️  Program durduruldu")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
