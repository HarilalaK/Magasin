import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        self.db_path = 'database/vente.db'
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Assure que la base de données existe"""
        if not os.path.exists(self.db_path):
            from database.init_db import init_database
            init_database()
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    # =============== GESTION DES UNITÉS ===============
    
    def get_all_unites(self):
        """Récupère toutes les unités"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM unite ORDER BY libelle")
        unites = cursor.fetchall()
        conn.close()
        return unites
    
    def create_unite(self, code, libelle):
        """Crée une nouvelle unité"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO unite (code, libelle) VALUES (?, ?)", (code, libelle))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_unite(self, id, code, libelle):
        """Met à jour une unité"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE unite SET code = ?, libelle = ? WHERE id = ?", (code, libelle, id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_unite(self, id):
        """Supprime une unité"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM unite WHERE id = ?", (id,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    # =============== GESTION DES ARTICLES ===============
    
    def get_all_articles(self):
        """Récupère tous les articles actifs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM article WHERE actif = 1 ORDER BY nom")
        articles = cursor.fetchall()
        conn.close()
        return articles
    
    def create_article(self, nom, reference, entrepot_id=None):
        """Crée un nouveau article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO article (nom, reference, entrepot_id) VALUES (?, ?, ?)", (nom, reference, entrepot_id))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def update_article(self, id, nom, reference, entrepot_id=None):
        """Met à jour un article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE article SET nom = ?, reference = ?, entrepot_id = ? WHERE id = ?", (nom, reference, entrepot_id, id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_article(self, article_id):
        """Désactive un article au lieu de le supprimer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Vérifier si l'article existe
            cursor.execute("SELECT * FROM article WHERE id = ?", (article_id,))
            article = cursor.fetchone()
            if not article:
                print(f"Erreur : Article avec ID {article_id} non trouvé.")
                return False

            # Vérifier le statut actuel de l'article
            cursor.execute("SELECT actif FROM article WHERE id = ?", (article_id,))
            statut_actuel = cursor.fetchone()[0]
            print(f"Statut actuel de l'article : {statut_actuel}")

            # Mettre à jour le statut de l'article à inactif
            cursor.execute("UPDATE article SET actif = 0 WHERE id = ?", (article_id,))
            conn.commit()
            
            # Vérifier que la mise à jour a bien été effectuée
            cursor.execute("SELECT actif FROM article WHERE id = ?", (article_id,))
            nouveau_statut = cursor.fetchone()[0]
            print(f"Nouveau statut de l'article : {nouveau_statut}")
            
            return True
        except Exception as e:
            print(f"Erreur lors de la désactivation de l'article : {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()
    
    # =============== GESTION DES PRIX ===============
    
    def get_prix_by_article(self, article_id):
        """Récupère les prix d'un article avec les détails des unités"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pa.id, pa.article_id, pa.unite_id, pa.prix_unitaire, u.code, u.libelle 
            FROM prix_article pa
            JOIN unite u ON pa.unite_id = u.id
            WHERE pa.article_id = ?
            ORDER BY u.libelle
        """, (article_id,))
        prix = cursor.fetchall()
        conn.close()
        return prix
    
    def get_unites_by_article(self, article_id):
        """Récupère les unités disponibles pour un article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.code, u.libelle, pa.prix_unitaire
            FROM unite u
            JOIN prix_article pa ON u.id = pa.unite_id
            WHERE pa.article_id = ?
            ORDER BY u.libelle
        """, (article_id,))
        unites = cursor.fetchall()
        conn.close()
        return unites
    
    def get_prix_unitaire(self, article_id, unite_id):
        """Récupère le prix unitaire d'un article pour une unité donnée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT prix_unitaire 
            FROM prix_article 
            WHERE article_id = ? AND unite_id = ?
        """, (article_id, unite_id))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def create_prix(self, article_id, unite_id, prix_unitaire):
        """Crée un nouveau prix pour un article/unité"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO prix_article (article_id, unite_id, prix_unitaire) 
                VALUES (?, ?, ?)
            """, (article_id, unite_id, prix_unitaire))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_prix(self, article_id, unite_id, prix_unitaire):
        """Met à jour le prix d'un article/unité"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE prix_article 
                SET prix_unitaire = ? 
                WHERE article_id = ? AND unite_id = ?
            """, (prix_unitaire, article_id, unite_id))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def delete_prix(self, article_id, unite_id):
        """Supprime un prix"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM prix_article WHERE article_id = ? AND unite_id = ?", (article_id, unite_id))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    # =============== GESTION DES FACTURES ===============
    
    def create_facture(self, nom_client, date_facture, montant_total):
        """Crée une nouvelle facture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO facture (nom_client, date_facture, montant_total) 
                VALUES (?, ?, ?)
            """, (nom_client, date_facture, montant_total))
            conn.commit()
            return cursor.lastrowid
        except:
            return None
        finally:
            conn.close()
    
    def add_article_to_facture(self, facture_id, article_id, unite_id, quantite, prix_unitaire):
        """Ajoute un article à une facture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            prix_total = quantite * prix_unitaire
            cursor.execute("""
                INSERT INTO facture_detail (facture_id, article_id, unite_id, quantite, prix_unitaire, prix_total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (facture_id, article_id, unite_id, quantite, prix_unitaire, prix_total))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def get_facture_details(self, facture_id):
        """Récupère les détails d'une facture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fd.*, 
                   a.nom as article_nom, 
                   u.libelle as unite_libelle,
                   e.nom as entrepot_nom
            FROM facture_detail fd
            JOIN article a ON fd.article_id = a.id
            JOIN unite u ON fd.unite_id = u.id
            LEFT JOIN entrepot e ON a.entrepot_id = e.id
            WHERE fd.facture_id = ?
        """, (facture_id,))
        details = cursor.fetchall()
        conn.close()
        return details
    
    def get_all_factures(self):
        """Récupère toutes les factures"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM facture ORDER BY date_facture DESC")
        factures = cursor.fetchall()
        conn.close()
        return factures
    
    def get_facture_by_id(self, facture_id):
        """Récupère une facture par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM facture WHERE id = ?", (facture_id,))
        facture = cursor.fetchone()
        conn.close()
        return facture
    
    def get_prix_article_unite(self, article_id, unite_id):
        """Récupère le prix unitaire d'un article pour une unité donnée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT prix_unitaire 
            FROM prix_article 
            WHERE article_id = ? AND unite_id = ?
        """, (article_id, unite_id))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def add_unite(self, code, libelle):
        """Ajoute une nouvelle unité à la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO unite (code, libelle) VALUES (?, ?)", (code, libelle))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_all_articles_with_unite(self):
        """Récupère tous les articles avec leurs unités associées"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.nom, a.reference, a.unite_id, u.libelle
            FROM article a
            LEFT JOIN unite u ON a.unite_id = u.id
            ORDER BY a.nom
        """)
        articles = cursor.fetchall()
        conn.close()
        return articles
    
    def add_article(self, nom, reference):
        """Ajoute un nouvel article dans la base de données."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO article (nom, reference) VALUES (?, ?)", (nom, reference))
        conn.commit()
        article_id = cursor.lastrowid  # Récupérer l'ID de l'article inséré
        conn.close()
        return article_id

    def add_prix_article(self, article_id, unite_id, prix):
        """Ajoute un prix pour un article et une unité donnée."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prix_article (article_id, unite_id, prix_unitaire) VALUES (?, ?, ?)", (article_id, unite_id, prix))
        conn.commit()
        conn.close()


    def create_facture(self, nom_client, date_facture, montant_total):
        """Crée une nouvelle facture et retourne son ID."""
        conn = self.get_connection()  # Utiliser get_connection
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO facture (nom_client, date_facture, montant_total) VALUES (?, ?, ?)",
                        (nom_client, date_facture, montant_total))
            conn.commit()
            return cursor.lastrowid  # Retourne l'ID de la facture ajoutée
        except Exception as e:
            print(f"Erreur lors de la création de la facture: {e}")
            return None
        finally:
            conn.close()  # Fermer la connexion

    def add_facture_detail(self, facture_id, article_id, unite_id, quantite, prix_unitaire, prix_total):
        """Enregistre les détails d'une facture."""
        conn = self.get_connection()  # Utiliser get_connection
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO facture_detail (facture_id, article_id, unite_id, quantite, prix_unitaire, prix_total) VALUES (?, ?, ?, ?, ?, ?)",
                        (facture_id, article_id, unite_id, quantite, prix_unitaire, prix_total))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout des détails de la facture: {e}")
        finally:
            conn.close()  # Fermer la connexion

    def get_all_articles_inactifs(self):
        """Récupère tous les articles inactifs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM article WHERE actif = 0 ORDER BY nom")
        articles = cursor.fetchall()
        conn.close()
        return articles

    def reactivate_article(self, article_id):
        """Réactive un article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE article SET actif = 1 WHERE id = ?", (article_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la réactivation de l'article : {e}")
            return False
        finally:
            conn.close()

    def delete_article_permanently(self, article_id):
        """Supprime définitivement un article et ses références"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            conn.execute('BEGIN')
            
            cursor.execute("DELETE FROM prix_article WHERE article_id = ?", (article_id,))
            
            cursor.execute("DELETE FROM facture_detail WHERE article_id = ?", (article_id,))
            
            cursor.execute("DELETE FROM article WHERE id = ?", (article_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de la suppression définitive de l'article : {e}")
            return False
        finally:
            conn.close()

    # =============== GESTION DES ENTREPÔTS ===============
    def get_all_entrepots(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entrepot ORDER BY nom")
        entrepots = cursor.fetchall()
        conn.close()
        return entrepots

    def create_entrepot(self, nom, localisation):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO entrepot (nom, localisation) VALUES (?, ?)", (nom, localisation))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def update_entrepot(self, id, nom, localisation):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE entrepot SET nom = ?, localisation = ? WHERE id = ?", (nom, localisation, id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_entrepot(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM entrepot WHERE id = ?", (id,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def get_entrepot_by_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entrepot WHERE id = ?", (id,))
        entrepot = cursor.fetchone()
        conn.close()
        return entrepot

    def get_entrepot_stats(self, entrepot_id):
        """Récupère les statistiques détaillées pour un entrepôt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Nombre total d'articles dans l'entrepôt
        cursor.execute("""
            SELECT COUNT(*) as total_articles
            FROM article 
            WHERE entrepot_id = ? AND actif = 1
        """, (entrepot_id,))
        total_articles = cursor.fetchone()[0]
        
        # Nombre total d'articles actifs dans tous les entrepôts
        cursor.execute("""
            SELECT COUNT(*) as total_articles_actifs
            FROM article 
            WHERE actif = 1
        """)
        total_articles_actifs = cursor.fetchone()[0]
        
        # Pourcentage d'articles dans cet entrepôt
        pourcentage_articles = (total_articles / total_articles_actifs * 100) if total_articles_actifs > 0 else 0
        
        # Répartition des articles par catégorie
        cursor.execute("""
            SELECT 
                u.libelle as unite, 
                COUNT(DISTINCT a.id) as nb_articles,
                ROUND(COUNT(DISTINCT a.id) * 100.0 / (
                    SELECT COUNT(DISTINCT id) 
                    FROM article 
                    WHERE entrepot_id = ? AND actif = 1
                ), 2) as pourcentage
            FROM article a
            LEFT JOIN prix_article pa ON a.id = pa.article_id
            LEFT JOIN unite u ON pa.unite_id = u.id
            WHERE a.entrepot_id = ? AND a.actif = 1
            GROUP BY u.libelle
            ORDER BY nb_articles DESC
        """, (entrepot_id, entrepot_id))
        repartition_unites = cursor.fetchall()
        
        # Statistiques de vente
        cursor.execute("""
            SELECT 
                ROUND(SUM(fd.quantite), 2) as total_quantite_vendue,
                ROUND(SUM(fd.prix_total), 2) as total_ventes
            FROM facture_detail fd
            JOIN article a ON fd.article_id = a.id
            WHERE a.entrepot_id = ?
        """, (entrepot_id,))
        stats_ventes = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'pourcentage_articles': round(pourcentage_articles, 2),
            'repartition_unites': repartition_unites,
            'total_quantite_vendue': stats_ventes[0] or 0,
            'total_ventes': stats_ventes[1] or 0
        }