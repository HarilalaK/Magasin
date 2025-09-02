import customtkinter as ctk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime
import os
import tempfile
import platform
import subprocess

class InventairePage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.setup_ui()
        self.load_articles()

    def setup_ui(self):
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        title = ctk.CTkLabel(
            self, 
            text="📦 Inventaire des Articles", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Bouton d'impression
        btn_imprimer = ctk.CTkButton(
            self,
            text="🖨️ Imprimer l'Inventaire",
            command=self.imprimer_inventaire,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        btn_imprimer.grid(row=0, column=0, padx=20, pady=20, sticky="e")

        # Frame pour le tableau
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Colonnes
        columns = ("ID", "Nom", "Référence", "Unités et Prix", "Entrepôt")
        self.tree_inventaire = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # Configuration des colonnes
        self.tree_inventaire.column("ID", width=50, anchor="center", stretch=False)
        self.tree_inventaire.column("Nom", width=150, anchor="w", stretch=True)
        self.tree_inventaire.column("Référence", width=100, anchor="center", stretch=False)
        self.tree_inventaire.column("Unités et Prix", width=250, anchor="w", stretch=True)
        self.tree_inventaire.column("Entrepôt", width=100, anchor="center", stretch=False)

        # Titres des colonnes
        for col in columns:
            self.tree_inventaire.heading(col, text=col, anchor="center")

        # Scrollbars
        scrollbar_vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_inventaire.yview)
        scrollbar_horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_inventaire.xview)
        
        self.tree_inventaire.configure(
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set
        )

        # Placement des scrollbars
        self.tree_inventaire.grid(row=0, column=0, sticky="nsew")
        scrollbar_vertical.grid(row=0, column=1, sticky="ns")
        scrollbar_horizontal.grid(row=1, column=0, sticky="ew")

    def load_articles(self):
        """Charge tous les articles avec leurs unités et prix"""
        try:
            # Vider le tableau
            for item in self.tree_inventaire.get_children():
                self.tree_inventaire.delete(item)

            # Récupérer tous les articles
            articles = self.db.get_all_articles()
            
            # Parcourir les articles
            for article in articles:
                # Récupérer les unités et prix pour cet article
                unites_prix = self.db.get_unites_by_article(article[0])
                
                # Formater les unités et prix de manière lisible
                unites_prix_details = []
                for unite in unites_prix:
                    unites_prix_details.append(f"{unite[2]} : {unite[3]} Ar")
                
                # Formater la chaîne des unités et prix
                unites_prix_str = " | ".join(unites_prix_details) if unites_prix_details else "Aucune unité"
                
                # Récupérer le nom de l'entrepôt
                entrepot_nom = "Non assigné"
                if article[5]:  # Si un entrepôt est assigné
                    entrepot = self.db.get_entrepot_by_id(article[5])
                    if entrepot:
                        entrepot_nom = entrepot[1]
                
                # Insérer l'article
                self.tree_inventaire.insert("", "end", values=(
                    article[0],      # ID
                    article[1],      # Nom
                    article[2],      # Référence
                    unites_prix_str, # Unités et Prix
                    entrepot_nom     # Entrepôt
                ))

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des articles: {e}")

    def imprimer_inventaire(self):
        """Génère un PDF de l'inventaire avec un style élégant"""
        try:
            # Créer le fichier PDF temporaire
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"Inventaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            # Créer le document PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                                  rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=72)
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Styles personnalisés
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=20,
                alignment=1  # Centré
            )
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#7f8c8d'),
                spaceAfter=20,
                alignment=1  # Centré
            )
            
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#2980b9'),
                spaceAfter=10
            )
            
            # Contenu du PDF
            story = []
            
            # Logo ou en-tête (si possible)
            story.append(Paragraph("<b>INVENTAIRE DES ARTICLES</b>", title_style))
            story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", subtitle_style))
            story.append(Spacer(1, 20))
            
            # Préparer les données du tableau
            table_data = [['ID', 'Nom', 'Entrepôt']]
            
            # Récupérer tous les articles
            articles = self.db.get_all_articles()
            
            for article in articles:
                # Récupérer le nom de l'entrepôt
                entrepot_nom = "Non assigné"
                if article[5]:  # Si un entrepôt est assigné
                    entrepot = self.db.get_entrepot_by_id(article[5])
                    if entrepot:
                        entrepot_nom = entrepot[1]
                
                # Ajouter à la liste des données
                table_data.append([
                    str(article[0]),
                    article[1],
                    entrepot_nom
                ])
            
            # Créer le tableau
            table = Table(table_data, colWidths=[1*inch, 3*inch, 2*inch])
            table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                
                # Corps du tableau
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                
                # Alternance de couleurs
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Pied de page
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#95a5a6'),
                alignment=1  # Centré
            )
            story.append(Paragraph("Inventaire généré automatiquement", footer_style))
            
            # Construire le PDF
            doc.build(story)
            
            # Ouvrir le fichier PDF
            self.ouvrir_pdf(pdf_path)
            
            messagebox.showinfo("Succès", f"Inventaire PDF généré avec succès !\nFichier: {os.path.basename(pdf_path)}")
            
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
