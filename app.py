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
from db import create_tables
from employe import ajouter_employe, get_employes, supprimer_employe, modifier_employe
from paiement import (calculer_salaire, get_paiements, get_total_mensuel, 
                      get_paiements_par_mois, enregistrer_avance, get_avances, 
                      verifier_avances_en_attente, marquer_avances_deduites,
                      verifier_paiement_existant)
from fiche_paie import creer_fiche_paie_pdf

# ----------- Configuration et Design CSS -----------
st.set_page_config(page_title="GSMD - Salaires", page_icon="🏫", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .salaire-card { background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-radius: 15px; padding: 30px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 20px; margin-bottom: 20px; border: 1px solid #b1dfbb; }
    .salaire-card h2 { color: #155724; font-weight: 600; margin-bottom: 10px; font-size: 24px;}
    .salaire-card h1 { color: #155724; font-weight: 800; font-size: 42px; margin: 0; }
    .salaire-card p { color: #28a745; font-size: 16px; margin-top: 5px; }
    .stButton>button { border-radius: 8px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ----------- Listes Statiques pour les Mois / Années -----------
LISTE_MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

# Liste de 2025 à 2050
LISTE_ANNEES = [str(annee) for annee in range(2025, 2051)]

# Calcul intelligent de la position de l'année en cours
annee_actuelle_str = str(datetime.now().year)
INDEX_ANNEE_ACTUELLE = LISTE_ANNEES.index(annee_actuelle_str) if annee_actuelle_str in LISTE_ANNEES else 0

def convert_df_to_csv(df):
    return df.to_csv(index=False, sep=';').encode('utf-8-sig')

# ----------- SÉCURITÉ -----------
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    
    st.markdown("<br><br><h1 style='text-align: center; color: #2c3e50;'>🏫 Espace Gestionnaire GSMD</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Veuillez vous authentifier pour accéder à la plateforme.</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            password = st.text_input("🔐 Mot de passe :", type="password")
            if st.button("Se connecter", use_container_width=True, type="primary"):
                if password == "papa2024":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("❌ Mot de passe incorrect")
    return False

LISTE_STATUTS = ["Agent permanent (Embauché)", "Prof Actionnaire", "Prof Forfaitaire", "Professeur", "Contractuel de service", "Prof EG"]

# ----------- Lancement de l'application -----------
if check_password():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135810.png", width=80)
    st.sidebar.markdown("### 👤 Administration GSMD")
    st.sidebar.write("---")
    
    menu = st.sidebar.selectbox("Navigation", ["📊 Tableau de Bord", "👥 Agents et Vacataires", "💸 Paiement salaire", "💰 Avances sur salaire", "🗓️ Résumé mensuel", "📜 Historique global"])
    
    st.sidebar.write("---")
    if st.sidebar.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

    # ----------- 1. Tableau de Bord -----------
    if menu == "📊 Tableau de Bord":
        st.title("📊 Vue d'ensemble de l'établissement")
        employes = get_employes()
        paiements = get_paiements()
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("👥 Total Employés", len(employes) if not employes.empty else 0)
        with col2: st.metric("💰 Masse Salariale", f"{paiements['salaire_net'].sum():,.0f} FCFA" if not paiements.empty else "0 FCFA")
        with col3:
            if not paiements.empty:
                dernier_mois = paiements['mois'].iloc[-1]
                st.metric(f"📉 Salaires {dernier_mois}", f"{paiements[paiements['mois'] == dernier_mois]['salaire_net'].sum():,.0f} FCFA")
            else: st.metric("📉 Dernier versement", "-")
            
        st.write("---")
        if not paiements.empty:
            st.markdown("### 📈 Évolution Mensuelle des Dépenses")
            df_graph = paiements.groupby('mois')['salaire_net'].sum().reset_index()
            fig = px.bar(df_graph, x='mois', y='salaire_net', text='salaire_net', color='salaire_net', color_continuous_scale='Teal')
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis=(dict(showgrid=False)))
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("⚙️ Options Administrateur"):
            st.warning("⚠️ Action irréversible : Ceci va vider tout l'historique.")
            if st.button("Nettoyer la Base de Données"):
                create_tables()
                st.success("✅ Base réinitialisée !")

    # ----------- 2. Gestion du Personnel -----------
    elif menu == "👥 Agents et Vacataires":
        st.title("👥 Gestion de l'Équipe")
        tab1, tab2, tab3 = st.tabs(["➕ Ajouter un membre", "✏️ Modifier un profil", "❌ Supprimer un membre"])
        employes = get_employes()
        
        with tab1:
            with st.container(border=True):
                col_a, col_b = st.columns(2)
                nom_new = col_a.text_input("Nom et Prénom complet")
                statut_new = col_b.selectbox("Statut du contrat", LISTE_STATUTS)
                if st.button("Valider l'inscription", type="primary"):
                    if nom_new and ajouter_employe(nom_new, statut_new):
                        st.success(f"✅ {nom_new} a été enregistré.")
                        st.rerun()
                        
        with tab2:
            if not employes.empty:
                with st.container(border=True):
                    list_names = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
                    target = st.selectbox("Choisir la personne à modifier", list_names)
                    curr_data = employes.iloc[list_names.index(target)]
                    c1, c2 = st.columns(2)
                    edit_nom = c1.text_input("Nom", value=curr_data['nom'])
                    idx_statut = LISTE_STATUTS.index(curr_data['poste']) if curr_data['poste'] in LISTE_STATUTS else 0
                    edit_statut = c2.selectbox("Statut", LISTE_STATUTS, index=idx_statut)
                    if st.button("Mettre à jour les informations"):
                        modifier_employe(int(curr_data['id']), edit_nom, edit_statut)
                        st.rerun()
                        
        with tab3:
            if not employes.empty:
                with st.container(border=True):
                    list_suppr = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
                    target_s = st.selectbox("Sélectionner la personne à retirer", list_suppr)
                    if st.button("Confirmer la suppression", type="primary"):
                        supprimer_employe(int(employes.iloc[list_suppr.index(target_s)]['id']))
                        st.rerun()
                        
        if not employes.empty: 
            st.write("---")
            st.dataframe(employes[['nom', 'poste']], use_container_width=True, hide_index=True)

    # ----------- 3. Paiement salaire -----------
    elif menu == "💸 Paiement salaire":
        st.title("💸 Traitement de la Paie Mensuelle")
        employes = get_employes()
        
        if not employes.empty:
            options = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
            selection = st.selectbox("👤 Sélectionnez le bénéficiaire", options)
            emp = employes.iloc[options.index(selection)]
            statut_emp = emp['poste']
            
            with st.container(border=True):
                st.markdown("##### 🗓️ Période de paie")
                col_m, col_y = st.columns(2)
                mois_actuel_idx = datetime.now().month - 1
                sel_mois = col_m.selectbox("Mois", LISTE_MOIS, index=mois_actuel_idx)
                sel_annee = col_y.selectbox("Année", LISTE_ANNEES, index=INDEX_ANNEE_ACTUELLE)
                mois_paye = f"{sel_mois} {sel_annee}"
                
                # Vérification des doublons
                deja_paye = verifier_paiement_existant(int(emp['id']), mois_paye)
                
                if deja_paye:
                    st.error(f"🛑 ATTENTION : {emp['nom']} a DÉJÀ été payé(e) pour le mois de {mois_paye}.")
                    st.info("💡 Allez dans l'historique global si vous souhaitez vérifier cette transaction ou effectuer un correctif.")
                else:
                    if statut_emp == "Agent permanent (Embauché)": st.info("ℹ️ Règle : **IPRES (5.6%)** sur le brut.")
                    elif statut_emp == "Prof Actionnaire": st.info("ℹ️ Règle : **Majoration +25%** et **BRS (5%)**.")
                    elif statut_emp == "Contractuel de service": st.info("ℹ️ Règle : Salaire fixe et **BRS (5%)**.")
                    elif statut_emp == "Prof EG": st.info("ℹ️ Règle : Taux 2700/2500 et **BRS (5%)**.")
                    else: st.info("ℹ️ Règle : **BRS (5%)**.")
                    
                    avances_dues = verifier_avances_en_attente(int(emp['id']), mois_paye) if mois_paye else 0
                    if avances_dues > 0: st.warning(f"⚠️ Une avance de **{avances_dues:,.0f} FCFA** sera déduite.")

                    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
                    
                    if statut_emp in ["Professeur", "Prof Actionnaire", "Prof EG"]:
                        st.markdown("##### ⏱️ Heures travaillées")
                        c1, c2 = st.columns(2)
                        h_ex = c1.number_input("Heures Classes Examen", min_value=0, step=1)
                        h_at = c2.number_input("Heures Autres Classes", min_value=0, step=1)
                        base_s, j_abs, total_h_pdf = 0, 0, h_ex + h_at
                    else:
                        st.markdown("##### 💶 Salaire et Présence")
                        c1, c2 = st.columns(2)
                        base_s = c1.number_input("Salaire Mensuel Fixe (FCFA)", min_value=0.0, step=1000.0)
                        j_abs = c2.number_input("Jours d'absence", min_value=0, max_value=31, step=1)
                        h_ex, h_at, total_h_pdf = 0, 0, 0

                    st.markdown("##### 🎁 Autres éléments")
                    c3, c4 = st.columns(2)
                    prm = c3.number_input("Primes Exceptionnelles (Bonus)", min_value=0.0, step=1000.0)
                    ret_m = c4.number_input("Autres retenues manuelles", min_value=0.0, step=1000.0)

                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.button(f"💾 Calculer et Valider le Paiement pour {mois_paye}", use_container_width=True, type="primary"):
                        # Calcul réel dans la base de données
                        net, r_abs, r_legale, r_tot = calculer_salaire(int(emp['id']), mois_paye, h_ex, h_at, prm, ret_m + avances_dues, j_abs, statut_emp, base_s)
                        if avances_dues > 0: marquer_avances_deduites(int(emp['id']), mois_paye)
                        
                        # --- RECONSTITUTION DES VARIABLES POUR LE PDF OFFICIEL ---
                        if statut_emp == "Prof EG":
                            gain_base_pdf = (h_ex * 2700) + (h_at * 2500)
                            des_base_pdf = f"Vacations (Examen:{h_ex}h / Autres:{h_at}h)"
                        elif statut_emp in ["Professeur", "Prof Actionnaire"]:
                            gain_base_pdf = (h_ex * 2500) + (h_at * 2300)
                            des_base_pdf = f"Vacations (Examen:{h_ex}h / Autres:{h_at}h)"
                        else:
                            gain_base_pdf = base_s
                            des_base_pdf = "Salaire de base fixe"
                            
                        majoration_pdf = gain_base_pdf * 0.25 if statut_emp == "Prof Actionnaire" else 0
                        brut_pdf = (gain_base_pdf - r_abs) + majoration_pdf + prm
                        
                        if statut_emp == "Agent permanent (Embauché)":
                            nom_impot, taux_impot = "Cotisation IPRES", "5.6%"
                        else:
                            nom_impot, taux_impot = "Retenue BRS", "5%" if brut_pdf >= 25000 else "0%"
                        # --------------------------------------------------------

                        st.markdown(f"""
                        <div class="salaire-card">
                            <h2>✅ Paiement Validé : {emp['nom']}</h2>
                            <h1>{net:,.0f} FCFA</h1>
                            <p>Période : {mois_paye}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Appel de la nouvelle fonction PDF avec les taux détaillés
                        nom_pdf = creer_fiche_paie_pdf(
                            nom=emp['nom'], statut=statut_emp, mois=mois_paye,
                            designation_base=des_base_pdf, base_montant=gain_base_pdf,
                            retenue_abs=r_abs, majoration=majoration_pdf, primes=prm,
                            brut=brut_pdf, nom_impot=nom_impot, taux_impot=taux_impot,
                            montant_impot=r_legale, autres_retenues=ret_m,
                            avances=avances_dues, net_a_payer=net
                        )
                        
                        with open(nom_pdf, "rb") as f:
                            st.download_button("📄 Télécharger le Bulletin (PDF)", f, file_name=f"Fiche_{emp['nom']}_{mois_paye.replace(' ', '_')}.pdf", use_container_width=True)

    # ----------- 4. Avances sur salaire -----------
    elif menu == "💰 Avances sur salaire":
        st.title("💰 Gestion des Acomptes")
        employes = get_employes()
        if not employes.empty:
            with st.container(border=True):
                with st.form("form_av"):
                    opt_av = [f"{row['nom']} ({row['poste']})" for _, row in employes.iterrows()]
                    sel_av = st.selectbox("Employé bénéficiaire", opt_av)
                    st.markdown("##### Détails de l'acompte")
                    mnt_av = st.number_input("Montant (FCFA)", min_value=1000, step=1000)
                    col_m, col_y = st.columns(2)
                    sel_mois_av = col_m.selectbox("Mois de déduction", LISTE_MOIS, index=datetime.now().month - 1)
                    sel_annee_av = col_y.selectbox("Année de déduction", LISTE_ANNEES, index=INDEX_ANNEE_ACTUELLE)
                    ms_av = f"{sel_mois_av} {sel_annee_av}"
                    if st.form_submit_button("Valider l'acompte", use_container_width=True):
                        enregistrer_avance(int(employes.iloc[opt_av.index(sel_av)]['id']), datetime.today(), ms_av, mnt_av, "Avance")
                        st.success(f"✅ Acompte enregistré. Déduction prévue en {ms_av}.")
            st.write("---")
            st.dataframe(get_avances(), use_container_width=True, hide_index=True)

    # ----------- 5. Résumé mensuel -----------
    elif menu == "🗓️ Résumé mensuel":
        st.title("🗓️ Rapport Mensuel de Paie")
        with st.container(border=True):
            col_m, col_y = st.columns(2)
            sel_mois_rech = col_m.selectbox("Mois à consulter", LISTE_MOIS, index=datetime.now().month - 1)
            sel_annee_rech = col_y.selectbox("Année", LISTE_ANNEES, index=INDEX_ANNEE_ACTUELLE)
            m = f"{sel_mois_rech} {sel_annee_rech}"
            if m:
                df = get_paiements_par_mois(m)
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.markdown(f"""
                    <div style="background-color: #e2e3e5; padding: 15px; border-radius: 10px; border-left: 5px solid #6c757d; margin-top:15px; margin-bottom:15px;">
                        <h3 style="margin:0; color: #383d41;">Total : {get_total_mensuel(m):,.0f} FCFA</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    csv = convert_df_to_csv(df)
                    st.download_button(label=f"📥 Exporter Excel", data=csv, file_name=f"Rapport_{m.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
                else: st.info(f"Aucun paiement enregistré pour {m}.")

    # ----------- 6. Historique global -----------
    elif menu == "📜 Historique global":
        st.title("📜 Archives des Transactions")
        df_hist = get_paiements()
        if not df_hist.empty:
            with st.container(border=True):
                st.subheader("🔍 Filtrer les résultats")
                col1, col2 = st.columns(2)
                recherche_nom = col1.text_input("Chercher un employé :", placeholder="Tapez un nom...")
                filtre_statut = col2.selectbox("Filtrer par contrat :", ["Tous"] + LISTE_STATUTS)
                if recherche_nom: df_hist = df_hist[df_hist['nom'].str.contains(recherche_nom, case=False, na=False)]
                if filtre_statut != "Tous": df_hist = df_hist[df_hist['statut'] == filtre_statut]
            st.write("---")
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            csv_hist = convert_df_to_csv(df_hist)
            st.download_button("📥 Exporter l'historique", data=csv_hist, file_name="Historique.csv", mime="text/csv", use_container_width=True)
        else: st.info("Base vide.")
