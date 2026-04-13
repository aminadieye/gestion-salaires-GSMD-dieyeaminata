# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 01:23:17 2025

@author: AMINATA
"""

# -*- coding: utf-8 -*-
import pandas as pd
from db import get_connection

def calculer_salaire(employe_id, mois, heures_examens, heures_autres, primes, retenues_manuelles, jours_absence, poste, salaire_base=0, est_fonctionnaire=False):
    poste_lower = poste.lower()
    retenue_absence = 0
    retenue_legale = 0

    # 1. Calcul du Brut
    if poste_lower in ["professeur", "professeur actionnaire"]:
        salaire_brut = (heures_examens * 2500) + (heures_autres * 2300)
        if poste_lower == "professeur actionnaire":
            salaire_brut += salaire_brut * 0.25
    else: 
        salaire_brut = salaire_base

    # 2. Calcul des retenues légales (IPRES/VRS)
    if not est_fonctionnaire:
        retenue_legale = salaire_brut * 0.056  # 5.6% IPRES

    # 3. Calcul des absences
    if poste_lower not in ["professeur", "professeur actionnaire"] and jours_absence > 0:
        valeur_jour = salaire_base / 30
        retenue_absence = valeur_jour * jours_absence

    # 4. Total des retenues
    retenue_totale = retenues_manuelles + retenue_absence + retenue_legale
    
    # 5. Net à payer
    salaire_net = salaire_brut + primes - retenue_totale
    
    if poste_lower not in ["professeur", "professeur actionnaire"]:
        heures_examens = 0
        heures_autres = 0

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO paiements (employe_id, mois, heures_examens, heures_autres, primes, retenues, salaire_net)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (employe_id, mois, heures_examens, heures_autres, primes, retenue_totale, salaire_net))
    conn.commit()
    cur.close()
    conn.close()
    
    return salaire_net, retenue_absence, retenue_legale, retenue_totale

def get_paiements():
    conn = get_connection()
    query = """
    SELECT p.id, e.nom, e.poste, p.mois, p.heures_examens, p.heures_autres, p.primes, p.retenues, p.salaire_net
    FROM paiements p
    JOIN employes e ON e.id = p.employe_id
    ORDER BY p.id DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_paiements_par_mois(mois):
    conn = get_connection()
    query = """
    SELECT e.nom, e.poste, p.mois, p.heures_examens, p.heures_autres, p.primes, p.retenues, p.salaire_net
    FROM paiements p
    JOIN employes e ON e.id = p.employe_id
    WHERE p.mois = %s
    """
    df = pd.read_sql(query, conn, params=(mois,))
    conn.close()
    return df

def get_total_mensuel(mois):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(salaire_net) FROM paiements WHERE mois = %s", (mois,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total or 0

def enregistrer_avance(employe_id, date_demande, mois_deduction, montant, motif):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO avances (employe_id, date_demande, mois_deduction, montant, motif)
        VALUES (%s, %s, %s, %s, %s)
    """, (employe_id, date_demande, mois_deduction, montant, motif))
    conn.commit()
    cur.close()
    conn.close()

def get_avances():
    conn = get_connection()
    query = """
    SELECT a.id, e.nom, a.date_demande, a.mois_deduction, a.montant, a.motif, a.statut
    FROM avances a
    JOIN employes e ON e.id = a.employe_id
    ORDER BY a.date_demande DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def verifier_avances_en_attente(employe_id, mois_deduction):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(montant) FROM avances 
        WHERE employe_id = %s AND mois_deduction = %s AND statut = 'En attente'
    """, (employe_id, mois_deduction))
    total_avances = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total_avances or 0

def marquer_avances_deduites(employe_id, mois_deduction):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE avances SET statut = 'Déduite'
        WHERE employe_id = %s AND mois_deduction = %s AND statut = 'En attente'
    """, (employe_id, mois_deduction))
    conn.commit()
    cur.close()
    conn.close()