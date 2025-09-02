import os
import subprocess
import sys

def build_exe():
    """Script pour créer l'exécutable"""
    
    print("🚀 Création de l'exécutable...")
    
    # Commande PyInstaller
    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--name=GestionVente",
        "--icon=assets/images/logo.ico",
        "--add-data=assets;assets",  # ou :assets sur Linux
        "--hidden-import=customtkinter",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=reportlab",
        "main.py"
    ]

    
    try:
        # Exécuter la commande
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ Exécutable créé avec succès !")
        print("📁 Fichier créé : dist/GestionVente.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création : {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        
    except FileNotFoundError:
        print("❌ PyInstaller n'est pas installé !")
        print("Installez-le avec : pip install pyinstaller")

if __name__ == "__main__":
    build_exe()
