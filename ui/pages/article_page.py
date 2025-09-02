import customtkinter as ctk
from tkinter import ttk, messagebox, Canvas
from database.db_manager import DatabaseManager
from ui.pages.article_trash_page import ArticleTrashPage

class ArticlePage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")

        self.db = DatabaseManager()
        self.selected_article_id = None
        self.setup_ui()
        self.load_articles()
        self.unite_vars = {}  # Stocker les variables pour chaque unité

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Frame pour le titre et le bouton corbeille
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="📦 Gestion des Articles",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")

        # Bouton Corbeille
        btn_corbeille = ctk.CTkButton(
            header_frame,
            text="🗑️ Corbeille",
            width=100,
            fg_color="#757575",
            hover_color="#424242",
            command=self.open_trash_page
        )
        btn_corbeille.grid(row=0, column=1, padx=(10, 0), sticky="e")

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        self.setup_articles_list(main_frame)
        self.setup_article_form(main_frame)

    def setup_articles_list(self, parent):
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.grid(row=0, column=0, padx=(0, 10), pady=(20, 20), sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)  # Pour que la recherche prenne l'espace disponible

        list_title = ctk.CTkLabel(
            header_frame,
            text="📋 Liste des Articles",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.grid(row=0, column=0, sticky="w", padx=(0, 15))

        # Frame de recherche avec style
        search_frame = ctk.CTkFrame(header_frame, fg_color="#F0F0F0", corner_radius=8)
        search_frame.grid(row=0, column=1, sticky="ew", padx=5)

        # Icône de recherche
        search_icon = ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=13)
        )
        search_icon.pack(side="left", padx=(10, 0))

        # Champ de recherche
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Rechercher un article...",
            border_width=0,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#F0F0F0",
            textvariable=self.search_var
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        # Bind l'événement de recherche
        self.search_var.trace_add("write", self.filter_articles)

        self.setup_articles_table(list_frame)

    def filter_articles(self, *args):
        """Filtre les articles en fonction du texte de recherche"""
        search_text = self.search_var.get().lower()
        
        # Si le treeview existe
        if hasattr(self, 'tree_articles'):
            if not search_text:  # Si le champ de recherche est vide
                # Recharger tous les articles
                self.load_articles()
                return
                
            # Pour chaque article dans le tableau
            for item in self.tree_articles.get_children():
                # Récupérer les valeurs de l'élément
                values = self.tree_articles.item(item)['values']
                # Convertir toutes les valeurs en chaînes de caractères et les joindre
                item_text = ' '.join(str(value).lower() for value in values if value is not None)
                
                # Si le texte de recherche est dans l'élément
                if search_text in item_text:
                    self.tree_articles.reattach(item, '', 'end')  # Montrer l'élément
                else:
                    self.tree_articles.detach(item)  # Cacher l'élément

    def setup_articles_table(self, parent):
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Colonnes avec des largeurs proportionnelles
        columns = ("ID", "Nom", "Référence", "Unités et Prix")
        self.tree_articles = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # Style pour le Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#f0f0f0", 
                        foreground="black", 
                        rowheight=25,
                        fieldbackground="#f0f0f0")
        style.map("Treeview", 
                  background=[('selected', '#3c8dbc')],
                  foreground=[('selected', 'white')])

        # Configuration des colonnes avec des largeurs ajustées
        self.tree_articles.column("ID", width=50, anchor="center", stretch=False)
        self.tree_articles.column("Nom", width=150, anchor="w", stretch=True)
        self.tree_articles.column("Référence", width=100, anchor="center", stretch=False)
        self.tree_articles.column("Unités et Prix", width=250, anchor="w", stretch=True)

        # Titres des colonnes
        for col in columns:
            self.tree_articles.heading(col, text=col, anchor="center")

        # Scrollbars verticale et horizontale
        scrollbar_vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_articles.yview)
        scrollbar_horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_articles.xview)
        
        self.tree_articles.configure(
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set
        )

        # Placement des scrollbars
        self.tree_articles.grid(row=0, column=0, sticky="nsew")
        scrollbar_vertical.grid(row=0, column=1, sticky="ns")
        scrollbar_horizontal.grid(row=1, column=0, sticky="ew")

        # Configuration du poids des lignes et colonnes
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Liaison des événements
        self.tree_articles.bind("<Double-1>", self.on_article_double_click)

    def setup_article_form(self, parent):
        # Frame avec bordure et style amélioré
        form_frame = ctk.CTkFrame(
            parent, 
            fg_color="#f9f9fc",  # Fond légèrement bleuté
            corner_radius=12,    # Coins plus arrondis
            border_width=1,      # Bordure fine
            border_color="#e1e4e8"  # Couleur de bordure élégante
        )
        form_frame.grid(row=0, column=1, padx=(10, 0), pady=(20, 20), sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=3)  # Colonne des champs plus large

        self.form_title = ctk.CTkLabel(
            form_frame,
            text="➕ Ajouter Article",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#333333"  # Correction : utiliser text_color au lieu de color
        )
        self.form_title.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="w", padx=15)

        # Ligne 1 : Nom
        ctk.CTkLabel(form_frame, text="Nom de l'article :", anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=15)
        self.entry_nom = ctk.CTkEntry(form_frame, width=300)
        self.entry_nom.grid(row=1, column=1, sticky="ew", pady=5, padx=(0, 15))

        # Ligne 2 : Référence
        ctk.CTkLabel(form_frame, text="Référence :").grid(row=2, column=0, sticky="w", pady=5, padx=15)
        self.entry_reference = ctk.CTkEntry(form_frame, width=300)
        self.entry_reference.grid(row=2, column=1, sticky="ew", pady=5, padx=(0, 15))

        # Ligne 3 : Entrepôt
        ctk.CTkLabel(form_frame, text="Entrepôt :").grid(row=3, column=0, sticky="w", pady=5, padx=15)
        self.entrepots = self.db.get_all_entrepots()
        self.entrepot_names = [e[1] for e in self.entrepots]
        self.entrepot_id_map = {e[1]: e[0] for e in self.entrepots}
        self.entrepot_var = ctk.StringVar()
        self.option_entrepot = ctk.CTkOptionMenu(form_frame, variable=self.entrepot_var, values=self.entrepot_names, width=300)
        self.option_entrepot.grid(row=3, column=1, sticky="ew", pady=5, padx=(0, 15))
        if self.entrepot_names:
            self.entrepot_var.set(self.entrepot_names[0])

        # Frame pour Unités & Prix avec fond légèrement différent
        unite_frame_bg = ctk.CTkFrame(
            form_frame, 
            fg_color="#f0f3f6",  # Fond légèrement différent
            corner_radius=8
        )
        unite_frame_bg.grid(row=5, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        
        # Placer la section Unités & Prix dans le nouveau frame
        self.setup_unite_prix_section(unite_frame_bg)
        self.unites_frame.grid_configure(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Ligne 5 : Boutons
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.grid(row=6, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)

        self.btn_action_article = ctk.CTkButton(
            buttons_frame,
            text="➕ Ajouter Article",
            command=self.ajouter_article,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        self.btn_action_article.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_annuler = ctk.CTkButton(
            buttons_frame,
            text="❌ Annuler",
            command=self.annuler_modification,
            fg_color="#757575",
            hover_color="#424242"
        )
        self.btn_annuler.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_supprimer = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Supprimer",
            command=self.supprimer_article,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.btn_supprimer.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        self.btn_supprimer.configure(state="disabled")

    def setup_unite_prix_section(self, parent):
        # Frame principale pour Unités & Prix avec style
        self.unites_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.unites_frame.pack(fill="x", padx=0, pady=0)

        # Titre de la section
        ctk.CTkLabel(
            self.unites_frame, 
            text="Unités & Prix:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="top", padx=(0, 10), pady=(0, 5))

        # Frame pour le conteneur scrollable avec une hauteur fixe
        scroll_frame = ctk.CTkFrame(self.unites_frame, fg_color="#ffffff")
        scroll_frame.pack(fill="x", padx=5, pady=5)

        # Canvas pour le scroll
        self.canvas = ctk.CTkCanvas(
            scroll_frame,
            height=150,  # Hauteur fixe
            bg="#ffffff",
            highlightthickness=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        # Configurer le canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Frame interne pour les unités
        self.frame_unites = ctk.CTkFrame(self.canvas, fg_color="#ffffff")
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.frame_unites,
            anchor="nw",
            width=self.canvas.winfo_reqwidth()
        )

        # Bind events for scrolling
        self.frame_unites.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.frame_unites.bind('<Enter>', lambda e: self._bind_mouse_wheel())
        self.frame_unites.bind('<Leave>', lambda e: self._unbind_mouse_wheel())

        # Ajouter après la configuration du frame_unites:
        self.unite_widgets = {}  # Pour stocker les références aux widgets des unités
        
        # Récupérer toutes les unités disponibles
        unites = self.get_unites()
        
        # Créer une ligne pour chaque unité
        for unite_id, unite_libelle in unites:
            # Frame pour chaque ligne d'unité
            unite_row = ctk.CTkFrame(self.frame_unites, fg_color="transparent")
            unite_row.pack(fill="x", padx=5, pady=2)
            
            # Checkbox pour sélectionner l'unité
            unite_var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                unite_row, 
                text=unite_libelle,
                variable=unite_var,
                command=lambda v=unite_var, id=unite_id: self.toggle_unite_prix(v, id)
            )
            checkbox.pack(side="left", padx=5)
            
            # Entry pour le prix avec style amélioré
            prix_entry = ctk.CTkEntry(
                unite_row,
                width=150,  # Augmentation de la largeur
                height=32,  # Hauteur définie pour meilleure visibilité
                placeholder_text="Prix en Ar...",  # Placeholder plus descriptif
                font=ctk.CTkFont(size=13),  # Police légèrement plus grande
                border_width=1,  # Bordure fine
                corner_radius=8,  # Coins arrondis
                state="disabled"
            )
            prix_entry.pack(side="right", padx=10)  # Augmentation du padding

            # Ajouter un label "Ar" après le champ prix
            prix_label = ctk.CTkLabel(
                unite_row,
                text="Ar",
                font=ctk.CTkFont(size=13),
                text_color="#666666"
            )
            prix_label.pack(side="right", padx=(0, 5))
            
            # Stocker les références aux widgets
            self.unite_widgets[unite_id] = {
                'row': unite_row,
                'checkbox': unite_var,
                'prix_entry': prix_entry,
                'libelle': unite_libelle
            }

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame to match"""
        min_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=min_width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mouse_wheel(self):
        """Bind mouse wheel events when mouse enters the frame"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse_wheel(self):
        """Unbind mouse wheel events when mouse leaves the frame"""
        self.canvas.unbind_all("<MouseWheel>")

    def filtrer_unites(self, event=None):
        # Récupérer le texte de recherche
        recherche = self.recherche_unite.get().lower()
        
        # Masquer/afficher les unités selon la recherche
        for unite_id, unite_info in self.unite_widgets.items():
            if recherche in unite_info['libelle'].lower():
                unite_info['row'].pack(fill="x", padx=0, pady=2)
            else:
                unite_info['row'].pack_forget()

    def toggle_unite_prix(self, unite_var, unite_id):
        # Trouver l'entrée de prix correspondante
        unite_info = self.unite_widgets.get(unite_id)
        if unite_info:
            prix_entry = unite_info['prix_entry']
            if unite_var.get():
                prix_entry.configure(state="normal")
            else:
                prix_entry.delete(0, "end")
                prix_entry.configure(state="disabled")

    def get_unites(self):
        try:
            unites = self.db.get_all_unites()
            return [(unite[0], unite[1]) for unite in unites]
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des unités: {e}")
            return []

    def load_articles(self):
        try:
            # Vider le tableau
            for item in self.tree_articles.get_children():
                self.tree_articles.delete(item)

            # Récupérer tous les articles
            articles = self.db.get_all_articles()
            
            # Trier les articles par nom
            articles_tries = sorted(articles, key=lambda x: x[1])

            # Parcourir les articles triés
            for article in articles_tries:
                # Récupérer les unités et prix pour cet article
                unites_prix = self.db.get_unites_by_article(article[0])
                
                # Formater les unités et prix de manière plus lisible
                unites_prix_details = []
                for unite in unites_prix:
                    unites_prix_details.append(f"{unite[2]} : {unite[3]} Ar")
                
                # Formater la chaîne des unités et prix
                unites_prix_str = " | ".join(unites_prix_details) if unites_prix_details else "Aucune unité"
                
                # Insérer l'article avec ses unités et prix
                self.tree_articles.insert("", "end", values=(
                    article[0],      # ID
                    article[1],      # Nom
                    article[2],      # Référence
                    unites_prix_str  # Unités et Prix
                ), tags=('odd' if len(self.tree_articles.get_children()) % 2 == 0 else 'even',))
            
            # Configurer des tags pour l'alternance des couleurs de lignes
            self.tree_articles.tag_configure('odd', background='#f0f0f0')
            self.tree_articles.tag_configure('even', background='#ffffff')

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des articles: {e}")

    def ajouter_article(self):
        try:
            nom = self.entry_nom.get().strip()
            reference = self.entry_reference.get().strip()
            entrepot_nom = self.entrepot_var.get()
            entrepot_id = self.entrepot_id_map.get(entrepot_nom)

            if not nom or not reference:
                messagebox.showwarning("Attention", "Veuillez saisir le nom et la référence de l'article.")
                return

            # Vérifier qu'au moins une unité est sélectionnée avec un prix
            unites_selectionnees = []
            for unite_id, unite_info in self.unite_widgets.items():
                if unite_info['checkbox'].get():  # Si la case est cochée
                    prix = unite_info['prix_entry'].get().strip()
                    if not prix:  # Vérifier que le prix est fourni
                        messagebox.showwarning("Attention", f"Veuillez saisir le prix pour l'unité {unite_info['libelle']}.")
                        return
                    try:
                        prix_float = float(prix)  # Convertir en float
                        if prix_float <= 0:
                            messagebox.showwarning("Attention", f"Le prix pour l'unité {unite_info['libelle']} doit être positif.")
                            return
                        unites_selectionnees.append((unite_id, unite_info['libelle'], prix_float))
                    except ValueError:
                        messagebox.showerror("Erreur", f"Prix invalide pour l'unité {unite_info['libelle']}. Veuillez saisir un nombre valide.")
                        return

            if not unites_selectionnees:
                messagebox.showwarning("Attention", "Veuillez sélectionner au moins une unité avec un prix.")
                return

            # Ajouter l'article
            article_id = self.db.create_article(nom, reference, entrepot_id)

            # Ajouter les prix pour les unités sélectionnées
            for unite_id, unite_label, prix in unites_selectionnees:
                self.db.add_prix_article(article_id, unite_id, prix)

            self.load_articles()  # Rafraîchir la liste des articles
            self.annuler_modification()
            messagebox.showinfo("Succès", f"Article '{nom}' ajouté avec succès avec {len(unites_selectionnees)} unité(s)!")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout de l'article: {e}")

    def annuler_modification(self):
        # Réinitialiser le formulaire
        self.entry_nom.delete(0, "end")
        self.entry_reference.delete(0, "end")
        
        # Réinitialiser les unités et prix
        for unite_id, unite_info in self.unite_widgets.items():
            unite_info['checkbox'].set(False)
            unite_info['prix_entry'].delete(0, "end")
            unite_info['prix_entry'].configure(state="disabled")
        
        # Réinitialiser l'ID de l'article sélectionné
        self.selected_article_id = None

        # Réinitialiser le titre et le bouton
        self.form_title.configure(text="➕ Nouvel Article")
        self.btn_action_article.configure(
            text="➕ Ajouter Article", 
            command=self.ajouter_article,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        
        # Désactiver le bouton Supprimer
        self.btn_supprimer.configure(state="disabled")

    def load_article_unites_prices(self, article_id):
        # Réinitialiser toutes les unités
        for unite_id, unite_info in self.unite_widgets.items():
            unite_info['checkbox'].set(False)
            unite_info['prix_entry'].delete(0, "end")
            unite_info['prix_entry'].configure(state="disabled")

        # Charger les prix existants
        try:
            # Récupérer tous les prix pour cet article avec les détails des unités
            prix_list = self.db.get_prix_by_article(article_id)
            
            # Récupérer les unités disponibles
            unites_disponibles = self.get_unites()
            
            # Vérifier si des prix existent pour cet article
            if not prix_list:
                messagebox.showwarning("Information", "Aucune unité trouvée pour cet article.")
                return

            # Parcourir tous les prix
            for prix in prix_list:
                # Structure de prix: (prix_id, article_id, unite_id, prix_unitaire, unite_code, unite_libelle)
                prix_id = prix[0]
                prix_unite_id = prix[2]
                prix_unitaire = prix[3]
                unite_code = prix[4]
                unite_libelle = prix[5]
                
                # Trouver la correspondance dans les widgets d'unités
                for widget_unite_id, unite_info in self.unite_widgets.items():
                    # Conversion explicite en entier pour éviter les problèmes de type
                    if int(widget_unite_id) == int(prix_unite_id):
                        # Cocher la case de l'unité
                        unite_info['checkbox'].set(True)
                        
                        # Activer et remplir le champ de prix
                        unite_info['prix_entry'].configure(state="normal")
                        unite_info['prix_entry'].delete(0, "end")
                        unite_info['prix_entry'].insert(0, str(prix_unitaire))
                        
                        # Appeler toggle_unite_prix pour s'assurer que l'état est correct
                        self.toggle_unite_prix(unite_info['checkbox'], int(widget_unite_id))
                        break

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des prix: {e}")
            import traceback
            traceback.print_exc()


    def modifier_article(self):
        # Vérifier qu'un article est sélectionné dans le tableau
        selection = self.tree_articles.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un article à modifier.")
            return

        # Récupérer les informations de l'article sélectionné
        item = self.tree_articles.item(selection[0])
        values = item['values']
        article_id = values[0]

        # Réinitialiser le formulaire
        self.annuler_modification()

        # Charger les informations de l'article
        self.selected_article_id = article_id
        self.entry_nom.insert(0, values[1])
        self.entry_reference.insert(0, values[2])

        # Charger l'entrepôt de l'article
        article = self.db.get_all_articles()
        entrepot_id = None
        for a in article:
            if str(a[0]) == str(article_id):
                entrepot_id = a[5] if len(a) > 5 else None
                break
        if entrepot_id:
            entrepot = self.db.get_entrepot_by_id(entrepot_id)
            if entrepot:
                self.entrepot_var.set(entrepot[1])

        # Charger les unités et prix de l'article
        self.load_article_unites_prices(article_id)

        # Changer le titre du formulaire
        self.form_title.configure(text="✏️ Modifier Article")
        self.btn_action_article.configure(
            text="✔️ Mettre à jour", 
            command=self.update_article,
            fg_color="#1976d2",
            hover_color="#1565c0"
        )
        
        # Activer le bouton Supprimer
        self.btn_supprimer.configure(state="normal")

    def update_article(self):
        try:
            # Vérifier que l'article est sélectionné
            if not self.selected_article_id:
                messagebox.showwarning("Attention", "Aucun article sélectionné pour modification.")
                return

            nom = self.entry_nom.get().strip()
            reference = self.entry_reference.get().strip()
            entrepot_nom = self.entrepot_var.get()
            entrepot_id = self.entrepot_id_map.get(entrepot_nom)

            if not nom or not reference:
                messagebox.showwarning("Attention", "Veuillez saisir le nom et la référence de l'article.")
                return

            # Mettre à jour les informations de base de l'article
            self.db.update_article(self.selected_article_id, nom, reference, entrepot_id)

            # Supprimer TOUS les anciens prix de cet article
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prix_article WHERE article_id = ?", (self.selected_article_id,))
            conn.commit()
            conn.close()

            # Ajouter les nouveaux prix
            unites_selectionnees = []
            for unite_id, unite_info in self.unite_widgets.items():
                if unite_info['checkbox'].get():  # Si la case est cochée
                    prix = unite_info['prix_entry'].get().strip()
                    if not prix:
                        messagebox.showwarning("Attention", f"Veuillez saisir le prix pour l'unité {unite_info['libelle']}.")
                        return
                    try:
                        prix_float = float(prix)
                        if prix_float <= 0:
                            messagebox.showwarning("Attention", f"Le prix pour l'unité {unite_info['libelle']} doit être positif.")
                            return
                        unites_selectionnees.append((unite_id, unite_info['libelle'], prix_float))
                    except ValueError:
                        messagebox.showerror("Erreur", f"Prix invalide pour l'unité {unite_info['libelle']}. Veuillez saisir un nombre valide.")
                        return

            if not unites_selectionnees:
                messagebox.showwarning("Attention", "Veuillez sélectionner au moins une unité avec un prix.")
                return

            # Ajouter les nouveaux prix
            for unite_id, unite_label, prix in unites_selectionnees:
                self.db.create_prix(self.selected_article_id, unite_id, prix)

            self.load_articles()  # Rafraîchir la liste des articles
            self.annuler_modification()
            messagebox.showinfo("Succès", f"Article '{nom}' mis à jour avec succès avec {len(unites_selectionnees)} unité(s)!")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour de l'article: {e}")
            import traceback
            traceback.print_exc()


    def supprimer_article(self):
        # Vérifier qu'un article est sélectionné dans le tableau
        selection = self.tree_articles.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un article à désactiver.")
            return

        # Récupérer les informations de l'article sélectionné
        item = self.tree_articles.item(selection[0])
        values = item['values']
        article_id = values[0]
        nom_article = values[1]
        reference_article = values[2]

        # Préparer le message de confirmation
        message_confirmation = (
            f"Voulez-vous vraiment désactiver l'article ?\n\n"
            f"Détails :\n"
            f"- Nom : {nom_article}\n"
            f"- Référence : {reference_article}\n\n"
            "⚠️ ATTENTION : L'article sera masqué de la liste des articles actifs.\n"
            "Les factures historiques resteront intactes."
        )

        # Boîte de dialogue de confirmation
        confirm = messagebox.askyesno(
            "Confirmation de désactivation", 
            message_confirmation
        )

        if confirm:
            # Tenter de désactiver l'article
            resultat = self.db.delete_article(article_id)
            
            if resultat:
                # Rafraîchir la liste des articles
                self.load_articles()
                
                # Réinitialiser le formulaire
                self.annuler_modification()
                
                # Message de succès
                messagebox.showinfo(
                    "Désactivation réussie", 
                    f"L'article '{nom_article}' a été désactivé avec succès."
                )
            else:
                # Message d'erreur plus détaillé
                messagebox.showerror(
                    "Erreur de désactivation", 
                    f"La désactivation de l'article '{nom_article}' a échoué.\n\n"
                    "Causes possibles :\n"
                    "- L'article n'existe plus\n"
                    "- Problème de connexion à la base de données\n"
                    "- Erreur système\n\n"
                    "Veuillez réessayer ou contacter le support technique."
                )

    def on_article_double_click(self, event):
        selection = self.tree_articles.selection()
        if selection:
            item = self.tree_articles.item(selection[0])
            values = item['values']
            article_id = values[0]

            # Réinitialiser le formulaire
            self.annuler_modification()

            # Charger les informations de l'article
            self.selected_article_id = article_id
            self.entry_nom.insert(0, values[1])
            self.entry_reference.insert(0, values[2])

            # Charger l'entrepôt de l'article
            article = self.db.get_all_articles()
            entrepot_id = None
            for a in article:
                if str(a[0]) == str(article_id):
                    entrepot_id = a[5] if len(a) > 5 else None
                    break
            if entrepot_id:
                entrepot = self.db.get_entrepot_by_id(entrepot_id)
                if entrepot:
                    self.entrepot_var.set(entrepot[1])

            # Charger les unités et prix de l'article
            self.load_article_unites_prices(article_id)

            # Changer le titre et le bouton
            self.form_title.configure(text="✏️ Modifier Article")
            self.btn_action_article.configure(
                text="✔️ Mettre à jour", 
                command=self.update_article,
                fg_color="#1976d2",
                hover_color="#1565c0"
            )
            
            # Activer le bouton Supprimer
            self.btn_supprimer.configure(state="normal")

    def open_trash_page(self):
        trash_window = ctk.CTkToplevel(self)
        trash_window.title("Corbeille des Articles")
        trash_window.geometry("800x600")
        
        trash_page = ArticleTrashPage(trash_window, self.db, self.load_articles)
        trash_page.pack(fill="both", expand=True)
        
        trash_window.transient(self.winfo_toplevel())
        trash_window.grab_set()