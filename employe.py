# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 01:23:10 2025

@author: AMINATA
"""

# -*- coding: utf-8 -*-
import pandas as pd
from db import get_connection


def ajouter_employe(nom, poste):
    """
    Ajoute un nouveau membre dans la base de données.
    """
    conn = get_connection()
    # MODIFICATION : On utilise ? au lieu de %s pour SQLite
    df = pd.read_sql("SELECT * FROM employes WHERE nom = ?", conn, params=(nom,))
    
    if not df.empty:
        conn.close()
        return False
        
    cur = conn.cursor()
    # MODIFICATION : On utilise ? au lieu de %s pour SQLite
    cur.execute(
        "INSERT INTO employes (nom, poste) VALUES (?, ?)",
        (nom, poste)
    )
    conn.commit()
    conn.close()
    return True

def get_employes():
    """Récupère la liste de tous les membres"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM employes", conn)
    conn.close()
    return df

def supprimer_employe(emp_id):
    """Supprime un membre de la base"""
    conn = get_connection()
    cur = conn.cursor()
    # MODIFICATION : On utilise ? au lieu de %s
    cur.execute("DELETE FROM employes WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()

def modifier_employe(emp_id, nouveau_nom, nouveau_poste):
    """Met à jour les informations"""
    conn = get_connection()
    cur = conn.cursor()
    # MODIFICATION : On utilise ? au lieu de %s
    cur.execute(
        "UPDATE employes SET nom = ?, poste = ? WHERE id = ?",
        (nouveau_nom, nouveau_poste, emp_id)
    )
    conn.commit()
    conn.close()
