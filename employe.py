# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 01:23:10 2025

@author: AMINATA
"""

# -*- coding: utf-8 -*-
import pandas as pd
from db import get_connection

def ajouter_employe(nom, poste, est_fonctionnaire=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM employes WHERE nom = %s AND poste = %s", (nom, poste))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return False
    
    cur.execute("""
        INSERT INTO employes (nom, poste, est_fonctionnaire, salaire_base, prix_heure) 
        VALUES (%s, %s, %s, 0, 0)
    """, (nom, poste, est_fonctionnaire))
    conn.commit()
    cur.close()
    conn.close()
    return True

def get_employes():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM employes ORDER BY nom ASC", conn)
    conn.close()
    return df

def modifier_employe(emp_id, nouveau_nom, nouveau_poste, est_fonctionnaire):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE employes 
        SET nom = %s, poste = %s, est_fonctionnaire = %s
        WHERE id = %s
    """, (nouveau_nom, nouveau_poste, est_fonctionnaire, emp_id))
    conn.commit()
    cur.close()
    conn.close()

def supprimer_employe(emp_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM employes WHERE id = %s", (emp_id,))
    conn.commit()
    cur.close()
    conn.close()