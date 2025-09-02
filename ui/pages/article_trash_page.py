import customtkinter as ctk
from tkinter import ttk, messagebox, Menu
from database.db_manager import DatabaseManager

class ArticleTrashPage(ctk.CTkFrame):
    def __init__(self, parent, db, load_articles_callback=None):
        super().__init__(parent, corner_radius=0, fg_color="transparent")

        self.db = db
        self.load_articles_callback = load_articles_callback
        self.setup_ui()
        self.load_articles_inactifs()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self,
            text="🗑️ Corbeille des Articles",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame principale
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Titre de la liste
        list_title = ctk.CTkLabel(
            main_frame,
            text="📋 Articles Désactivés (Clic droit pour les actions)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.grid(row=0, column=0, sticky="w", padx=0, pady=(0, 10))

        # Setup de la table
        self.setup_articles_table(main_frame)

    def setup_articles_table(self, parent):
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Colonnes sans Actions
        columns = ("ID", "Nom", "Référence")
        self.tree_articles_inactifs = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

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

        # Configuration des colonnes
        self.tree_articles_inactifs.column("ID", width=50, anchor="center", stretch=False)
        self.tree_articles_inactifs.column("Nom", width=200, anchor="w", stretch=True)
        self.tree_articles_inactifs.column("Référence", width=150, anchor="center", stretch=False)

        # Titres des colonnes
        for col in columns:
            self.tree_articles_inactifs.heading(col, text=col, anchor="center")

        # Scrollbars
        scrollbar_vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_articles_inactifs.yview)
        scrollbar_horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_articles_inactifs.xview)
        
        self.tree_articles_inactifs.configure(
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set
        )

        # Placement des scrollbars et de la table
        self.tree_articles_inactifs.grid(row=0, column=0, sticky="nsew")
        scrollbar_vertical.grid(row=0, column=1, sticky="ns")
        scrollbar_horizontal.grid(row=1, column=0, sticky="ew")

        # Configuration du poids des lignes et colonnes
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Menu contextuel
        self.create_context_menu()
        
        # Bind pour le clic droit
        self.tree_articles_inactifs.bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="🔄 Restaurer l'article", 
            command=self.reactivate_selected_article
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="❌ Supprimer définitivement", 
            command=self.delete_selected_article_permanently
        )

    def show_context_menu(self, event):
        # Sélectionner l'item sous le curseur
        item = self.tree_articles_inactifs.identify_row(event.y)
        if item:
            self.tree_articles_inactifs.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def load_articles_inactifs(self):
        for item in self.tree_articles_inactifs.get_children():
            self.tree_articles_inactifs.delete(item)

        articles = self.db.get_all_articles_inactifs()
        
        for article in articles:
            # Insérer l'article dans le tableau
            item = self.tree_articles_inactifs.insert("", "end", values=(
                article[0],  # ID
                article[1],  # Nom
                article[2]   # Référence
            ), tags=('odd' if len(self.tree_articles_inactifs.get_children()) % 2 == 0 else 'even',))

        self.tree_articles_inactifs.tag_configure('odd', background='#f0f0f0')
        self.tree_articles_inactifs.tag_configure('even', background='#ffffff')

    def get_selected_article(self):
        selected_items = self.tree_articles_inactifs.selection()
        if not selected_items:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un article.")
            return None
        
        item = selected_items[0]
        values = self.tree_articles_inactifs.item(item, 'values')
        return {
            'id': values[0],
            'nom': values[1],
            'reference': values[2],
            'item': item
        }

    def reactivate_selected_article(self):
        article_data = self.get_selected_article()
        if not article_data:
            return
        
        self.reactivate_article(article_data['id'], article_data['nom'], article_data['item'])

    def delete_selected_article_permanently(self):
        article_data = self.get_selected_article()
        if not article_data:
            return
        
        self.delete_article_permanently(article_data['id'], article_data['nom'], article_data['item'])

    def reactivate_article(self, article_id, article_nom, item=None):
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmation de restauration", 
            f"Voulez-vous vraiment restaurer l'article '{article_nom}' ?"
        )
        
        if confirm:
            resultat = self.db.reactivate_article(article_id)
            
            if resultat:
                # Rafraîchir la liste des articles inactifs
                self.load_articles_inactifs()
                
                # Rafraîchir la liste des articles dans la page principale si le callback est défini
                if self.load_articles_callback:
                    self.load_articles_callback()
                
                messagebox.showinfo("Succès", f"L'article '{article_nom}' a été restauré avec succès.")
            else:
                messagebox.showerror("Erreur", f"La restauration de l'article '{article_nom}' a échoué.")

    def delete_article_permanently(self, article_id, article_nom, item=None):
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmation de suppression définitive", 
            f"⚠️ ATTENTION : Voulez-vous vraiment supprimer définitivement l'article '{article_nom}' ?\n\n"
            "Cette action est IRRÉVERSIBLE et supprimera toutes les références à cet article."
        )
        
        if confirm:
            resultat = self.db.delete_article_permanently(article_id)
            
            if resultat:
                # Rafraîchir la liste des articles inactifs
                self.load_articles_inactifs()
                
                # Rafraîchir la liste des articles dans la page principale si le callback est défini
                if self.load_articles_callback:
                    self.load_articles_callback()
                
                messagebox.showinfo("Succès", f"L'article '{article_nom}' a été supprimé définitivement.")
            else:
                messagebox.showerror("Erreur", f"La suppression définitive de l'article '{article_nom}' a échoué.")