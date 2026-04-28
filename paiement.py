# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 01:23:17 2025

@author: AMINATA
"""
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime
from db import get_connection

def calculer_salaire(emp_id, mois, h_ex, h_at, primes, autres_retenues, j_abs, statut, salaire_base=0.0):
    conn = get_connection()
    
    if statut in ["Professeur", "Prof Actionnaire", "Prof EG"]:
        if statut == "Prof EG":
            taux_examen = 2700
            taux_autres = 2500
        else:
            taux_examen = 2500
            taux_autres = 2300
            
        gain_base = (h_ex * taux_examen) + (h_at * taux_autres)
        retenue_absence = 0 
    else:
        gain_base = salaire_base
        retenue_absence = (salaire_base / 30) * j_abs if salaire_base > 0 else 0
        gain_base = gain_base - retenue_absence

    majoration = 0
    if statut == "Prof Actionnaire":
        majoration = gain_base * 0.25

    salaire_brut = gain_base + majoration + primes
    
    retenue_legale = 0
    if statut == "Agent permanent (Embauché)":
        retenue_legale = salaire_brut * 0.056
    else:
        if salaire_brut >= 25000:
            retenue_legale = salaire_brut * 0.05

    retenue_totale = autres_retenues + retenue_legale
    salaire_net = salaire_brut - retenue_totale

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO paiements (employe_id, mois, heures_examens, heures_autres, primes, retenues, salaire_net) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (emp_id, mois, h_ex, h_at, primes, retenue_totale, salaire_net)
    )
    conn.commit()
    conn.close()

    return salaire_net, retenue_absence, retenue_legale, retenue_totale

def get_paiements():
    conn = get_connection()
    query = """
    SELECT p.id, e.nom, e.poste as statut, p.mois, p.salaire_net 
    FROM paiements p
    JOIN employes e ON p.employe_id = e.id
    ORDER BY p.id DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_paiements_par_mois(mois):
    conn = get_connection()
    query = """
    SELECT e.nom, e.poste as statut, p.salaire_net 
    FROM paiements p
    JOIN employes e ON p.employe_id = e.id
    WHERE p.mois = ?
    """ 
    df = pd.read_sql(query, conn, params=(mois,))
    conn.close()
    return df

def get_total_mensuel(mois):
    df = get_paiements_par_mois(mois)
    return df['salaire_net'].sum() if not df.empty else 0

# --- NOUVELLE FONCTION : VÉRIFICATION DES DOUBLONS ---
def verifier_paiement_existant(emp_id, mois):
    """Vérifie si l'employé a déjà été payé pour ce mois précis"""
    conn = get_connection()
    query = "SELECT COUNT(*) as compte FROM paiements WHERE employe_id = ? AND mois = ?"
    df = pd.read_sql(query, conn, params=(emp_id, mois))
    conn.close()
    # Si le compte est supérieur à 0, ça veut dire qu'il a déjà été payé
    return df['compte'].iloc[0] > 0

# --- GESTION DES AVANCES ---
def enregistrer_avance(emp_id, date_demande, mois_deduction, montant, motif=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO avances (employe_id, date_demande, mois_deduction, montant, motif, statut) VALUES (?, ?, ?, ?, ?, 'En attente')",
        (emp_id, date_demande, mois_deduction, montant, motif)
    )
    conn.commit()
    conn.close()

def get_avances():
    conn = get_connection()
    query = """
    SELECT a.id, e.nom, a.date_demande, a.mois_deduction, a.montant, a.statut
    FROM avances a
    JOIN employes e ON a.employe_id = e.id
    ORDER BY a.id DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def verifier_avances_en_attente(emp_id, mois):
    conn = get_connection()
    query = "SELECT SUM(montant) as total FROM avances WHERE employe_id = ? AND mois_deduction = ? AND statut = 'En attente'"
    df = pd.read_sql(query, conn, params=(emp_id, mois))
    conn.close()
    return df['total'].iloc[0] if pd.notna(df['total'].iloc[0]) else 0

def marquer_avances_deduites(emp_id, mois):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE avances SET statut = 'Déduite' WHERE employe_id = ? AND mois_deduction = ? AND statut = 'En attente'", (emp_id, mois))
    conn.commit()
    conn.close()
