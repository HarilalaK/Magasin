import customtkinter as ctk
from database.db_manager import DatabaseManager
from ui.pages.home_page import HomePage
from ui.pages.unite_page import UnitePage
from ui.pages.article_page import ArticlePage
from ui.pages.rapport_page import RapportPage
from ui.pages.entrepot_page import EntrepotPage
from ui.pages.inventaire_page import InventairePage
from PIL import Image
import os

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de l'apparence
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configuration de la fenêtre
        self.title("🏪 Gestion de Vente")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Initialiser la base de données
        self.db = DatabaseManager()
        
        # Variables
        self.current_page = None
        self.current_button = None
        
        # Créer l'interface
        self.create_layout()
        
        # Charger le logo
        self.load_logo()
        
        # Afficher la page d'accueil par défaut
        self.show_home_page()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_layout(self):
        """Crée le layout principal avec sidebar et zone de contenu"""
        
        # Frame principale
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        # Configuration du grid
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Créer la sidebar (25%)
        self.create_sidebar()
        
        # Créer la zone de contenu (75%)
        self.create_content_area()
    
    def create_sidebar(self):
        """Crée la sidebar avec les boutons de navigation"""
        
        # Frame sidebar avec couleurs claires
        self.sidebar_frame = ctk.CTkFrame(
            self.main_frame, 
            width=280, 
            corner_radius=0,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#e9ecef"
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # Header avec logo
        self.header_frame = ctk.CTkFrame(
            self.sidebar_frame, 
            height=120,  # Augmenté de 80 à 120
            fg_color="#ffffff",
            corner_radius=0
        )
        self.header_frame.pack(fill="x", pady=(0, 1))
        self.header_frame.pack_propagate(False)
        
        # Logo
        self.logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.logo_frame.pack(expand=True, fill="both")
        
        # Espace pour le logo (sera rempli par load_logo())
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, 
            text="🏪",
            font=ctk.CTkFont(size=48),  # Augmenté de 32 à 48
            text_color="#495057"
        )
        self.logo_label.pack(expand=True)
        
        # Navigation section
        self.nav_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.nav_frame.pack(fill="both", expand=True, padx=0, pady=10)
        
        # Label Navigation
        self.nav_label = ctk.CTkLabel(
            self.nav_frame,
            text="NAVIGATION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6c757d"
        )
        self.nav_label.pack(pady=(10, 15), padx=20, anchor="w")
        
        # Boutons de navigation
        self.nav_buttons = []
        
        # Bouton Home
        self.home_btn = self.create_nav_button(
            self.nav_frame,
            "🏠",
            "Accueil",
            self.show_home_page
        )
        self.nav_buttons.append(self.home_btn)
        
        # Bouton Unités
        self.unite_btn = self.create_nav_button(
            self.nav_frame,
            "📏",
            "Unités",
            self.show_unite_page
        )
        self.nav_buttons.append(self.unite_btn)
        
        # Bouton Articles
        self.article_btn = self.create_nav_button(
            self.nav_frame,
            "📦",
            "Articles & Prix",
            self.show_article_page
        )
        self.nav_buttons.append(self.article_btn)
        
        
        
        # Bouton Entrepôts
        self.entrepot_btn = self.create_nav_button(
            self.nav_frame,
            "🏢",
            "Entrepôts",
            self.show_entrepot_page
        )
        self.nav_buttons.append(self.entrepot_btn)
        
        # Bouton Rapports
        self.rapport_btn = self.create_nav_button(
            self.nav_frame,
            "📊",
            "Rapports",
            self.show_rapport_page
        )
        self.nav_buttons.append(self.rapport_btn)

        # Bouton Inventaire
        self.inventaire_btn = self.create_nav_button(
            self.nav_frame,
            "📋",
            "Inventaire",
            self.show_inventaire_page
        )
        self.nav_buttons.append(self.inventaire_btn)
        
        # Séparateur
        self.separator = ctk.CTkFrame(
            self.nav_frame,
            height=1,
            fg_color="#e9ecef"
        )
        self.separator.pack(fill="x", pady=20, padx=20)
        
        # Espace flexible
        self.spacer = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        self.spacer.pack(fill="both", expand=True)
        
        # Footer avec citation biblique
        self.footer_frame = ctk.CTkFrame(
            self.sidebar_frame,
            height=80,
            fg_color="#ffffff",
            corner_radius=0
        )
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)
        
        # Citation biblique
        self.quote_label = ctk.CTkLabel(
            self.footer_frame,
            text="\"Ho tahiana ianao raha miditra,\nho tahiana ianao raha mivoaka\"",
            font=ctk.CTkFont(size=12),
            text_color="#0f3a61",
            justify="center"
        )
        self.quote_label.pack(expand=True, padx=15)
    
    def create_nav_button(self, parent, icon, text, command):
        """Crée un bouton de navigation avec style professionnel"""
        
        # Frame pour le bouton
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent", height=45)
        btn_frame.pack(fill="x", padx=10, pady=2)
        btn_frame.pack_propagate(False)
        
        # Bouton principal
        btn = ctk.CTkButton(
            btn_frame,
            text=f"{icon}  {text}",
            font=ctk.CTkFont(size=14),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            text_color="#495057",
            hover_color="#e9ecef",
            command=command
        )
        btn.pack(fill="both", expand=True, padx=5)
        
        return btn
    
    def load_logo(self):
        """Charge et affiche le logo"""
        try:
            # Chemin vers le logo
            logo_path = os.path.join("assets", "images", "logo.png")
            
            # Vérifier si le fichier existe
            if os.path.exists(logo_path):
                # Charger et redimensionner l'image
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)  # Augmenté de 50x50 à 80x80
                
                # Convertir en CTkImage
                logo_ctk = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=(80, 80)  # Augmenté de 50x50 à 80x80
                )
                
                # Mettre à jour le label avec l'image
                self.logo_label.configure(
                    image=logo_ctk,
                    text=""  # Enlever le texte
                )
            else:
                # Si le fichier n'existe pas, garder l'emoji
                print(f"Logo non trouvé dans : {logo_path}")
                print("Utilisation de l'emoji par défaut")
                
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {e}")
            print("Utilisation de l'emoji par défaut")
    
    def create_content_area(self):
        """Crée la zone de contenu principal"""
        
        # Frame contenu
        self.content_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=0,
            fg_color="#ffffff"
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def clear_content(self):
        """Efface le contenu actuel"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_page = None
    
    def set_active_button(self, active_button):
        """Met en surbrillance le bouton actif"""
        # Réinitialiser tous les boutons
        for btn in self.nav_buttons:
            btn.configure(
                fg_color="transparent",
                text_color="#495057"
            )
        
        # Mettre en surbrillance le bouton actif
        active_button.configure(
            fg_color="#0d6efd",
            text_color="#ffffff"
        )
        self.current_button = active_button
    
    def show_home_page(self):
        """Affiche la page d'accueil (vente)"""
        self.clear_content()
        self.set_active_button(self.home_btn)
        
        self.current_page = HomePage(self.content_frame, self.db)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_unite_page(self):
        """Affiche la page de gestion des unités"""
        self.clear_content()
        self.set_active_button(self.unite_btn)
        
        self.current_page = UnitePage(self.content_frame, self.db)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_article_page(self):
        """Affiche la page de gestion des articles"""
        self.clear_content()
        self.set_active_button(self.article_btn)
        
        self.current_page = ArticlePage(self.content_frame, self.db)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_rapport_page(self):
        """Affiche la page des rapports"""
        self.clear_content()
        self.set_active_button(self.rapport_btn)
        
        self.current_page = RapportPage(self.content_frame, self.db)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)

    def show_entrepot_page(self):
        """Affiche la page de gestion des entrepôts"""
        self.clear_content()
        self.set_active_button(self.entrepot_btn)
        
        self.current_page = EntrepotPage(self.content_frame, self.db)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)

    def show_inventaire_page(self):
        """Affiche la page d'inventaire"""
        self.clear_content()
        self.set_active_button(self.inventaire_btn)
        
        self.current_page = InventairePage(self.content_frame, self.db)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()