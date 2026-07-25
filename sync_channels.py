import json
import requests
import os
import sys
from datetime import datetime

FIREBASE_URL = 'https://mutluapk-803a4-default-rtdb.firebaseio.com/channels.json'
ADULT_URL = 'https://yavuzok.vercel.app/xxx.json'
OUTPUT_FILE = 'src/lib/multipleChannelData.js'
WORKER_URL = 'https://gizli.mutlumedya.workers.dev'

def fetch_channels_from_firebase():
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
    try:
        response = requests.get(ADULT_URL, timeout=10)
        response.raise_for_status()
        adult_data = response.json()
        channels = adult_data.get('data', [])
        
        # 🔥 Her adult kanala benzersiz tvgId ver
        for i, channel in enumerate(channels):
            if not channel.get('tvgId') or channel.get('tvgId') == 'no_epg_xxx':
                # title'dan slug oluştur
                title_slug = channel.get('title', f'adult_{i}').lower().replace(' ', '-').replace('tv', '').strip('-')
                channel['tvgId'] = f"adult_{title_slug}"
                print(f"   🔄 Adult kanal ID: {channel['title']} → {channel['tvgId']}")
        
        print(f"✅ {len(channels)} yetişkin kanalı çekildi")
        return channels
    except Exception as e:
        print(f"❌ Adult kanalları hatası: {e}")
        return []

def generate_js_file(normal_channels, adult_channels):
    if normal_channels is None:
        print("❌ Normal kanal verisi eksik")
        return False
    
    if not adult_channels:
        print("⚠️ Adult kanal listesi boş")
    
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
        print(f"✅ Dosya oluşturuldu: {OUTPUT_FILE}")
        print(f"📊 Toplam {len(normal_channels)} normal + {len(adult_channels)} yetişkin")
        return True
    except Exception as e:
        print(f"❌ Dosya yazma hatası: {e}")
        return False

def sync_channels():
    print(f"\n🔄 Senkronizasyon başladı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    normal = fetch_channels_from_firebase()
    adult = fetch_adult_channels()
    if normal is not None:
        success = generate_js_file(normal, adult if adult else [])
        if success:
            print("✅ Senkronizasyon tamamlandı")
            return True
    print("❌ Senkronizasyon başarısız")
    return False

if __name__ == "__main__":
    try:
        success = sync_channels()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)
