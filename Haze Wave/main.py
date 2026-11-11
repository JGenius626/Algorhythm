import os
import random
import subprocess
import imageio_ffmpeg

def create_radio_broadcast():
    songs = []
    jingles = []
    intro_file = None
    
    # 1. Prende le canzoni dalla cartella 'songs'
    if os.path.exists("songs") and os.path.isdir("songs"):
        songs = [os.path.join("songs", f) for f in os.listdir("songs") if f.lower().endswith(".mp3")]
        
    # 2. Prende i jingle e cerca l'intro ("welcome" o "intro" nel nome)
    search_dirs = ["jingle", "jingles", "."]
    for d in search_dirs:
        if os.path.exists(d) and os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower().endswith(".mp3"):
                    file_path = os.path.join(d, f)
                    # Se trova un file con welcome o intro, lo imposta come sigla iniziale
                    if "welcome" in f.lower() or "intro" in f.lower():
                        intro_file = file_path
                    else:
                        jingles.append(file_path)
                        
    # Rimuovi eventuali duplicati nelle liste
    songs = list(set(songs))
    jingles = list(set(jingles))

    # Fallback se non ha trovato la cartella songs
    if not songs:
        songs = [f for f in os.listdir(".") if f.lower().endswith(".mp3") and len(f) > 8]

    print(f"Trovate {len(songs)} canzoni, {len(jingles)} jingle standard" + (f" e 1 jingle di benvenuto." if intro_file else "."))

    if not songs:
        print("❌ Errore: Nessuna canzone trovata!")
        return

    # Mescoliamo le canzoni senza ripeterle
    random.shuffle(songs)

    # Costruiamo la playlist
    playlist = []
    
    # Se esiste il jingle di benvenuto, lo mettiamo per primo in assoluto!
    if intro_file:
        playlist.append(intro_file)
        print("🎙️ Sigla iniziale 'Welcome' aggiunta all'inizio del flusso.")

    # Aggiungiamo le canzoni alternate ai jingle standard
    for song in songs:
        playlist.append(song)
        if jingles:
            jingle = random.choice(jingles)
            playlist.append(jingle)

    os.makedirs("output", exist_ok=True)
    output_path = "output/neonreggaeton.mp3"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Costruiamo il comando FFmpeg con input multipli
    cmd = [ffmpeg_exe, "-y"]
    
    for track in playlist:
        cmd.extend(["-i", track])
        
    # Unisce tutti i file in sequenza normalizzando l'audio
    filter_str = ""
    for i in range(len(playlist)):
        filter_str += f"[{i}:a]"
    filter_str += f"concat=n={len(playlist)}:v=0:a=1[outa]"
    
    cmd.extend([
        "-filter_complex", filter_str, 
        "-map", "[outa]", 
        "-b:a", "192k", 
        output_path
    ])

    print("🎧 Generazione della trasmissione con sigla di apertura in corso...")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✨ Fatto! Il mix con intro di NeonReggaeton è pronto in: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Errore di FFmpeg: {e}")

if __name__ == "__main__":
    create_radio_broadcast()