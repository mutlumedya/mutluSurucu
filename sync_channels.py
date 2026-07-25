import json
import requests
import os
import time
import schedule
from datetime import datetime

# ============================================
# YAPILANDIRMA
# ============================================
FIREBASE_URL = 'https://mutluapk-803a4-default-rtdb.firebaseio.com/channels.json'
ADULT_URL = 'https://yavuzok.vercel.app/xxx.json'
OUTPUT_FILE = 'src/lib/multipleChannelData.js'
WORKER_URL = 'https://gizli.mutlumedya.workers.dev'

# ============================================
# FONKSİYONLAR
# ============================================

def fetch_channels_from_firebase():
    """Firebase'den normal kanalları çek"""
    try:
        response = requests.get(FIREBASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        channels = []
        for key, channel in data.items():
            channel_id = channel.get('channelId', key)
            channels.append({
                "duration": -1,
                "title": channel.get('isim', 'Bilinmeyen Kanal'),
                "tvgId": channel_id,
                "tvgName": channel.get('isim', 'Bilinmeyen Kanal'),
                "tvgLogo": channel.get('logo', ''),
                "groupTitle": channel.get('kategori', 'Genel'),
                "url": f"{WORKER_URL}/{channel_id}.m3u8"
            })
        
        print(f"✅ {len(channels)} normal kanal Firebase'den çekildi")
        return channels
    except Exception as e:
        print(f"❌ Firebase hatası: {e}")
        return None

def fetch_adult_channels():
    """Adult IPTV kanallarını çek"""
    try:
        response = requests.get(ADULT_URL, timeout=10)
        response.raise_for_status()
        
        # JSON içeriğini parse et (JavaScript object'ten JSON'a çevir)
        content = response.text
        # "const ADULT_IPTV = " kısmını kaldır
        if content.startswith('const ADULT_IPTV = '):
            content = content.replace('const ADULT_IPTV = ', '')
        # Sonundaki noktalı virgülü kaldır
        if content.endswith(';'):
            content = content[:-1]
        
        adult_data = json.loads(content)
        
        # Sadece data array'ini al
        channels = adult_data.get('data', [])
        
        # Her kanala tvgId ekle (yoksa)
        for i, channel in enumerate(channels):
            if not channel.get('tvgId'):
                channel['tvgId'] = f"adult_{i+1}"
        
        print(f"✅ {len(channels)} yetişkin kanalı çekildi")
        return channels
    except Exception as e:
        print(f"❌ Adult kanalları hatası: {e}")
        return None

def generate_js_file(normal_channels, adult_channels):
    """JavaScript dosyasını oluştur"""
    if normal_channels is None or adult_channels is None:
        print("❌ Kanal verisi eksik, dosya oluşturulmadı")
        return False
    
    # Normal kanalları kontrol et
    if not normal_channels:
        print("⚠️ Normal kanal listesi boş!")
    
    # Adult kanalları kontrol et
    if not adult_channels:
        print("⚠️ Adult kanal listesi boş!")
    
    js_content = f"""const CODE_CLOUD_BD = {{
    name: "CodeCloudBD",
    slug: "codecloudbd",
    source: "https://stream.codecloud.bd/",
    active: true,
    isAdult: false,
    copyright: "We do not host or stream any content. All streams are publicly available. This service is provided free of charge for entertainment purposes only. By using this service, you agree to release us from all liability.",
    data: {json.dumps(normal_channels, indent=4, ensure_ascii=False)}
}};

const ADULT_IPTV = {{
    name: "Adult IPTV",
    slug: "adult-ip-tv",
    source: "https://adultiptv.net/",
    active: true,
    isAdult: true,
    copyright: "We do not host or stream any content. All streams are publicly available. This service is provided free of charge for entertainment purposes only. By using this service, you agree to release us from all liability.",
    data: {json.dumps(adult_channels, indent=4, ensure_ascii=False)}
}};

export {{ CODE_CLOUD_BD, ADULT_IPTV }};"""
    
    try:
        # Klasörü kontrol et
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Dosyaya yaz
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ Dosya güncellendi: {OUTPUT_FILE}")
        print(f"📊 Toplam {len(normal_channels)} normal + {len(adult_channels)} yetişkin = {len(normal_channels) + len(adult_channels)} kanal kaydedildi")
        return True
    except Exception as e:
        print(f"❌ Dosya yazma hatası: {e}")
        return False

def sync_channels():
    """Ana senkronizasyon fonksiyonu"""
    print(f"\n🔄 Senkronizasyon başladı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Her iki kaynaktan da çek
    normal_channels = fetch_channels_from_firebase()
    adult_channels = fetch_adult_channels()
    
    if normal_channels is not None and adult_channels is not None:
        generate_js_file(normal_channels, adult_channels)
    else:
        print("❌ Senkronizasyon başarısız")
    
    print("✅ Senkronizasyon tamamlandı")

def run_scheduler():
    """Zamanlayıcıyı başlat"""
    print("🚀 Bot başlatıldı - Her 1 saatte bir senkronizasyon yapılacak")
    print(f"📁 Çıktı dosyası: {OUTPUT_FILE}")
    print(f"🔥 Firebase URL: {FIREBASE_URL}")
    print(f"🔞 Adult URL: {ADULT_URL}")
    
    # İlk çalıştırma
    sync_channels()
    
    # Her 1 saatte bir çalıştır
    schedule.every(1).hours.do(sync_channels)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ============================================
# ÇALIŞTIRMA
# ============================================

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu")
