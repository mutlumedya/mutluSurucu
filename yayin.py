import subprocess
import sys
import time

# ===================== CATCAST AYARLARI =====================
RTMP_URL = "rtmp://stream.livepush.io/live"
STREAM_KEY = "rtmp_2f5b9d80cdc2401ebf22745c0b901375"
rtmp_server = f"{RTMP_URL}/{STREAM_KEY}"

# ===================== YAYIN AYARLARI =====================
VIDEO_URL = "https://cdn.codenet.work/streamgo/stremgo123/4865.m3u8"
LOGO_URL = "https://raw.githubusercontent.com/mutlumedya/yayin/refs/heads/main/logo1.png"

print(f"🎬 Video Kaynağı: {VIDEO_URL}")
print(f"🎨 Logo: {LOGO_URL}")
print(f"🔑 Stream Key: {STREAM_KEY}")

# FFmpeg komutu - Logo SAĞ ÜSTTE (BÜYÜK)
command = [
    'ffmpeg',
    '-re',
    '-stream_loop', '-1',
    '-i', VIDEO_URL,
    '-i', LOGO_URL,
    '-filter_complex',
    '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[v0];'
    '[1:v]scale=230:90[logo];'
    '[v0][logo]overlay=W-w-10:3[v1];'
    '[v1]drawtext=text=t.me/digitaltivi:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=5:x=(w-text_w)/2:y=h-text_h-20[v]',
    '-map', '[v]',
    '-map', '0:a?',
    '-c:v', 'libx264',
    '-preset', 'veryfast',
    '-b:v', '4000k',
    '-c:a', 'aac',
    '-b:a', '128k',
    '-f', 'flv',
    rtmp_server
]

print("\n🎥 Catcast.tv yayını başlatılıyor...")
print("🖼️  Logo: Sağ üst (230x90 - büyük)")
print("📝 Alt yazı: t.me/digitaltivi")
print("⏸️  Durdurmak için: Ctrl + C\n")

try:
    proc = subprocess.Popen(command)
    
    # Yayını canlı tut
    while True:
        time.sleep(60)
        if proc.poll() is not None:
            print("⚠️ Yayın durdu, yeniden başlatılıyor...")
            proc = subprocess.Popen(command)
            
except KeyboardInterrupt:
    print("\n\n⛔ Yayın durduruluyor...")
    proc.terminate()
    print("✅ Yayın sonlandırıldı.")
