import sqlite3
import os

def init_database():
    """Initialise la base de données avec les tables nécessaires"""
    
    # Créer le dossier database s'il n'existe pas
    os.makedirs('database', exist_ok=True)
    
    # Connexion à la base de données
    conn = sqlite3.connect('database/vente.db')
    cursor = conn.cursor()
    
    # Table des unités de mesure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            libelle TEXT NOT NULL
        )
    ''')
    
    # Table des entrepôts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entrepot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            localisation TEXT
        )
    ''')
    
    # Table des articles (modifiée pour inclure entrepot_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS article (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            reference TEXT NOT NULL UNIQUE,
            unite_id INTEGER,
            actif INTEGER DEFAULT 1,
            entrepot_id INTEGER,
            FOREIGN KEY (unite_id) REFERENCES unite(id),
            FOREIGN KEY (entrepot_id) REFERENCES entrepot(id)
        )
    ''')
    
    # Table des prix par article et unité
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prix_article (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            unite_id INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            FOREIGN KEY (article_id) REFERENCES article(id),
            FOREIGN KEY (unite_id) REFERENCES unite(id),
            UNIQUE(article_id, unite_id)
        )
    ''')
    
    # Table des factures
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_client TEXT NOT NULL,
            date_facture TEXT NOT NULL,
            montant_total REAL NOT NULL
        )
    ''')
    
    # Détails des articles dans une facture (panier)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facture_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facture_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            unite_id INTEGER NOT NULL,
            quantite REAL NOT NULL,
            prix_unitaire REAL NOT NULL,
            prix_total REAL NOT NULL,
            FOREIGN KEY (facture_id) REFERENCES facture(id),
            FOREIGN KEY (article_id) REFERENCES article(id),
            FOREIGN KEY (unite_id) REFERENCES unite(id)
        )
    ''')
    
    # Insérer quelques données de test
    cursor.execute("INSERT OR IGNORE INTO unite (code, libelle) VALUES ('KG', 'Kilogramme')")
    cursor.execute("INSERT OR IGNORE INTO unite (code, libelle) VALUES ('SAC', 'Sac')")
    cursor.execute("INSERT OR IGNORE INTO unite (code, libelle) VALUES ('PCS', 'Pièce')")
    cursor.execute("INSERT OR IGNORE INTO unite (code, libelle) VALUES ('L', 'Litre')")
    
    # Insérer un entrepôt de test
    cursor.execute("INSERT OR IGNORE INTO entrepot (id, nom, localisation) VALUES (1, 'Entrepôt Principal', 'Antananarivo')")
    
    # Article de test (modifié pour inclure entrepot_id)
    cursor.execute("INSERT OR IGNORE INTO article (nom, reference, entrepot_id) VALUES ('Riz', 'RIZ001', 1)")
    cursor.execute("INSERT OR IGNORE INTO article (nom, reference, entrepot_id) VALUES ('Sucre', 'SUC001', 1)")
    
    # Prix de test
    cursor.execute("INSERT OR IGNORE INTO prix_article (article_id, unite_id, prix_unitaire) VALUES (1, 1, 4000)")  # Riz Kg
    cursor.execute("INSERT OR IGNORE INTO prix_article (article_id, unite_id, prix_unitaire) VALUES (1, 2, 150000)")  # Riz Sac
    cursor.execute("INSERT OR IGNORE INTO prix_article (article_id, unite_id, prix_unitaire) VALUES (2, 1, 3500)")  # Sucre Kg
    
    conn.commit()
    conn.close()
    
    print("✅ Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_database()