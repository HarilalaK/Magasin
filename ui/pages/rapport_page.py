# ui/pages/rapport_page.py
import customtkinter as ctk
from tkinter import ttk, messagebox, Menu
from datetime import datetime, date
import os

class RapportPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre de la page
        title = ctk.CTkLabel(
            self, 
            text="📊 Rapports de Ventes (Clic droit pour les actions)", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Frame principale
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Section de filtrage
        filter_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        filter_frame.grid_columnconfigure(4, weight=1)
        
        # Type de recherche
        ctk.CTkLabel(filter_frame, text="Rechercher par:").grid(row=0, column=0, padx=5, pady=5)
        self.type_recherche = ctk.CTkOptionMenu(
            filter_frame, 
            values=["Tous", "Nom Client", "Date", "Montant"],
            width=120
        )
        self.type_recherche.grid(row=0, column=1, padx=5, pady=5)
        
        # Champ de recherche
        self.entry_recherche = ctk.CTkEntry(
            filter_frame, 
            placeholder_text="Terme de recherche",
            width=200
        )
        self.entry_recherche.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Sélecteur de date
        self.date_picker = ctk.CTkSegmentedButton(
            filter_frame, 
            values=["Aujourd'hui", "Cette semaine", "Ce mois", "Personnalisé"],
            width=300
        )
        self.date_picker.grid(row=0, column=3, padx=5, pady=5)
        
        # Bouton de filtrage
        btn_filtrer = ctk.CTkButton(
            filter_frame, 
            text="🔍 Rechercher", 
            command=self.filtrer_ventes,
            fg_color="#1976d2",
            hover_color="#1565c0"
        )
        btn_filtrer.grid(row=0, column=5, padx=5, pady=5)
        
        # Tableau des ventes
        self.setup_ventes_table(main_frame)
        
        # Créer le menu contextuel
        self.create_context_menu()
        
        # Initialiser avec toutes les ventes
        self.load_ventes()
    
    def setup_ventes_table(self, parent):
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Colonnes sans Actions
        columns = ("ID", "Client", "Date", "Montant Total")
        self.tree_ventes = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        # Style pour le Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#f0f0f0", 
                        foreground="black", 
                        rowheight=30,
                        fieldbackground="#f0f0f0")
        style.map("Treeview", 
                  background=[('selected', '#3c8dbc')],
                  foreground=[('selected', 'white')])
        
        # Configuration des colonnes
        self.tree_ventes.column("ID", width=50, anchor="center", stretch=False)
        self.tree_ventes.column("Client", width=150, anchor="w", stretch=True)
        self.tree_ventes.column("Date", width=100, anchor="center", stretch=False)
        self.tree_ventes.column("Montant Total", width=100, anchor="e", stretch=False)
        
        # Titres des colonnes
        for col in columns:
            self.tree_ventes.heading(col, text=col, anchor="center")
        
        # Scrollbars
        scrollbar_vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_ventes.yview)
        scrollbar_horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_ventes.xview)
        
        self.tree_ventes.configure(
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set
        )
        
        # Placement des scrollbars et de la table
        self.tree_ventes.grid(row=0, column=0, sticky="nsew")
        scrollbar_vertical.grid(row=0, column=1, sticky="ns")
        scrollbar_horizontal.grid(row=1, column=0, sticky="ew")
        
        # Bind pour le clic droit
        self.tree_ventes.bind("<Button-3>", self.show_context_menu)
    
    def create_context_menu(self):
        """Créer le menu contextuel"""
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="📄 Voir Détails", 
            command=self.voir_details_vente_selectionnee
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="🖨️ Générer Facture", 
            command=self.generer_facture_selectionnee
        )
    
    def show_context_menu(self, event):
        """Afficher le menu contextuel"""
        # Sélectionner l'item sous le curseur
        item = self.tree_ventes.identify_row(event.y)
        if item:
            self.tree_ventes.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_selected_vente(self):
        """Récupérer la vente sélectionnée"""
        selected_items = self.tree_ventes.selection()
        if not selected_items:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une vente.")
            return None
        
        item = selected_items[0]
        values = self.tree_ventes.item(item, 'values')
        return {
            'id': values[0],
            'client': values[1],
            'date': values[2],
            'montant': values[3]
        }
    
    def voir_details_vente_selectionnee(self):
        """Voir les détails de la vente sélectionnée"""
        vente = self.get_selected_vente()
        if vente:
            self.voir_details_vente(vente['id'])
    
    def generer_facture_selectionnee(self):
        """Générer la facture de la vente sélectionnée"""
        vente = self.get_selected_vente()
        if vente:
            self.generer_facture(vente['id'])
    
    def load_ventes(self, filtres=None):
        # Vider le tableau
        for item in self.tree_ventes.get_children():
            self.tree_ventes.delete(item)
        
        # Récupérer les factures
        factures = self.db.get_all_factures()
        
        # Appliquer les filtres
        if filtres:
            factures = self.appliquer_filtres(factures, filtres)
        
        # Trier par date décroissante
        factures_triees = sorted(factures, key=lambda x: x[2], reverse=True)
        
        # Remplir le tableau
        for facture in factures_triees:
            # Insérer la facture
            self.tree_ventes.insert("", "end", values=(
                facture[0],      # ID
                facture[1],      # Nom Client
                facture[2],      # Date
                f"{facture[3]} Ar",  # Montant Total
            ), tags=('odd' if len(self.tree_ventes.get_children()) % 2 == 0 else 'even',))
        
        # Configuration des tags pour l'alternance des couleurs
        self.tree_ventes.tag_configure('odd', background='#f0f0f0')
        self.tree_ventes.tag_configure('even', background='#ffffff')
    
    def appliquer_filtres(self, factures, filtres):
        """Filtrer les factures selon différents critères"""
        type_recherche = filtres.get('type_recherche', 'Tous')
        terme_recherche = filtres.get('terme_recherche', '').lower().strip()
        
        # Filtrage par période
        periode = filtres.get('periode', 'Tous')
        today = date.today()
        
        # Filtres de date
        date_debut = None
        date_fin = None
        if periode == "Aujourd'hui":
            date_debut = date_fin = today.strftime("%Y-%m-%d")
        elif periode == "Cette semaine":
            date_debut = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            date_fin = today.strftime("%Y-%m-%d")
        elif periode == "Ce mois":
            date_debut = today.replace(day=1).strftime("%Y-%m-%d")
            date_fin = today.strftime("%Y-%m-%d")
        elif periode == "Personnalisé":
            # Vous pouvez ajouter une logique pour sélectionner des dates personnalisées
            pass
        
        # Filtrer les factures
        resultats_filtres = []
        for facture in factures:
            # Filtres de date
            if date_debut and date_fin:
                if not (date_debut <= facture[2] <= date_fin):
                    continue
            
            # Filtres de recherche
            if type_recherche == "Nom Client":
                if terme_recherche and terme_recherche not in facture[1].lower():
                    continue
            elif type_recherche == "Montant":
                try:
                    if terme_recherche and float(terme_recherche) != float(facture[3]):
                        continue
                except ValueError:
                    continue
            
            resultats_filtres.append(facture)
        
        return resultats_filtres
    
    def filtrer_ventes(self):
        # Préparer les filtres
        filtres = {
            'type_recherche': self.type_recherche.get(),
            'terme_recherche': self.entry_recherche.get(),
            'periode': self.date_picker.get()
        }
        
        # Charger les ventes filtrées
        self.load_ventes(filtres)
    
    def voir_details_vente(self, facture_id):
        # Récupérer les détails de la facture
        facture = self.db.get_facture_by_id(facture_id)
        details = self.db.get_facture_details(facture_id)
        
        # Créer une fenêtre de détails
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Détails Facture #{facture_id}")
        details_window.geometry("800x600")
        
        # Informations de la facture
        info_frame = ctk.CTkFrame(details_window, fg_color="transparent")
        info_frame.pack(padx=20, pady=20, fill="x")
        
        ctk.CTkLabel(info_frame, text=f"Facture #{facture_id}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Client : {facture[1]}").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Date : {facture[2]}").pack(anchor="w")
        
        # Tableau des détails
        columns = ("Article", "Unité", "Quantité", "Prix Unitaire", "Prix Total")
        tree_details = ttk.Treeview(details_window, columns=columns, show="headings")
        
        for col in columns:
            tree_details.heading(col, text=col)
            tree_details.column(col, anchor="center")
        
        # Remplir le tableau des détails
        total_facture = 0
        for detail in details:
            total_ligne = detail[6]  # prix_total
            total_facture += total_ligne
            
            tree_details.insert("", "end", values=(
                detail[7],  # article_nom
                detail[8],  # unite_libelle
                detail[4],  # quantite
                f"{detail[5]} Ar",  # prix_unitaire
                f"{total_ligne} Ar"  # prix_total
            ))
        
        # Total de la facture
        tree_details.insert("", "end", values=(
            "", "", "", "TOTAL", f"{total_facture} Ar"
        ))
        
        tree_details.pack(padx=20, pady=(0, 20), fill="both", expand=True)
    
    def generer_facture(self, facture_id):
        # Récupérer les détails de la facture
        facture = self.db.get_facture_by_id(facture_id)
        details = self.db.get_facture_details(facture_id)
        
        # Créer un dossier pour les factures si inexistant
        os.makedirs('factures', exist_ok=True)
        
        # Nom du fichier de facture
        nom_fichier = f'factures/facture_{facture_id}_{facture[1]}_{facture[2]}.txt'
        
        # Générer la facture
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            f.write("===== FACTURE =====\n")
            f.write(f"Numéro : {facture_id}\n")
            f.write(f"Client : {facture[1]}\n")
            f.write(f"Date : {facture[2]}\n\n")
            f.write("Détails des Articles :\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Article':<20} {'Unité':<10} {'Qté':<5} {'P.U.':<10} {'Total':<10}\n")
            f.write("-" * 50 + "\n")
            
            total_facture = 0
            for detail in details:
                article_nom = detail[7]
                unite_libelle = detail[8]
                quantite = detail[4]
                prix_unitaire = detail[5]
                prix_total = detail[6]
                
                total_facture += prix_total
                
                f.write(f"{article_nom:<20} {unite_libelle:<10} {quantite:<5} {prix_unitaire:<10} Ar {prix_total:<10} Ar\n")
            
            f.write("-" * 50 + "\n")
            f.write(f"{'TOTAL':<40} {total_facture} Ar")
        
        messagebox.showinfo("Facture Générée", f"Facture sauvegardée : {nom_fichier}")