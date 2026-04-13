# -*- coding: utf-8 -*-
"""
Plateforme de Gestion des Salaires - GSMD
Auteur: AMINATA
"""

import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
from employe import ajouter_employe, get_employes, supprimer_employe, modifier_employe
from paiement import (calculer_salaire, get_paiements, get_total_mensuel, 
                      get_paiements_par_mois, enregistrer_avance, get_avances, 
                      verifier_avances_en_attente, marquer_avances_deduites)
from fiche_paie import creer_fiche_paie_pdf

# ----------- Configuration de la page -----------
st.set_page_config(page_title="Gestion Salaires", page_icon="💼", layout="wide")
st.title("💼 Plateforme de Gestion des Salaires")

# ----------- Menu Latéral -----------
menu = st.sidebar.selectbox("Menu Principal", [
    "📊 Tableau de Bord", 
    "👥 Gestion du Personnel", 
    "💸 Paiement salaire", 
    "💰 Avances sur salaire",
    "🗓️ Résumé mensuel",
    "📜 Historique global"
])

# ----------- 1. Tableau de Bord -----------
if menu == "📊 Tableau de Bord":
    st.subheader("📊 Vue d'ensemble de l'établissement")
    
    employes = get_employes()
    paiements = get_paiements()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_emp = len(employes) if not employes.empty else 0
        st.metric("Total Employés", f"{total_emp}")
        
    with col2:
        if not paiements.empty:
            total_paye = paiements['salaire_net'].sum()
            st.metric("Masse Salariale Totale", f"{total_paye:,.0f} FCFA".replace(',', ' '))
        else:
            st.metric("Masse Salariale", "0 FCFA")
            
    with col3:
        if not paiements.empty:
            dernier_mois = paiements['mois'].iloc[0]
            total_mois = paiements[paiements['mois'] == dernier_mois]['salaire_net'].sum()
            st.metric(f"Salaires {dernier_mois}", f"{total_mois:,.0f} FCFA".replace(',', ' '))
        else:
            st.metric("Dernier versement", "-")

    st.markdown("---")
    if not paiements.empty:
        st.markdown("### Évolution Mensuelle des Dépenses")
        df_graph = paiements.groupby('mois')['salaire_net'].sum().reset_index()
        fig = px.bar(df_graph, x='mois', y='salaire_net', text='salaire_net', 
                     labels={'salaire_net': 'Montant (FCFA)', 'mois': 'Mois'},
                     color='salaire_net', color_continuous_scale='Blues')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# ----------- 2. Gestion du Personnel -----------
elif menu == "👥 Gestion du Personnel":
    tab1, tab2, tab3 = st.tabs(["➕ Ajouter", "✏️ Modifier", "❌ Supprimer"])
    
    employes = get_employes()

    with tab1:
        st.subheader("Ajouter un nouvel employé")
        col_a, col_b = st.columns(2)
        with col_a:
            nom_new = st.text_input("Nom et Prénom")
        with col_b:
            poste_new = st.selectbox("Type de contrat", ["Professeur", "Professeur actionnaire", "Professeur forfaitaire", "Personnel"])
        
        est_fonc_new = st.checkbox("Cet employé est un fonctionnaire de l'État (Exonéré IPRES)")
        
        if st.button("Valider l'inscription"):
            if nom_new:
                if ajouter_employe(nom_new, poste_new, est_fonctionnaire=est_fonc_new):
                    st.success("✅ Employé enregistré avec succès.")
                    st.rerun()
                else:
                    st.warning("⚠️ Cet employé est déjà dans la base.")
            else:
                st.error("Le nom est obligatoire.")
        
        st.markdown("---")
        
        if not employes.empty:
            df_affichage = employes.copy()
            df_affichage['est_fonctionnaire'] = df_affichage['est_fonctionnaire'].apply(lambda x: 'Oui' if x == 1 or x == True else 'Non')
            st.dataframe(df_affichage, use_container_width=True)

    with tab2:
        if not employes.empty:
            st.subheader("Modifier un profil")
            list_names = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
            target = st.selectbox("Choisir l'employé à corriger", list_names)
            idx = list_names.index(target)
            curr_data = employes.iloc[idx]
            
            edit_nom = st.text_input("Corriger le nom", value=curr_data['nom'])
            edit_poste = st.selectbox("Changer le poste", ["Professeur", "Professeur actionnaire", "Professeur forfaitaire", "Personnel"], 
                                     index=["Professeur", "Professeur actionnaire", "Professeur forfaitaire", "Personnel"].index(curr_data['poste']))
            
            edit_fonc = st.checkbox("Fonctionnaire de l'État", value=bool(curr_data['est_fonctionnaire']))
            
            if st.button("Mettre à jour"):
                modifier_employe(int(curr_data['id']), edit_nom, edit_poste, edit_fonc)
                st.success("✅ Informations mises à jour.")
                st.rerun()
        else:
            st.info("Aucun employé à modifier.")

    with tab3:
        if not employes.empty:
            st.subheader("Supprimer un compte")
            list_suppr = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
            target_s = st.selectbox("Choisir l'employé à retirer", list_suppr)
            if st.button("Confirmer la suppression", type="primary"):
                idx_s = list_suppr.index(target_s)
                supprimer_employe(int(employes.iloc[idx_s]['id']))
                st.success("✅ Employé supprimé de la base.")
                st.rerun()

# ----------- 3. Paiement salaire -----------
elif menu == "💸 Paiement salaire":
    st.subheader("💸 Traitement de la paie mensuelle")
    employes = get_employes()
    
    if employes.empty:
        st.info("Veuillez d'abord ajouter des employés.")
    else:
        options = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
        selection = st.selectbox("Sélectionner l'employé", options)
        idx = options.index(selection)
        emp = employes.iloc[idx]
        
        mois_paye = st.text_input("Mois concerné (ex: Avril 2026)")
        
        avances_dues = 0
        if mois_paye:
            avances_dues = verifier_avances_en_attente(int(emp['id']), mois_paye)
            if avances_dues > 0:
                st.info(f"💡 Une avance de **{avances_dues:,.0f} FCFA** sera déduite ce mois-ci.")
                
        if emp['est_fonctionnaire']:
            st.info("ℹ️ Ce collaborateur est fonctionnaire de l'État : Aucune retenue IPRES ne sera appliquée.")

        st.markdown("### Éléments variables")
        if emp['poste'].lower() in ["professeur", "professeur actionnaire"]:
            c1, c2 = st.columns(2)
            h_ex = c1.number_input("Heures Classes Examen", min_value=0)
            h_at = c2.number_input("Heures Autres Classes", min_value=0)
            base_s, j_abs, total_h_pdf = 0, 0, h_ex + h_at
        else:
            c1, c2 = st.columns(2)
            base_s = c1.number_input("Salaire de base fixe", min_value=0.0)
            j_abs = c2.number_input("Nombre de jours d'absence", min_value=0, max_value=31)
            h_ex, h_at, total_h_pdf = 0, 0, 0

        c3, c4 = st.columns(2)
        prm = c3.number_input("Primes exceptionnelles", min_value=0.0)
        ret_m = c4.number_input("Autres retenues manuelles", min_value=0.0)
        
        ret_totale_input = ret_m + avances_dues

        if st.button("💾 Enregistrer et Générer le reçu"):
            if not mois_paye:
                st.error("Veuillez saisir le mois.")
            else:
                net, r_abs, r_legale, r_tot = calculer_salaire(
                    int(emp['id']), mois_paye, h_ex, h_at, prm, ret_totale_input, j_abs, emp['poste'], base_s, bool(emp['est_fonctionnaire'])
                )
                if avances_dues > 0: 
                    marquer_avances_deduites(int(emp['id']), mois_paye)
                
                if r_abs > 0: st.warning(f"Retenue Absence : {r_abs:,.0f} FCFA")
                if r_legale > 0: st.warning(f"Retenue Légale (IPRES 5.6%) : {r_legale:,.0f} FCFA")
                
                st.success(f"✅ Net à payer : {net:,.0f} FCFA".replace(',', ' '))
                
                nom_pdf = creer_fiche_paie_pdf(emp['nom'], emp['poste'], mois_paye, total_h_pdf, prm, r_tot, net)
                with open(nom_pdf, "rb") as f:
                    st.download_button("📄 Télécharger le Bulletin (PDF)", f, file_name=nom_pdf)

# ----------- 4. Avances sur salaire -----------
elif menu == "💰 Avances sur salaire":
    st.subheader("💰 Enregistrement des acomptes")
    employes = get_employes()
    if not employes.empty:
        with st.form("form_av"):
            opt_av = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
            sel_av = st.selectbox("Employé bénéficiaire", opt_av)
            mnt_av = st.number_input("Montant de l'avance", min_value=1000, step=1000)
            ms_av = st.text_input("Mois de déduction (ex: Mai 2026)")
            if st.form_submit_button("Valider l'avance"):
                if ms_av:
                    enregistrer_avance(int(employes.iloc[opt_av.index(sel_av)]['id']), datetime.today(), ms_av, mnt_av, "Avance sur salaire")
                    st.success("Avance enregistrée.")
                else:
                    st.error("Mois requis.")
        
        st.markdown("---")
        st.write("### Historique des avances")
        st.dataframe(get_avances(), use_container_width=True)

# ----------- 5. Résumé mensuel -----------
elif menu == "🗓️ Résumé mensuel":
    st.subheader("🗓️ Rapport mensuel de paie")
    m_search = st.text_input("Entrer le mois à analyser")
    if m_search:
        df_m = get_paiements_par_mois(m_search)
        if not df_m.empty:
            st.dataframe(df_m, use_container_width=True)
            st.metric("Total Décaissements", f"{get_total_mensuel(m_search):,.0f} FCFA".replace(',', ' '))
            
            # Export Excel
            buf = io.BytesIO()
            with pd.ExcelWriter(buf) as wr: df_m.to_excel(wr, index=False)
            st.download_button("📗 Télécharger le rapport Excel", buf.getvalue(), file_name=f"Salaires_{m_search}.xlsx")
        else:
            st.warning("Aucun historique pour ce mois.")

# ----------- 6. Historique global -----------
elif menu == "📜 Historique global":
    st.subheader("📜 Historique complet des transactions")
    st.dataframe(get_paiements(), use_container_width=True)