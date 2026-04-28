# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 00:49:23 2026

@author: AMINATA
"""

# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

def creer_fiche_paie_pdf(nom, statut, mois, designation_base, base_montant, retenue_abs, majoration, primes, brut, nom_impot, taux_impot, montant_impot, autres_retenues, avances, net_a_payer):
    """
    Génère un bulletin de salaire PDF avec le format standard (Base, Taux, Gains, Retenues).
    """
    filename = f"Bulletin_{nom.replace(' ', '_')}_{mois.replace(' ', '_')}.pdf"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # === EN-TÊTE ===
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(40, height - 50, "GROUPE SCOLAIRE MAMADOU DIAGNE (GSMD)")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.gray)
    c.drawString(40, height - 65, "Éducation - Rigueur - Excellence")
    c.drawString(40, height - 80, "Pout/Thiès, Sénégal")
    
    c.setStrokeColor(colors.black)
    c.line(40, height - 95, width - 40, height - 95)
    
    # === TITRE ===
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 130, "BULLETIN DE PAIE")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2.0, height - 145, f"Période de paiement : {mois}")
    
    # === INFOS EMPLOYÉ ===
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, height - 180, "INFORMATIONS SALARIÉ :")
    c.setFont("Helvetica", 10)
    c.drawString(45, height - 200, f"Nom et Prénom : {nom}")
    c.drawString(45, height - 220, f"Qualification : {statut}")
    
    c.rect(40, height - 235, width - 80, 70) # Cadre employé
    
    # === TABLEAU DES RUBRIQUES ===
    y = height - 280
    
    # En-tête du tableau (Fond gris)
    c.setFillColor(colors.lightgrey)
    c.rect(40, y, width - 80, 20, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    
    # Titres des colonnes
    c.drawString(45, y + 6, "DÉSIGNATION")
    c.drawCentredString(315, y + 6, "BASE")
    c.drawCentredString(380, y + 6, "TAUX")
    c.drawCentredString(445, y + 6, "GAINS")
    c.drawCentredString(515, y + 6, "RETENUES")
    
    y -= 20
    c.setFont("Helvetica", 9)
    
    def draw_row(y_pos, des, base, taux, gain, ret):
        """Dessine une ligne du tableau avec les séparateurs verticaux"""
        c.drawString(45, y_pos + 6, des)
        if base: c.drawRightString(345, y_pos + 6, str(base))
        if taux: c.drawRightString(405, y_pos + 6, str(taux))
        if gain: c.drawRightString(475, y_pos + 6, f"{gain:,.0f}".replace(',', ' '))
        if ret: c.drawRightString(550, y_pos + 6, f"{ret:,.0f}".replace(',', ' '))
        
        # Lignes verticales et horizontales
        c.setStrokeColor(colors.grey)
        c.line(40, y_pos, width - 40, y_pos) # Ligne du bas
        c.line(40, y_pos, 40, y_pos + 20)    # Bord gauche
        c.line(280, y_pos, 280, y_pos + 20)  # Sep Désignation/Base
        c.line(350, y_pos, 350, y_pos + 20)  # Sep Base/Taux
        c.line(410, y_pos, 410, y_pos + 20)  # Sep Taux/Gains
        c.line(480, y_pos, 480, y_pos + 20)  # Sep Gains/Retenues
        c.line(width - 40, y_pos, width - 40, y_pos + 20) # Bord droit
    
    # 1. Base / Heures
    draw_row(y, designation_base, "", "", base_montant, "")
    y -= 20
    
    # 2. Absence
    if retenue_abs > 0:
        draw_row(y, "Retenue pour absence", "", "", "", retenue_abs)
        y -= 20
        
    # 3. Majoration Actionnaire
    if majoration > 0:
        base_maj = base_montant - retenue_abs
        draw_row(y, "Majoration Actionnaire", f"{base_maj:,.0f}", "25%", majoration, "")
        y -= 20
        
    # 4. Primes
    if primes > 0:
        draw_row(y, "Primes exceptionnelles", "", "", primes, "")
        y -= 20
        
    # Ligne Total Brut (Gris clair)
    c.setFillColor(colors.HexColor("#f4f6f6"))
    c.rect(40, y, width - 80, 20, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 6, "SALAIRE BRUT IMPOSABLE")
    c.drawRightString(475, y + 6, f"{brut:,.0f}".replace(',', ' '))
    c.setFont("Helvetica", 9)
    y -= 20
    
    # 5. Impôts (IPRES ou BRS)
    if montant_impot > 0:
        draw_row(y, nom_impot, f"{brut:,.0f}", taux_impot, "", montant_impot)
        y -= 20
        
    # 6. Autres retenues
    if autres_retenues > 0:
        draw_row(y, "Autres retenues manuelles", "", "", "", autres_retenues)
        y -= 20
        
    # 7. Avances
    if avances > 0:
        draw_row(y, "Acompte / Avance sur salaire", "", "", "", avances)
        y -= 20
        
    # Contour extérieur (fermer le tableau)
    c.setStrokeColor(colors.black)
    c.line(40, y, width - 40, y) # Ligne finale du tableau
    
    # === NET À PAYER ===
    y -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "NET À PAYER :")
    
    # Encadré du Net
    c.setFillColor(colors.black)
    c.rect(width - 200, y - 10, 160, 30, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 50, y - 2, f"{net_a_payer:,.0f} FCFA".replace(',', ' '))
    
    # === CACHET ET SIGNATURE ===
    y -= 80
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, y, "Pour valoir ce que de droit.")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 30, "Signature de l'Employé")
    c.drawString(width - 220, y - 30, "La Direction (Cachet et Signature)")
    
    c.save()
    return filepath
