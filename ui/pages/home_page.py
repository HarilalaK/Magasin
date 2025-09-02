import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database.db_manager import DatabaseManager
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
import tempfile
import os
import subprocess
import platform
import tkinter as tk

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = DatabaseManager()
        self.panier = []  # Liste pour stocker les articles du panier
        self.setup_ui()

    def setup_ui(self):
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        title = ctk.CTkLabel(
            self, 
            text="🏠 Gestion des Ventes", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame principal avec deux colonnes
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Colonne gauche - Formulaire de vente
        self.setup_vente_form(main_frame)

        # Colonne droite - Panier
        self.setup_panier(main_frame)

    def setup_vente_form(self, parent):
        # Frame pour le formulaire
        form_frame = ctk.CTkFrame(parent)
        form_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Titre du formulaire
        form_title = ctk.CTkLabel(
            form_frame, 
            text="📝 Nouvelle Vente", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Nom client
        ctk.CTkLabel(form_frame, text="Nom Client:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_client = ctk.CTkEntry(form_frame, placeholder_text="Nom du client")
        self.entry_client.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Date facture
        ctk.CTkLabel(form_frame, text="Date:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_date = ctk.CTkEntry(form_frame)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # Séparateur
        separator = ctk.CTkFrame(form_frame, height=2, fg_color="#3a3a3a")
        separator.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Article avec recherche automatique
        ctk.CTkLabel(form_frame, text="Article:").grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        # Frame pour l'entrée et les suggestions
        article_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        article_frame.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        article_frame.grid_columnconfigure(0, weight=1)

        # Entrée pour l'article
        self.entry_article = ctk.CTkEntry(
            article_frame, 
            placeholder_text="Rechercher un article"
        )
        self.entry_article.grid(row=0, column=0, sticky="ew")
        
        # Lier les événements de frappe
        self.entry_article.bind('<KeyRelease>', self.filtrer_articles)

        # Liste de suggestions
        self.liste_suggestions = tk.Listbox(
            article_frame, 
            height=5, 
            width=0,  # Largeur dynamique
            font=('Arial', 11),
            bg='white',
            fg='black',
            selectbackground='#3498db',
            selectforeground='white',
            activestyle='none',
            borderwidth=1,
            relief='flat',
            highlightthickness=0
        )
        self.liste_suggestions.grid(row=1, column=0, sticky="ew", padx=0, pady=(2,0))
        self.liste_suggestions.bind('<<ListboxSelect>>', self.selectionner_article)

        # Initialiser la liste complète des articles
        self.tous_articles = self.get_articles()
        self.liste_suggestions.grid_remove()  # Cacher initialement

        # Unité
        ctk.CTkLabel(form_frame, text="Unité:").grid(row=5, column=0, padx=20, pady=10, sticky="w")
        self.combo_unite = ctk.CTkComboBox(
            form_frame, 
            values=["Sélectionnez d'abord un article"],
            command=self.on_unite_change
        )
        self.combo_unite.grid(row=5, column=1, padx=20, pady=10, sticky="ew")

        # Prix unitaire (affiché automatiquement)
        ctk.CTkLabel(form_frame, text="Prix Unitaire:").grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.label_prix = ctk.CTkLabel(form_frame, text="0 Ar", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_prix.grid(row=6, column=1, padx=20, pady=10, sticky="w")

        # Quantité
        ctk.CTkLabel(form_frame, text="Quantité:").grid(row=7, column=0, padx=20, pady=10, sticky="w")
        self.entry_quantite = ctk.CTkEntry(form_frame, placeholder_text="Quantité")
        self.entry_quantite.grid(row=7, column=1, padx=20, pady=10, sticky="ew")

        # Bouton ajouter au panier
        self.btn_ajouter = ctk.CTkButton(
            form_frame, 
            text="➕ Ajouter au Panier",
            command=self.ajouter_au_panier,
            height=40
        )
        self.btn_ajouter.grid(row=8, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def filtrer_articles(self, event):
        """Filtre et affiche les articles correspondant à la recherche"""
        # Vider la liste précédente
        self.liste_suggestions.delete(0, tk.END)
        
        recherche = self.entry_article.get().lower()
        
        # Filtrer les articles
        resultats = [
            article for article in self.tous_articles 
            if recherche.lower() in article.lower()
        ]
        
        # Afficher ou masquer la liste de suggestions
        if recherche and resultats:
            for article in resultats[:5]:  # Limiter à 5 suggestions
                self.liste_suggestions.insert(tk.END, article)
            
            # Ajuster la hauteur dynamiquement
            hauteur = min(len(resultats), 5)
            self.liste_suggestions.config(height=hauteur)
            
            # Personnaliser l'apparence
            self.liste_suggestions.config(
                bg='#f0f0f0', 
                selectbackground='#3498db',
                selectforeground='white'
            )
            
            # Afficher la liste de suggestions
            self.liste_suggestions.grid()
        else:
            # Masquer la liste de suggestions
            self.liste_suggestions.grid_remove()

    def selectionner_article(self, event):
        """Gère la sélection d'un article dans la liste de suggestions"""
        # Vérifier s'il y a une sélection
        if not self.liste_suggestions.curselection():
            return
        
        # Récupérer l'article sélectionné
        selection = self.liste_suggestions.get(self.liste_suggestions.curselection())
        
        # Mettre à jour l'entrée
        self.entry_article.delete(0, tk.END)
        self.entry_article.insert(0, selection)
        
        # Masquer la liste de suggestions
        self.liste_suggestions.grid_remove()
        
        # Appeler la méthode de changement d'article
        self.on_article_change(selection)

    def setup_panier(self, parent):
        # Frame pour le panier
        panier_frame = ctk.CTkFrame(parent)
        panier_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        panier_frame.grid_columnconfigure(0, weight=1)
        panier_frame.grid_rowconfigure(1, weight=1)

        # Titre du panier
        panier_title = ctk.CTkLabel(
            panier_frame, 
            text="🛒 Panier", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        panier_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Tableau du panier
        self.setup_panier_table(panier_frame)

        # Total
        self.label_total = ctk.CTkLabel(
            panier_frame, 
            text="Total: 0 Ar", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_total.grid(row=2, column=0, padx=20, pady=10, sticky="e")

        # Boutons d'action
        actions_frame = ctk.CTkFrame(panier_frame, fg_color="transparent")
        actions_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        self.btn_vider = ctk.CTkButton(
            actions_frame, 
            text="🗑️ Vider Panier",
            command=self.vider_panier,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.btn_vider.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_enregistrer = ctk.CTkButton(
            actions_frame, 
            text="💾 Enregistrer Vente",
            command=self.enregistrer_vente,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        self.btn_enregistrer.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        # Case à cocher pour imprimer la facture
        self.imprimer_var = ctk.BooleanVar()
        self.checkbox_imprimer = ctk.CTkCheckBox(
            actions_frame,
            text="Imprimer la facture (PDF)",
            variable=self.imprimer_var
        )
        self.checkbox_imprimer.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="w")

    def setup_panier_table(self, parent):
        # Frame pour le tableau
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Treeview pour le panier
        columns = ("Article", "Unité", "Quantité", "Prix U.", "Total", "Action")
        self.tree_panier = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        # Configuration des colonnes
        for col in columns:
            self.tree_panier.heading(col, text=col)
            if col == "Action":
                self.tree_panier.column(col, width=60, anchor="center")
            elif col in ["Quantité", "Prix U.", "Total"]:
                self.tree_panier.column(col, width=80, anchor="center")
            else:
                self.tree_panier.column(col, width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_panier.yview)
        self.tree_panier.configure(yscrollcommand=scrollbar.set)

        # Placement
        self.tree_panier.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind double-click pour supprimer
        self.tree_panier.bind("<Double-1>", self.supprimer_du_panier)

    def get_articles(self):
        """Récupère la liste des articles"""
        try:
            articles = self.db.get_all_articles()
            return [f"{article[0]} - {article[1]}" for article in articles]
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des articles: {e}")
            return []

    def on_article_change(self, choice):
        """Callback quand l'article change"""
        if choice and choice != "":
            article_id = choice.split(" - ")[0]
            unites = self.get_unites_by_article(article_id)
            self.combo_unite.configure(values=unites)
            self.combo_unite.set("")
            self.label_prix.configure(text="0 Ar")

    def get_unites_by_article(self, article_id):
        """Récupère les unités disponibles pour un article"""
        try:
            unites = self.db.get_unites_by_article(article_id)
            return [f"{unite[0]} - {unite[1]}" for unite in unites]
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des unités: {e}")
            return []

    def on_unite_change(self, choice):
        """Callback quand l'unité change"""
        if choice and choice != "" and self.entry_article.get():
            article_id = self.entry_article.get().split(" - ")[0]
            unite_id = choice.split(" - ")[0]
            prix = self.get_prix_article_unite(article_id, unite_id)
            self.label_prix.configure(text=f"{prix:,.0f} Ar")

    def get_prix_article_unite(self, article_id, unite_id):
        """Récupère le prix pour un article et une unité"""
        try:
            prix = self.db.get_prix_article_unite(article_id, unite_id)
            return prix if prix else 0
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du prix: {e}")
            return 0

    def ajouter_au_panier(self):
        """Ajoute un article au panier"""
        try:
            # Validation des champs
            if not self.entry_article.get():
                messagebox.showwarning("Attention", "Veuillez sélectionner un article")
                return
            
            if not self.combo_unite.get():
                messagebox.showwarning("Attention", "Veuillez sélectionner une unité")
                return
            
            if not self.entry_quantite.get():
                messagebox.showwarning("Attention", "Veuillez saisir la quantité")
                return
            
            # Récupération des données
            article_info = self.entry_article.get().split(" - ")
            unite_info = self.combo_unite.get().split(" - ")
            quantite = float(self.entry_quantite.get())
            prix_unitaire = float(self.label_prix.cget("text").replace(" Ar", "").replace(",", ""))
            
            # Calcul du total
            prix_total = quantite * prix_unitaire
            
            # Ajout au panier
            item = {
                "article_id": article_info[0],
                "article_nom": article_info[1],
                "unite_id": unite_info[0],
                "unite_nom": unite_info[1],
                "quantite": quantite,
                "prix_unitaire": prix_unitaire,
                "prix_total": prix_total
            }
            
            self.panier.append(item)
            self.refresh_panier()
            
            # Reset des champs
            self.entry_quantite.delete(0, "end")
            
            
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir une quantité valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {e}")

    def refresh_panier(self):
        """Rafraîchit l'affichage du panier"""
        # Vider le tableau
        for item in self.tree_panier.get_children():
            self.tree_panier.delete(item)
        
        # Ajouter les items
        total_general = 0
        for i, item in enumerate(self.panier):
            self.tree_panier.insert("", "end", values=(
                item["article_nom"],
                item["unite_nom"],
                f"{item['quantite']:.2f}",
                f"{item['prix_unitaire']:,.0f} Ar",
                f"{item['prix_total']:,.0f} Ar",
                "❌"
            ))
            total_general += item["prix_total"]
        
        # Mettre à jour le total
        self.label_total.configure(text=f"Total: {total_general:,.0f} Ar")

    def supprimer_du_panier(self, event):
        """Supprime un item du panier"""
        selection = self.tree_panier.selection()
        if selection:
            item = self.tree_panier.item(selection[0])
            index = self.tree_panier.index(selection[0])
            
            if messagebox.askyesno("Confirmation", f"Supprimer {item['values'][0]} du panier ?"):
                self.panier.pop(index)
                self.refresh_panier()

    def vider_panier(self):
        """Vide complètement le panier"""
        if self.panier and messagebox.askyesno("Confirmation", "Vider complètement le panier ?"):
            self.panier.clear()
            self.refresh_panier()

    def enregistrer_vente(self):
        """Enregistre la vente dans la base de données"""
        try:
            # Validation
            if not self.entry_client.get():
                messagebox.showwarning("Attention", "Veuillez saisir le nom du client")
                return
            
            if not self.panier:
                messagebox.showwarning("Attention", "Le panier est vide")
                return
            
            # Calcul du total
            total = sum(item["prix_total"] for item in self.panier)
            
            # Enregistrement de la facture
            facture_id = self.db.create_facture(
                self.entry_client.get(),
                self.entry_date.get(),
                total
            )
            
            # Enregistrement des détails
            for item in self.panier:
                self.db.add_facture_detail(
                    facture_id,
                    item["article_id"],
                    item["unite_id"],
                    item["quantite"],
                    item["prix_unitaire"],
                    item["prix_total"]
                )
            
            messagebox.showinfo("Succès", f"Vente enregistrée avec succès !\nFacture N°{facture_id}")
            
            # Imprimer la facture si l'utilisateur le souhaite
            if self.imprimer_var.get():
                self.generer_pdf_facture(facture_id)

            # Reset du formulaire
            self.reset_formulaire()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {e}")

    def generer_pdf_facture(self, facture_id):
        """Génère et ouvre une facture PDF professionnelle"""
        try:
            # Récupérer les détails de la facture
            details = self.db.get_facture_details(facture_id)
            facture_info = self.db.get_facture_by_id(facture_id)
            
            if not details or not facture_info:
                messagebox.showerror("Erreur", "Données de facture introuvables.")
                return
            
            # Créer le fichier PDF temporaire
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"Facture_{facture_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            # Créer le document PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                                  rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=72)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=1,  # Centré
                textColor=colors.darkblue
            )
            
            normal_style = styles['Normal']
            
            # Contenu du PDF
            story = []
            
            # Titre
            story.append(Paragraph(f"<b>FACTURE N° {facture_id}</b>", title_style))
            story.append(Spacer(1, 20))
            
            # Informations client et date
            client_info = f"""
            <b>Client:</b> {facture_info[1]}<br/>
            <b>Date:</b> {facture_info[2]}<br/>
            <b>Date d'impression:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """
            story.append(Paragraph(client_info, normal_style))
            story.append(Spacer(1, 20))
            
            # Tableau des articles
            table_data = [['Article', 'Unité', 'Quantité', 'Prix Unitaire', 'Total', 'Entrepôt']]
            
            total_facture = 0
            for detail in details:
                article_nom = detail[7]
                unite_libelle = detail[8]
                quantite = detail[4]
                prix_unitaire = detail[5]
                prix_total = detail[6]
                entrepot_nom = detail[9] or "Non spécifié"
                total_facture += prix_total
                
                table_data.append([
                    article_nom,
                    unite_libelle,
                    f"{quantite:.2f}",
                    f"{prix_unitaire:,.0f} Ar",
                    f"{prix_total:,.0f} Ar",
                    entrepot_nom
                ])
            
            # Ajouter ligne de total
            table_data.append(['', '', '', '', 'TOTAL A PAYER : ', f'{total_facture:,.0f} Ar'])
            
            # Créer le tableau
            table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1.25*inch, 1.25*inch, 1.5*inch])
            table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                
                # Corps du tableau
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 10),
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                
                # Ligne de total
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('ALIGN', (4, -1), (-1, -1), 'RIGHT'),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Pied de page
            footer_text = """
            <b><center>"Ho tahiana ianao raha miditra, Ho tahiana ianao raha mivoaka"</center></b><br/><br/>
            
            """
            story.append(Paragraph(footer_text, normal_style))
            
            # Construire le PDF
            doc.build(story)
            
            # Ouvrir le fichier PDF
            self.ouvrir_pdf(pdf_path)
            
            messagebox.showinfo("Succès", f"Facture PDF générée avec succès !\nFichier: {os.path.basename(pdf_path)}")
            
        except ImportError:
            messagebox.showerror("Erreur", "La bibliothèque ReportLab n'est pas installée.\nInstallez-la avec: pip install reportlab")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du PDF: {e}")

    def ouvrir_pdf(self, pdf_path):
        """Ouvre le fichier PDF selon le système d'exploitation"""
        try:
            if platform.system() == "Windows":
                os.startfile(pdf_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", pdf_path])
            else:  # Linux
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            messagebox.showwarning("Attention", f"Impossible d'ouvrir automatiquement le PDF.\nFichier sauvegardé: {pdf_path}")

    def reset_formulaire(self):
        """Réinitialise le formulaire"""
        self.entry_client.delete(0, "end")
        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_article.delete(0, "end")
        self.combo_unite.set("Sélectionnez d'abord un article")
        self.label_prix.configure(text="0 Ar")
        self.entry_quantite.delete(0, "end")
        self.panier.clear()
        self.refresh_panier()
        self.imprimer_var.set(False)  # Réinitialiser la case à cocher