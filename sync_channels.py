import json
import requests
import os
import sys
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
    """Adult IPTV kanallarını çek - ID'leri adult- prefix ile düzenle"""
    try:
        response = requests.get(ADULT_URL, timeout=10)
        response.raise_for_status()
        adult_data = response.json()
        channels = adult_data.get('data', [])
        
        # 🔥 Adult kanallarını düzenle
        for channel in channels:
            old_tvg_id = channel.get('tvgId', '')
            
            # Eğer ID boş veya no_epg_xxx ise title'dan oluştur
            if not old_tvg_id or old_tvg_id == 'no_epg_xxx':
                base_id = channel.get('title', 'unknown')
                base_id = base_id.lower().replace(' ', '-').replace('tv', '').strip('-')
                base_id = ''.join(c for c in base_id if c.isalnum() or c == '-')
                new_tvg_id = f"adult-{base_id}"
            else:
                # Mevcut ID'yi kullan ama başına adult- ekle (zaten yoksa)
                if old_tvg_id.startswith('kanal_'):
                    # kanal_ prefix'ini kaldır ve adult- ekle
                    clean_id = old_tvg_id.replace('kanal_', '')
                    new_tvg_id = f"adult-{clean_id}"
                elif not old_tvg_id.startswith('adult-'):
                    new_tvg_id = f"adult-{old_tvg_id}"
                else:
                    new_tvg_id = old_tvg_id
            
            # 🔥 URL'yi Worker'a yönlendir
            channel['url'] = f"{WORKER_URL}/{new_tvg_id}.m3u8"
            channel['tvgId'] = new_tvg_id
            
            print(f"   🔄 Adult: {channel['title']} → {new_tvg_id}")
        
        print(f"✅ {len(channels)} yetişkin kanalı çekildi ve düzenlendi")
        return channels
    except Exception as e:
        print(f"❌ Adult kanalları hatası: {e}")
        return []

def generate_js_file(normal_channels, adult_channels):
    """JavaScript dosyasını oluştur"""
    if normal_channels is None:
        print("❌ Normal kanal verisi eksik, dosya oluşturulmadı")
        return False
    
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
        
        print(f"✅ Dosya oluşturuldu/güncellendi: {OUTPUT_FILE}")
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
