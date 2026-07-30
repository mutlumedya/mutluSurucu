#!/data/data/com.termux/files/usr/bin/bash

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}     Catcast.tv Yayın Kurulum Scripti${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${CYAN}   Stream Key: ${YELLOW}rtmp_2f5b9d80cdc2401ebf22745c0b901375${NC}"
echo -e "${BLUE}========================================${NC}"

# 1. Depoları güncelle
echo -e "${YELLOW}[1/6] Depolar güncelleniyor...${NC}"
pkg update -y && pkg upgrade -y

# 2. Gerekli paketleri kur
echo -e "${YELLOW}[2/6] Gerekli paketler kuruluyor...${NC}"
pkg install -y python ffmpeg

# 3. Termux storage izni
echo -e "${YELLOW}[3/6] Depolama izni isteniyor...${NC}"
termux-setup-storage

# 4. Gerekli klasörleri oluştur
echo -e "${YELLOW}[4/6] Dizinler oluşturuluyor...${NC}"
mkdir -p ~/catcast_yayin
mkdir -p ~/catcast_yayin/logs
mkdir -p ~/catcast_yayin/backup

# 5. Yayın scriptini oluştur
echo -e "${YELLOW}[5/6] Yayın scripti oluşturuluyor...${NC}"
cat > ~/catcast_yayin/catcast_go.py << 'EOF'
import subprocess
import sys
import time
import os
import signal
from datetime import datetime

# ===================== CATCAST AYARLARI =====================
RTMP_URL = "rtmp://s.catcast.tv/live"
STREAM_KEY = "rtmp_2f5b9d80cdc2401ebf22745c0b901375"
rtmp_server = f"{RTMP_URL}/{STREAM_KEY}"

# ===================== YAYIN AYARLARI =====================
# Video kaynağı (m3u8 - canlı yayın veya VOD)
VIDEO_URL = "https://cdn.codenet.work/streamgo/stremgo123/4865.m3u8"

# Logo (PNG formatında - transparan arkaplanlı önerilir)
LOGO_URL = "https://raw.githubusercontent.com/mutlumedya/yayin/refs/heads/main/logo1.png"

# ===================== KESME VE EKLEME =====================
# Yayına kesme ekleme (isteğe bağlı)
CUT_TIME_START = None  # "00:00:00" veya None
CUT_TIME_END = None    # "00:05:00" veya None

# Video filtresi
def get_filter_complex():
    filter_parts = []
    
    # 1. Video boyutlandırma (1280x720)
    filter_parts.append('[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[v0]')
    
    # 2. Logo ekleme (SAĞ ÜST - 200x90)
    filter_parts.append('[1:v]scale=200:90[logo]')
    filter_parts.append('[v0][logo]overlay=W-w-10:3[v1]')
    
    # 3. Alt yazı ekleme (t.me/digitaltivi - ortada alt)
    filter_parts.append('[v1]drawtext=text=t.me/digitaltivi:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=5:x=(w-text_w)/2:y=h-text_h-20[v]')
    
    # 4. Kesme efekti (isteğe bağlı)
    if CUT_TIME_START and CUT_TIME_END:
        filter_parts.append(f'[v]trim=start={CUT_TIME_START}:end={CUT_TIME_END},setpts=PTS-STARTPTS[v_final]')
    else:
        filter_parts.append('[v]null[v_final]')
    
    return ';'.join(filter_parts)

def get_ffmpeg_command():
    base_cmd = [
        'ffmpeg',
        '-re',
        '-stream_loop', '-1',
        '-i', VIDEO_URL,
        '-i', LOGO_URL,
        '-filter_complex', get_filter_complex(),
        '-map', '[v_final]',
        '-map', '0:a?',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-b:v', '4000k',
        '-maxrate', '4500k',
        '-bufsize', '8000k',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-ar', '44100',
        '-f', 'flv',
        '-flvflags', 'no_duration_filesize',
        rtmp_server
    ]
    return base_cmd

def log_message(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")
    with open('~/catcast_yayin/logs/yayin.log', 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

def signal_handler(sig, frame):
    log_message("⛔ Yayın durduruluyor...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Ana program
def main():
    log_message("🎬 Catcast.tv yayın başlatılıyor...")
    log_message(f"📺 Video Kaynağı: {VIDEO_URL}")
    log_message(f"🎨 Logo: {LOGO_URL}")
    log_message(f"🔑 Stream Key: {STREAM_KEY}")
    log_message(f"🖼️  Logo konumu: Sağ üst (200x90)")
    log_message(f"📝 Alt yazı: t.me/digitaltivi")
    log_message("⏸️  Durdurmak için: Ctrl + C")
    log_message("=" * 50)
    
    command = get_ffmpeg_command()
    
    # FFmpeg'i başlat
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log_message("✅ Yayın başarıyla başladı!")
        
        # Yayını canlı tut
        while True:
            time.sleep(60)
            if proc.poll() is not None:
                log_message("⚠️ Yayın durdu, yeniden başlatılıyor...")
                proc = subprocess.Popen(command)
                
    except KeyboardInterrupt:
        log_message("⛔ Yayın durduruluyor...")
        proc.terminate()
        log_message("✅ Yayın sonlandırıldı.")
    except Exception as e:
        log_message(f"❌ HATA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# 6. Yedek script oluştur (otomatik yeniden başlatma için)
echo -e "${YELLOW}[6/6] Otomatik yeniden başlatma scripti oluşturuluyor...${NC}"
cat > ~/catcast_yayin/start_yayin.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
while true; do
    echo "$(date): Yayın başlatılıyor..."
    python ~/catcast_yayin/catcast_go.py
    echo "$(date): Yayın durdu, 5 saniye sonra yeniden başlatılacak..."
    sleep 5
done
EOF
chmod +x ~/catcast_yayin/start_yayin.sh

# 7. Run script
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✨ Kurulum tamamlandı!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Başlatmak için:${NC}"
echo -e "  ${CYAN}python ~/catcast_yayin/catcast_go.py${NC}"
echo -e "${YELLOW}Otomatik yeniden başlatma için:${NC}"
echo -e "  ${CYAN}bash ~/catcast_yayin/start_yayin.sh${NC}"
echo -e "${YELLOW}Yayın bilgileri:${NC}"
echo -e "  ${CYAN}Stream Key: rtmp_2f5b9d80cdc2401ebf22745c0b901375${NC}"
echo -e "  ${CYAN}RTMP URL: rtmp://s.catcast.tv/live/${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎥 Yayın başlatılıyor...${NC}\n"

# Başlat
python ~/catcast_yayin/catcast_go.py
