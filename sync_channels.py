import json
import requests
import os
import sys
import re
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
    """Adult IPTV kanallarını çek - DÜZELTİLDİ"""
    try:
        response = requests.get(ADULT_URL, timeout=10)
        response.raise_for_status()
        
        # UTF-8 olarak decode et
        content = response.text
        print(f"📄 Adult verisi uzunluğu: {len(content)} karakter")
        
        # "const ADULT_IPTV = " kısmını kaldır
        if 'const ADULT_IPTV = ' in content:
            content = content.split('const ADULT_IPTV = ', 1)[1]
        
        # Başındaki ve sonundaki boşlukları temizle
        content = content.strip()
        
        # Sonundaki noktalı virgülü kaldır
        if content.endswith(';'):
            content = content[:-1]
        
        # 🔥 JavaScript object'ini JSON'a çevir
        # 1. Tek tırnakları çift tırnak yap (kaçışlı olanları koru)
        content = re.sub(r"(?<!\\)'", '"', content)
        
        # 2. undefined → null
        content = content.replace('undefined', 'null')
        
        # 3. Son kontroller
        content = content.strip()
        
        # 4. JSON parse et
        adult_data = json.loads(content)
        
        # Sadece data array'ini al
        channels = adult_data.get('data', [])
        
        # Her kanala tvgId ekle (yoksa)
        for i, channel in enumerate(channels):
            if not channel.get('tvgId'):
                channel['tvgId'] = f"adult_{i+1}"
        
        print(f"✅ {len(channels)} yetişkin kanalı çekildi")
        return channels
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        print(f"📄 Hata alınan verinin ilk 500 karakteri:")
        print(content[:500])
        # JSON'u düzeltmeye çalış
        try:
            # Bozuk JSON'u düzeltmek için deneyelim
            fixed_content = re.sub(r'(\w+):', r'"\1":', content)
            fixed_content = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', fixed_content)
            adult_data = json.loads(fixed_content)
            channels = adult_data.get('data', [])
            for i, channel in enumerate(channels):
                if not channel.get('tvgId'):
                    channel['tvgId'] = f"adult_{i+1}"
            print(f"✅ Düzeltilmiş JSON ile {len(channels)} yetişkin kanalı çekildi")
            return channels
        except:
            return []
    except Exception as e:
        print(f"❌ Adult kanalları hatası: {e}")
        return []

def generate_js_file(normal_channels, adult_channels):
    """JavaScript dosyasını oluştur"""
    if normal_channels is None:
        print("❌ Normal kanal verisi eksik, dosya oluşturulmadı")
        return False
    
    # Adult kanalları boşsa uyarı ver ama devam et
    if not adult_channels:
        print("⚠️ Adult kanal listesi boş, sadece normal kanallar kaydedilecek")
    
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
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ Dosya güncellendi: {OUTPUT_FILE}")
        print(f"📊 Toplam {len(normal_channels)} normal + {len(adult_channels)} yetişkin = {len(normal_channels) + len(adult_channels)} kanal")
        return True
    except Exception as e:
        print(f"❌ Dosya yazma hatası: {e}")
        return False

def sync_channels():
    """Ana senkronizasyon fonksiyonu"""
    print(f"\n🔄 Senkronizasyon başladı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    normal_channels = fetch_channels_from_firebase()
    adult_channels = fetch_adult_channels()
    
    if normal_channels is not None:
        success = generate_js_file(normal_channels, adult_channels if adult_channels else [])
        if success:
            print("✅ Senkronizasyon başarıyla tamamlandı")
            return True
        else:
            print("❌ Dosya oluşturulamadı")
            return False
    else:
        print("❌ Senkronizasyon başarısız (normal kanallar alınamadı)")
        return False

# ============================================
# ÇALIŞTIRMA
# ============================================

if __name__ == "__main__":
    try:
        success = sync_channels()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        sys.exit(1)
