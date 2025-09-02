#!/usr/bin/env python3
"""
Application de Gestion de Vente
Point d'entrée principal
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.init_db import init_database
    from ui.main_app import MainApp
    
    def main():
        """Fonction principale"""
        print("🚀 Démarrage de l'application de gestion de vente...")
        
        # Initialiser la base de données
        init_database()
        
        # Lancer l'application
        app = MainApp()
        app.mainloop()
        
        print("👋 Application fermée")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("🔧 Assurez-vous d'avoir installé les dépendances : pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Erreur lors du démarrage : {e}")
    sys.exit(1)