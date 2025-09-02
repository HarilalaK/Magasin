import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

class UnitePage(ctk.CTkFrame):
    def __init__(self, parent,db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.db = DatabaseManager()
        self.selected_unite_id = None
        self.setup_ui()
        self.load_unites()
        
    def setup_ui(self):
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre
        title = ctk.CTkLabel(
            self, 
            text="📏 Gestion des Unités", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Frame principal avec deux colonnes
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Colonne gauche - Formulaire
        self.setup_form(main_frame)
        
        # Colonne droite - Liste des unités
        self.setup_liste(main_frame)
        
    def setup_form(self, parent):
        # Frame pour le formulaire
        form_frame = ctk.CTkFrame(parent)
        form_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Titre du formulaire
        self.form_title = ctk.CTkLabel(
            form_frame, 
            text="➕ Nouvelle Unité", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Code de l'unité
        ctk.CTkLabel(form_frame, text="Code:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_code = ctk.CTkEntry(form_frame, placeholder_text="Ex: KG, L, PCS...")
        self.entry_code.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        # Libellé de l'unité
        ctk.CTkLabel(form_frame, text="Libellé:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_libelle = ctk.CTkEntry(form_frame, placeholder_text="Ex: Kilogramme, Litre, Pièce...")
        self.entry_libelle.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        
        self.btn_ajouter = ctk.CTkButton(
            buttons_frame, 
            text="➕ Ajouter",
            command=self.ajouter_unite,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        self.btn_ajouter.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.btn_modifier = ctk.CTkButton(
            buttons_frame, 
            text="✏️ Modifier",
            command=self.modifier_unite,
            fg_color="#ed6c02",
            hover_color="#e65100"
        )
        self.btn_modifier.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.btn_annuler = ctk.CTkButton(
            buttons_frame, 
            text="❌ Annuler",
            command=self.annuler_modification,
            fg_color="#757575",
            hover_color="#424242"
        )
        self.btn_annuler.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # Séparateur
        separator = ctk.CTkFrame(form_frame, height=2, fg_color="#3a3a3a")
        separator.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        # Informations d'aide
        info_frame = ctk.CTkFrame(form_frame, fg_color="#1a1a1a")
        info_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        info_title = ctk.CTkLabel(
            info_frame, 
            text="💡 Conseils",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        info_text = ctk.CTkLabel(
            info_frame, 
            text="• Code: Abréviation courte (KG, L, PCS, SAC...)\n• Libellé: Nom complet de l'unité\n• Double-clic sur une unité pour la modifier\n• Suppression: Sélectionnez et appuyez sur Suppr",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        info_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
    def setup_liste(self, parent):
        # Frame pour la liste
        liste_frame = ctk.CTkFrame(parent)
        liste_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        liste_frame.grid_columnconfigure(0, weight=1)
        liste_frame.grid_rowconfigure(1, weight=1)
        
        # Titre et boutons
        header_frame = ctk.CTkFrame(liste_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        liste_title = ctk.CTkLabel(
            header_frame, 
            text="📋 Liste des Unités", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        liste_title.grid(row=0, column=0, sticky="w")
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=1, column=0, pady=10, sticky="ew")
        actions_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_supprimer = ctk.CTkButton(
            actions_frame, 
            text="🗑️ Supprimer",
            command=self.supprimer_unite,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=100
        )
        self.btn_supprimer.grid(row=0, column=0, sticky="w")
        
        self.btn_rafraichir = ctk.CTkButton(
            actions_frame, 
            text="🔄 Rafraîchir",
            command=self.load_unites,
            fg_color="#1976d2",
            hover_color="#0d47a1",
            width=100
        )
        self.btn_rafraichir.grid(row=0, column=1, padx=(10, 0), sticky="w")
        
        # Tableau des unités
        self.setup_table(liste_frame)
        
    def setup_table(self, parent):
        # Frame pour le tableau
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview pour les unités
        columns = ("ID", "Code", "Libellé")
        self.tree_unites = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configuration des colonnes
        self.tree_unites.heading("ID", text="ID")
        self.tree_unites.heading("Code", text="Code")
        self.tree_unites.heading("Libellé", text="Libellé")
        
        self.tree_unites.column("ID", width=50, anchor="center")
        self.tree_unites.column("Code", width=100, anchor="center")
        self.tree_unites.column("Libellé", width=200, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_unites.yview)
        self.tree_unites.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.tree_unites.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind events
        self.tree_unites.bind("<Double-1>", self.on_double_click)
        self.tree_unites.bind("<KeyPress-Delete>", self.on_delete_key)
        
        # Statistiques
        self.label_stats = ctk.CTkLabel(
            parent, 
            text="", 
            font=ctk.CTkFont(size=12)
        )
        self.label_stats.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
    def load_unites(self):
        """Charge les unités depuis la base de données"""
        try:
            # Vider le tableau
            for item in self.tree_unites.get_children():
                self.tree_unites.delete(item)
            
            # Charger les unités
            unites = self.db.get_all_unites()
            
            for unite in unites:
                self.tree_unites.insert("", "end", values=(
                    unite[0],  # ID
                    unite[1],  # Code
                    unite[2]   # Libellé
                ))
            
            # Mettre à jour les statistiques
            self.label_stats.configure(text=f"📊 Total: {len(unites)} unité(s)")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")
    
    def ajouter_unite(self):
        """Ajoute une nouvelle unité"""
        try:
            # Validation
            code = self.entry_code.get().strip().upper()
            libelle = self.entry_libelle.get().strip()
            
            if not code:
                messagebox.showwarning("Attention", "Veuillez saisir le code de l'unité")
                return
            
            if not libelle:
                messagebox.showwarning("Attention", "Veuillez saisir le libellé de l'unité")
                return
            
            # Ajouter l'unité
            self.db.add_unite(code, libelle)
            
            # Rafraîchir la liste
            self.load_unites()
            
            # Vider les champs
            self.entry_code.delete(0, "end")
            self.entry_libelle.delete(0, "end")
            
            messagebox.showinfo("Succès", f"Unité '{code}' ajoutée avec succès !")
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erreur", f"Le code '{code}' existe déjà !")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {e}")
    
    def modifier_unite(self):
        """Modifie l'unité sélectionnée"""
        try:
            if not self.selected_unite_id:
                messagebox.showwarning("Attention", "Veuillez sélectionner une unité à modifier")
                return
            
            # Validation
            code = self.entry_code.get().strip().upper()
            libelle = self.entry_libelle.get().strip()
            
            if not code:
                messagebox.showwarning("Attention", "Veuillez saisir le code de l'unité")
                return
            
            if not libelle:
                messagebox.showwarning("Attention", "Veuillez saisir le libellé de l'unité")
                return
            
            # Modifier l'unité
            self.db.update_unite(self.selected_unite_id, code, libelle)
            
            # Rafraîchir la liste
            self.load_unites()
            
            # Reset du formulaire
            self.annuler_modification()
            
            messagebox.showinfo("Succès", f"Unité '{code}' modifiée avec succès !")
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erreur", f"Le code '{code}' existe déjà !")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")
    
    def supprimer_unite(self):
        """Supprime l'unité sélectionnée"""
        try:
            selection = self.tree_unites.selection()
            if not selection:
                messagebox.showwarning("Attention", "Veuillez sélectionner une unité à supprimer")
                return
            
            item = self.tree_unites.item(selection[0])
            unite_id = item['values'][0]
            code = item['values'][1]
            
            # Confirmation
            if messagebox.askyesno("Confirmation", f"Supprimer l'unité '{code}' ?\n\nAttention: Cette action est irréversible !"):
                self.db.delete_unite(unite_id)
                self.load_unites()
                self.annuler_modification()
                messagebox.showinfo("Succès", f"Unité '{code}' supprimée avec succès !")
                
        except Exception as e:
            if "FOREIGN KEY constraint failed" in str(e):
                messagebox.showerror("Erreur", "Impossible de supprimer cette unité car elle est utilisée par des articles !")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    
    def annuler_modification(self):
        """Annule la modification en cours"""
        self.selected_unite_id = None
        self.entry_code.delete(0, "end")
        self.entry_libelle.delete(0, "end")
        self.form_title.configure(text="➕ Nouvelle Unité")
        self.btn_ajouter.configure(text="➕ Ajouter")
        
        # Désélectionner dans le tableau
        for item in self.tree_unites.selection():
            self.tree_unites.selection_remove(item)
    
    def on_double_click(self, event):
        """Gère le double-clic sur une unité"""
        selection = self.tree_unites.selection()
        if selection:
            item = self.tree_unites.item(selection[0])
            values = item['values']
            
            # Remplir le formulaire
            self.selected_unite_id = values[0]
            self.entry_code.delete(0, "end")
            self.entry_code.insert(0, values[1])
            self.entry_libelle.delete(0, "end")
            self.entry_libelle.insert(0, values[2])
            
            # Changer le titre et le bouton
            self.form_title.configure(text="✏️ Modifier Unité")
            self.btn_ajouter.configure(text="💾 Sauvegarder")
    
    def on_delete_key(self, event):
        """Gère la suppression avec la touche Suppr"""
        self.supprimer_unite()