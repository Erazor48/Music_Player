import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import random
import pygame

# Initialisation de pygame et du mixer
pygame.init()
pygame.mixer.init()

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lecteur Audio amélioré")
        # Variables de gestion
        self.music_directory = ""
        self.music_list = []             # Liste complète des chemins des fichiers MP3
        self.current_song_path = None    # Chemin de la musique actuellement chargée
        self.is_paused = False           # Etat de pause

        self.build_gui()
        # Vérification périodique pour l'auto-changement à la fin de la musique
        self.check_playback()

    def build_gui(self):
        # Bouton pour charger un dossier de musiques
        btn_load_dir = tk.Button(self.root, text="Charger dossier musique", command=self.load_directory)
        btn_load_dir.pack(pady=5)

        # Combobox pour afficher la liste des musiques
        self.song_var = tk.StringVar()
        self.song_combo = ttk.Combobox(self.root, textvariable=self.song_var, state="readonly", width=50)
        self.song_combo.pack(pady=5)
        self.song_combo.bind("<<ComboboxSelected>>", self.song_selected)

        # Bouton pour lancer la lecture de la musique sélectionnée
        btn_play_selected = tk.Button(self.root, text="Lecture (chanson sélectionnée)", command=self.play_selected)
        btn_play_selected.pack(pady=5)

        # Bouton Pause/Reprendre
        btn_pause_resume = tk.Button(self.root, text="Pause/Reprendre", command=self.pause_resume)
        btn_pause_resume.pack(pady=5)

        # Bouton d'arrêt
        btn_stop = tk.Button(self.root, text="Arrêt", command=self.stop_music)
        btn_stop.pack(pady=5)

        # Bouton pour lecture aléatoire
        btn_random = tk.Button(self.root, text="Lecture aléatoire", command=self.play_random)
        btn_random.pack(pady=5)

        # Case à cocher pour activer/désactiver l'auto-changement à la fin d'une chanson
        self.auto_shuffle_var = tk.BooleanVar(value=True)
        chk_auto = tk.Checkbutton(self.root, text="Auto changement à la fin", variable=self.auto_shuffle_var)
        chk_auto.pack(pady=5)

        # Label de statut
        self.status_label = tk.Label(self.root, text="Aucune musique chargée.", width=50)
        self.status_label.pack(pady=10)

    def load_directory(self):
        """Charge un dossier et récupère tous les fichiers MP3 de ce répertoire."""
        directory = filedialog.askdirectory(title="Sélectionnez un dossier de musique")
        if directory:
            self.music_directory = directory
            # Sélection des fichiers se terminant par .mp3 (insensible à la casse)
            self.music_list = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(".mp3")]
            if not self.music_list:
                messagebox.showinfo("Info", "Aucun fichier MP3 trouvé dans ce dossier.")
                self.song_combo['values'] = []
                self.song_var.set("")
                self.current_song_path = None
                self.status_label.config(text="Aucune musique chargée.")
            else:
                song_names = [os.path.basename(f) for f in self.music_list]
                self.song_combo['values'] = song_names
                # Sélection par défaut du premier fichier
                self.song_combo.current(0)
                self.current_song_path = self.music_list[0]
                self.status_label.config(text=f"{len(self.music_list)} musiques chargées depuis : {directory}")

    def song_selected(self, event=None):
        """Met à jour la musique sélectionnée dans la liste déroulante."""
        selected_name = self.song_var.get()
        for path in self.music_list:
            if os.path.basename(path) == selected_name:
                self.current_song_path = path
                break
        self.status_label.config(text=f"Morceau sélectionné : {selected_name}")

    def play_selected(self):
        """Charge et joue le morceau sélectionné (depuis le début)."""
        if not self.current_song_path:
            self.status_label.config(text="Aucune musique sélectionnée.")
            return
        try:
            pygame.mixer.music.load(self.current_song_path)
            pygame.mixer.music.play()
            self.is_paused = False
            self.status_label.config(text="Lecture : " + os.path.basename(self.current_song_path))
        except Exception as e:
            self.status_label.config(text="Erreur lors de la lecture.")
            print("Erreur :", e)

    def pause_resume(self):
        """
        Si la musique est en pause, la reprend.
        Si la musique est en cours de lecture, la met en pause.
        Ce bouton n'affecte pas la sélection de la musique.
        """
        if self.current_song_path is None:
            self.status_label.config(text="Aucune musique chargée.")
            return

        # Si déjà en pause, on dépause :
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_label.config(text="Reprise : " + os.path.basename(self.current_song_path))
        else:
            # Sinon, si la musique est en cours, on la met en pause.
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.is_paused = True
                self.status_label.config(text="Pause")
            else:
                self.status_label.config(text="Aucune musique en lecture.")

    def stop_music(self):
        """Arrête la lecture de la musique en cours."""
        pygame.mixer.music.stop()
        self.is_paused = False
        self.status_label.config(text="Lecture arrêtée.")

    def play_random(self):
        """Sélectionne et joue une musique aléatoire parmi la liste, différente du morceau actuel si possible."""
        if not self.music_list:
            self.status_label.config(text="Liste de musique vide.")
            return
        next_song = random.choice(self.music_list)
        if self.current_song_path and len(self.music_list) > 1:
            while next_song == self.current_song_path:
                next_song = random.choice(self.music_list)
        self.current_song_path = next_song
        self.song_var.set(os.path.basename(next_song))
        try:
            pygame.mixer.music.load(next_song)
            pygame.mixer.music.play()
            self.is_paused = False
            self.status_label.config(text="Lecture : " + os.path.basename(next_song))
        except Exception as e:
            self.status_label.config(text="Erreur lors de la lecture aléatoire.")
            print("Erreur :", e)

    def check_playback(self):
        """
        Vérifie, toutes les secondes, si la musique est terminée.
        Si l'auto-shuffle est activé et que la musique s'est naturellement arrêtée,
        lance automatiquement une lecture aléatoire.
        """
        # Si la musique n'est plus diffusée et n'est pas en pause…
        if not pygame.mixer.music.get_busy() and not self.is_paused:
            if self.auto_shuffle_var.get() and self.current_song_path is not None:
                self.play_random()
        self.root.after(1000, self.check_playback)

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.mainloop()