# ============================================
# sync_channels.py - GITHUB API İLE GÖNDER
# ============================================

import json
import os
import requests
import sys
import base64
from datetime import datetime

# ============================================
# YAPILANDIRMA - .env.local'dan Oku
# ============================================

def load_env_local():
    """.env.local dosyasını oku"""
    try:
        env_file = '.env.local'
        if not os.path.exists(env_file):
            env_file = '.env'
            if not os.path.exists(env_file):
                return {}
        
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        return True
    except Exception as e:
        print(f"⚠️ .env.local okuma hatası: {e}")
        return False

load_env_local()

# Değişkenleri al
FIREBASE_URL = os.getenv('FIREBASE_URL')
ADULT_URL = os.getenv('ADULT_URL')
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'src/lib/multipleChannelData.js')
WORKER_URL = os.getenv('WORKER_URL')

# GitHub bilgileri
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER')
REPO_NAME = os.getenv('REPO_NAME')
FILE_PATH_IN_REPO = os.getenv('FILE_PATH_IN_REPO', 'src/lib/multipleChannelData.js')
BRANCH = os.getenv('BRANCH', 'main')

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
        
        print(f"✅ {len(channels)} normal kanal çekildi")
        return channels
    except Exception as e:
        print(f"❌ Firebase hatası: {e}")
        return None

def fetch_adult_channels():
    """Adult IPTV kanallarını çek"""
    try:
        response = requests.get(ADULT_URL, timeout=10)
        response.raise_for_status()
        adult_data = response.json()
        channels = adult_data.get('data', [])
        
        for channel in channels:
            channel_id = channel.get('tvgId', '')
            
            if not channel_id or channel_id == 'no_epg_xxx':
                base_id = channel.get('title', 'unknown')
                base_id = base_id.lower().replace(' ', '-').replace('tv', '').strip('-')
                base_id = ''.join(c for c in base_id if c.isalnum() or c == '-')
                channel_id = f"kanal_{abs(hash(base_id)) % 10000000000:010d}"
                channel['tvgId'] = channel_id
            
            channel['url'] = f"{WORKER_URL}/{channel_id}.m3u8"
        
        print(f"✅ {len(channels)} yetişkin kanalı çekildi")
        return channels
    except Exception as e:
        print(f"❌ Adult kanalları hatası: {e}")
        return []

def generate_js_file(normal_channels, adult_channels):
    """JavaScript dosyasını oluştur"""
    if normal_channels is None:
        print("❌ Normal kanal verisi eksik")
        return False
    
    js_content = f"""const CODE_CLOUD_BD = {{
    name: "CodeCloudBD",
    slug: "codecloudbd",
    source: "https://stream.codecloud.bd/",
    active: true,
    isAdult: false,
    copyright: "We do not host or stream any content. All streams are publicly available.",
    data: {json.dumps(normal_channels, indent=4, ensure_ascii=False)}
}};

const ADULT_IPTV = {{
    name: "Adult IPTV",
    slug: "adult-ip-tv",
    source: "https://adultiptv.net/",
    active: true,
    isAdult: true,
    copyright: "We do not host or stream any content. All streams are publicly available.",
    data: {json.dumps(adult_channels, indent=4, ensure_ascii=False)}
}};

export {{ CODE_CLOUD_BD, ADULT_IPTV }};"""
    
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ Dosya oluşturuldu: {OUTPUT_FILE}")
        print(f"📊 Toplam {len(normal_channels)} normal + {len(adult_channels)} yetişkin = {len(normal_channels) + len(adult_channels)} kanal")
        return True
    except Exception as e:
        print(f"❌ Dosya yazma hatası: {e}")
        return False

def push_to_github_api(file_path, token, owner, repo, file_path_in_repo, branch='main'):
    """
    GitHub API kullanarak dosyayı repoya gönder
    """
    try:
        # 1. Dosyayı oku
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. Base64 encode
        content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # 3. API URL
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path_in_repo}"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 4. Önce dosya var mı kontrol et (SHA gerekli)
        print(f"🔍 Kontrol: {owner}/{repo}/{file_path_in_repo}")
        response = requests.get(api_url, headers=headers)
        
        sha = None
        if response.status_code == 200:
            sha = response.json().get('sha')
            print(f"📁 Dosya mevcut, güncellenecek (SHA: {sha[:8]}...)")
        elif response.status_code == 404:
            print(f"📄 Dosya yok, yeni oluşturulacak")
        else:
            print(f"⚠️ Beklenmeyen durum: {response.status_code}")
        
        # 5. Commit mesajı
        commit_message = f"🔄 Kanal listesi güncellendi: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 6. Data
        data = {
            'message': commit_message,
            'content': content_base64,
            'branch': branch
        }
        
        if sha:
            data['sha'] = sha
        
        # 7. API'ye gönder (PUT ile güncelle/oluştur)
        print(f"📤 GitHub'a gönderiliyor...")
        response = requests.put(api_url, headers=headers, json=data)
        
        # 8. Sonuç kontrol
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Dosya başarıyla gönderildi!")
            print(f"🔗 Link: {result.get('content', {}).get('html_url', '')}")
            return True
        else:
            print(f"❌ GitHub API hatası: {response.status_code}")
            print(f"📝 Hata mesajı: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub push hatası: {e}")
        return False

def sync_channels():
    """Ana senkronizasyon fonksiyonu"""
    print(f"\n{'='*50}")
    print(f"🔄 SENKRONİZASYON BAŞLADI: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # 1. Kanalları çek
    normal_channels = fetch_channels_from_firebase()
    adult_channels = fetch_adult_channels()
    
    if normal_channels is None:
        print("❌ Senkronizasyon başarısız (normal kanallar alınamadı)")
        return False
    
    # 2. Dosyayı oluştur
    success = generate_js_file(normal_channels, adult_channels if adult_channels else [])
    
    if not success:
        print("❌ Dosya oluşturulamadı")
        return False
    
    # 3. GitHub'a gönder
    print(f"\n📤 GitHub'a gönderiliyor...")
    
    # GitHub bilgilerini kontrol et
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN tanımlı değil! .env.local'a ekleyin")
        return False
    
    if not REPO_OWNER or not REPO_NAME:
        print("❌ REPO_OWNER veya REPO_NAME tanımlı değil!")
        return False
    
    # GitHub'a gönder
    push_success = push_to_github_api(
        OUTPUT_FILE,
        GITHUB_TOKEN,
        REPO_OWNER,
        REPO_NAME,
        FILE_PATH_IN_REPO,
        BRANCH
    )
    
    if push_success:
        print(f"\n✅ TÜM İŞLEMLER BAŞARILI! 🎉")
        return True
    else:
        print(f"\n❌ GitHub gönderimi başarısız!")
        return False

# ============================================
# ÇALIŞTIRMA
# ============================================

if __name__ == "__main__":
    try:
        success = sync_channels()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        sys.exit(1)
