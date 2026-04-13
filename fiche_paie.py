# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 00:49:23 2026

@author: AMINATA
"""

# -*- coding: utf-8 -*-
from fpdf import FPDF
import os

def creer_fiche_paie_pdf(nom, poste, mois, total_heures, primes, retenues, net):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête de l'école
    pdf.set_font("Helvetica", 'B', 20)
    pdf.cell(0, 15, "GROUPE SCOLAIRE MAMADOU DIAGNE - GESTION RH", ln=True, align='C')
    pdf.set_font("Helvetica", 'I', 12)
    pdf.cell(0, 10, "Bulletin de salaire officiel", ln=True, align='C')
    pdf.ln(10)
    
    # Informations de l'employé
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(50, 10, "Mois de paie :", border=0)
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 10, f"{mois}", ln=True)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(50, 10, "Employé(e) :", border=0)
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 10, f"{nom}", ln=True)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(50, 10, "Poste :", border=0)
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 10, f"{poste}", ln=True)
    pdf.ln(10)
    
    # Tableau des montants
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(100, 10, "Désignation", border=1, align='C')
    pdf.cell(90, 10, "Montant / Quantité", border=1, align='C', ln=True)
    
    pdf.set_font("Helvetica", '', 12)
    if total_heures > 0:
        pdf.cell(100, 10, "Heures travaillées (Professeur)", border=1)
        pdf.cell(90, 10, f"{total_heures} h", border=1, align='C', ln=True)
    else:
        pdf.cell(100, 10, "Salaire de base (Personnel/Forfait)", border=1)
        pdf.cell(90, 10, "Forfait mensuel", border=1, align='C', ln=True)
        
    pdf.cell(100, 10, "Primes", border=1)
    pdf.cell(90, 10, f"+ {primes:,.0f} FCFA".replace(',', ' '), border=1, align='R', ln=True)
    
    pdf.cell(100, 10, "Retenues (Avances, Absences)", border=1)
    pdf.cell(90, 10, f"- {retenues:,.0f} FCFA".replace(',', ' '), border=1, align='R', ln=True)
    
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(100, 12, "NET À PAYER", border=1)
    pdf.cell(90, 12, f"{net:,.0f} FCFA".replace(',', ' '), border=1, align='R', ln=True)
    
    pdf.ln(20)
    pdf.set_font("Helvetica", 'I', 10)
    pdf.cell(0, 10, "Signature de l'employeur : _______________________", ln=True)
    pdf.cell(0, 10, "Signature de l'employé(e) : _______________________", ln=True)
    
    # Sauvegarde du fichier
    nom_fichier = f"Fiche_Paie_{nom.replace(' ', '_')}_{mois.replace(' ', '_')}.pdf"
    pdf.output(nom_fichier)
    
    return nom_fichier