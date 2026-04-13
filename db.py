# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 01:19:43 2025

@author: AMINATA
"""
# -*- coding: utf-8 -*-
import mysql.connector

def get_connection():
    # Connexion à la base de données gratuite AIVEN sur internet
    return mysql.connector.connect(
        host="mysql-30ebd1da-aminatadieye748-8208.g.aivencloud.com",
        user="avnadmin",
        password="AVNS_CLaCaKOQH-KpBLzcLkX",
        port="14916",
        database="defaultdb"
    )

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS paiements')
    cur.execute('DROP TABLE IF EXISTS avances')
    cur.execute('DROP TABLE IF EXISTS employes')

    # 1. Table des employés
    cur.execute('''
    CREATE TABLE IF NOT EXISTS employes (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        nom VARCHAR(255) NOT NULL,
        poste VARCHAR(100) NOT NULL,
        est_fonctionnaire BOOLEAN DEFAULT FALSE,
        salaire_base REAL DEFAULT 0,
        prix_heure FLOAT DEFAULT 0
    )
    ''')

    # 2. Table des paiements mensuels
    cur.execute('''
    CREATE TABLE IF NOT EXISTS paiements (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        employe_id INTEGER NOT NULL,
        mois VARCHAR(50) NOT NULL,
        heures_examens INTEGER DEFAULT 0,
        heures_autres INTEGER DEFAULT 0, 
        primes REAL,
        retenues REAL,
        salaire_net REAL,
        FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE
    )
    ''')

    # 3. Table des avances sur salaire
    cur.execute('''
    CREATE TABLE IF NOT EXISTS avances (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        employe_id INTEGER NOT NULL,
        date_demande DATE NOT NULL,
        mois_deduction VARCHAR(50) NOT NULL,
        montant REAL NOT NULL,
        motif VARCHAR(255),
        statut VARCHAR(20) DEFAULT 'En attente',
        FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables créées avec succès sur la base de données EN LIGNE (Aiven) !")