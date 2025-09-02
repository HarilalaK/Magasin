import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import tkinter as tk

class EntrepotDetailsWindow(ctk.CTkToplevel):
    def __init__(self, master, db, entrepot):
        super().__init__(master)
        self.db = db
        self.entrepot = entrepot
        
        # Configuration de la fenêtre
        self.title(f"Détails de l'Entrepôt : {entrepot[1]}")
        self.geometry("1000x700")
        
        # Frame principale
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titre
        titre = ctk.CTkLabel(
            self, 
            text=f"📦 Détails de l'Entrepôt : {entrepot[1]}", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        titre.pack(pady=(20, 10))
        
        # Récupérer les statistiques
        stats = self.db.get_entrepot_stats(entrepot[0])
        
        # Frame Articles
        articles_frame = ctk.CTkFrame(main_frame, fg_color="#f9f9fc", corner_radius=10)
        articles_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Titre Articles
        ctk.CTkLabel(
            articles_frame, 
            text="📊 Statistiques Articles", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Détails des articles
        articles_details = ctk.CTkFrame(articles_frame, fg_color="transparent")
        articles_details.pack(fill="x", padx=20, pady=10)
        
        # Total articles et pourcentage
        ctk.CTkLabel(
            articles_details, 
            text=f"Total Articles: {stats['total_articles']}\n"
                 f"Pourcentage du Stock: {stats['pourcentage_articles']}%", 
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # Répartition par unité
        unite_frame = ctk.CTkFrame(articles_frame, fg_color="transparent")
        unite_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            unite_frame, 
            text="Répartition par Unité:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        for unite in stats['repartition_unites']:
            ctk.CTkLabel(
                unite_frame, 
                text=f"{unite[0]}: {unite[1]} articles ({unite[2]}%)", 
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w")
        
        # Frame Ventes
        ventes_frame = ctk.CTkFrame(main_frame, fg_color="#f0f0f0", corner_radius=10)
        ventes_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        # Titre Ventes
        ctk.CTkLabel(
            ventes_frame, 
            text="💰 Statistiques de Vente", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Détails des ventes
        ventes_details = ctk.CTkFrame(ventes_frame, fg_color="transparent")
        ventes_details.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            ventes_details, 
            text=f"Quantité Totale Vendue: {stats['total_quantite_vendue']:.2f}\n"
                 f"Total des Ventes: {stats['total_ventes']:,.2f} Ar", 
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # Frame pour le tableau des articles
        articles_table_frame = ctk.CTkFrame(main_frame, fg_color="#ffffff", corner_radius=10)
        articles_table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Titre du tableau
        ctk.CTkLabel(
            articles_table_frame, 
            text="📋 Liste des Articles", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Treeview pour les articles
        self.tree_articles = ttk.Treeview(
            articles_table_frame, 
            columns=("Nom", "Référence", "Unités"), 
            show="headings"
        )
        self.tree_articles.heading("Nom", text="Nom de l'Article")
        self.tree_articles.heading("Référence", text="Référence")
        self.tree_articles.heading("Unités", text="Unités Disponibles")
        
        # Configurer les colonnes
        self.tree_articles.column("Nom", width=250)
        self.tree_articles.column("Référence", width=150)
        self.tree_articles.column("Unités", width=250)
        
        self.tree_articles.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(articles_table_frame, orient="vertical", command=self.tree_articles.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_articles.configure(yscrollcommand=scrollbar.set)
        
        # Charger les articles de l'entrepôt
        self.charger_articles_entrepot()
    
    def charger_articles_entrepot(self):
        # Vider le treeview
        for i in self.tree_articles.get_children():
            self.tree_articles.delete(i)
        
        # Récupérer les articles de l'entrepôt
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.nom, a.reference, 
                   GROUP_CONCAT(u.libelle || ' (' || pa.prix_unitaire || ' Ar)') as unites
            FROM article a
            LEFT JOIN prix_article pa ON a.id = pa.article_id
            LEFT JOIN unite u ON pa.unite_id = u.id
            WHERE a.entrepot_id = ? AND a.actif = 1
            GROUP BY a.id, a.nom, a.reference
        """, (self.entrepot[0],))
        
        articles = cursor.fetchall()
        conn.close()
        
        # Ajouter les articles au treeview
        for article in articles:
            self.tree_articles.insert("", "end", values=(
                article[1],  # Nom
                article[2],  # Référence
                article[3] or "Aucune unité"  # Unités
            ))

class EntrepotPage(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        
        # Configuration du layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre de la page
        titre = ctk.CTkLabel(
            self, 
            text="🏢 Gestion des Entrepôts", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titre.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame pour le formulaire et la liste
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Frame pour le formulaire
        form_frame = ctk.CTkFrame(main_frame, fg_color="#f9f9fc", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Titre du formulaire
        form_titre = ctk.CTkLabel(
            form_frame, 
            text="Ajouter/Modifier un Entrepôt", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        form_titre.pack(pady=(15, 10))
        
        # Frame principale pour les champs
        input_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=20, pady=10)
        input_container.columnconfigure(1, weight=1)
        
        # Champ Nom
        ctk.CTkLabel(
            input_container, 
            text="Nom de l'Entrepôt:", 
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.nom_entry = ctk.CTkEntry(
            input_container, 
            width=300,
            height=35  # Hauteur uniforme
        )
        self.nom_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Champ Localisation
        ctk.CTkLabel(
            input_container, 
            text="Localisation:", 
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.loc_entry = ctk.CTkEntry(
            input_container, 
            width=300,
            height=35  # Hauteur uniforme
        )
        self.loc_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Boutons d'action
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_ajouter = ctk.CTkButton(
            btn_frame, 
            text="Ajouter Entrepôt", 
            command=self.ajouter_entrepot,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.btn_ajouter.pack(side="left", padx=(0, 10))
        
        self.btn_modifier = ctk.CTkButton(
            btn_frame, 
            text="Modifier", 
            command=self.modifier_entrepot,
            fg_color="#2196F3",
            hover_color="#1976D2",
            state="disabled"
        )
        self.btn_modifier.pack(side="left", padx=(0, 10))
        
        self.btn_annuler = ctk.CTkButton(
            btn_frame, 
            text="Annuler", 
            command=self.reset_form,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        self.btn_annuler.pack(side="left")
        
        # Frame pour la liste des entrepôts
        liste_frame = ctk.CTkFrame(main_frame, fg_color="#ffffff", corner_radius=10)
        liste_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        # Titre de la liste
        liste_titre = ctk.CTkLabel(
            liste_frame, 
            text="Liste des Entrepôts", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        liste_titre.pack(pady=(15, 10))
        
        # Treeview pour la liste des entrepôts
        self.tree_entrepots = ttk.Treeview(
            liste_frame, 
            columns=("Nom", "Localisation"), 
            show="headings"
        )
        self.tree_entrepots.heading("Nom", text="Nom")
        self.tree_entrepots.heading("Localisation", text="Localisation")
        self.tree_entrepots.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(liste_frame, orient="vertical", command=self.tree_entrepots.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_entrepots.configure(yscrollcommand=scrollbar.set)
        
        # Événements
        self.tree_entrepots.bind("<Double-1>", self.voir_details_entrepot)
        self.tree_entrepots.bind("<Button-3>", self.show_context_menu)
        
        # Menu contextuel
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Modifier", command=self.selectionner_entrepot_menu)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_entrepot)
        self.context_menu.add_command(label="Voir Articles", command=self.voir_details_entrepot_menu)
        
        # Charger les entrepôts initiaux
        self.charger_entrepots()
        
        # ID de l'entrepôt sélectionné (pour modification)
        self.selected_entrepot_id = None
    
    def ajouter_entrepot(self):
        nom = self.nom_entry.get().strip()
        localisation = self.loc_entry.get().strip()
        
        if not nom:
            messagebox.showerror("Erreur", "Le nom de l'entrepôt est obligatoire.")
            return
        
        entrepot_id = self.db.create_entrepot(nom, localisation)
        
        if entrepot_id:
            messagebox.showinfo("Succès", f"Entrepôt '{nom}' ajouté avec succès.")
            self.reset_form()
            self.charger_entrepots()
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter l'entrepôt.")
    
    def modifier_entrepot(self):
        if not self.selected_entrepot_id:
            messagebox.showerror("Erreur", "Aucun entrepôt sélectionné.")
            return
        
        nom = self.nom_entry.get().strip()
        localisation = self.loc_entry.get().strip()
        
        if not nom:
            messagebox.showerror("Erreur", "Le nom de l'entrepôt est obligatoire.")
            return
        
        success = self.db.update_entrepot(self.selected_entrepot_id, nom, localisation)
        
        if success:
            messagebox.showinfo("Succès", f"Entrepôt '{nom}' modifié avec succès.")
            self.reset_form()
            self.charger_entrepots()
        else:
            messagebox.showerror("Erreur", "Impossible de modifier l'entrepôt.")
    
    def supprimer_entrepot(self):
        selected_item = self.tree_entrepots.selection()
        if not selected_item:
            messagebox.showerror("Erreur", "Aucun entrepôt sélectionné.")
            return
        
        # Récupérer l'ID de l'entrepôt
        entrepot_id = self.tree_entrepots.item(selected_item[0])['values'][2]
        nom = self.tree_entrepots.item(selected_item[0])['values'][0]
        
        # Confirmation de suppression
        confirm = messagebox.askyesno(
            "Confirmation", 
            f"Voulez-vous vraiment supprimer l'entrepôt '{nom}' ?"
        )
        
        if confirm:
            success = self.db.delete_entrepot(entrepot_id)
            if success:
                messagebox.showinfo("Succès", f"Entrepôt '{nom}' supprimé avec succès.")
                self.reset_form()
                self.charger_entrepots()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer l'entrepôt.")
    
    def selectionner_entrepot(self, event=None):
        selected_item = self.tree_entrepots.selection()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.tree_entrepots.item(selected_item[0])['values']
        
        # Remplir le formulaire
        self.nom_entry.delete(0, "end")
        self.nom_entry.insert(0, values[0])
        
        self.loc_entry.delete(0, "end")
        self.loc_entry.insert(0, values[1])
        
        # Activer le bouton de modification
        self.btn_ajouter.configure(state="disabled")
        self.btn_modifier.configure(state="normal")
        
        # Stocker l'ID de l'entrepôt sélectionné
        self.selected_entrepot_id = values[2]
    
    def selectionner_entrepot_menu(self):
        # Méthode pour le menu contextuel
        selected_item = self.tree_entrepots.selection()
        if selected_item:
            self.selectionner_entrepot()
    
    def reset_form(self):
        # Réinitialiser les champs
        self.nom_entry.delete(0, "end")
        self.loc_entry.delete(0, "end")
        
        # Réinitialiser les boutons
        self.btn_ajouter.configure(state="normal")
        self.btn_modifier.configure(state="disabled")
        
        # Réinitialiser l'ID sélectionné
        self.selected_entrepot_id = None
    
    def charger_entrepots(self):
        # Vider le treeview
        for i in self.tree_entrepots.get_children():
            self.tree_entrepots.delete(i)
        
        # Récupérer les entrepôts
        entrepots = self.db.get_all_entrepots()
        
        # Ajouter les entrepôts au treeview
        for entrepot in entrepots:
            self.tree_entrepots.insert(
                "", 
                "end", 
                values=(entrepot[1], entrepot[2] or "Non spécifiée", entrepot[0])
            )
    
    def show_context_menu(self, event):
        # Sélectionner la ligne sur laquelle on a cliqué
        iid = self.tree_entrepots.identify_row(event.y)
        if iid:
            self.tree_entrepots.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)
    
    def voir_details_entrepot(self, event=None):
        selected_item = self.tree_entrepots.selection()
        if not selected_item:
            return
        
        # Récupérer les valeurs de l'entrepôt
        values = self.tree_entrepots.item(selected_item[0])['values']
        
        # Trouver l'entrepôt complet
        entrepots = self.db.get_all_entrepots()
        entrepot = next((e for e in entrepots if e[1] == values[0]), None)
        
        if entrepot:
            # Ouvrir la fenêtre de détails
            EntrepotDetailsWindow(self, self.db, entrepot)
    
    def voir_details_entrepot_menu(self):
        # Méthode pour le menu contextuel
        selected_item = self.tree_entrepots.selection()
        if selected_item:
            self.voir_details_entrepot()