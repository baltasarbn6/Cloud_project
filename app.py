import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL")

st.title("Prédiction du diabète avec XGBoost")
st.write("Répondez aux questions ci-dessous pour prédire votre risque de diabète.")

# Fonction pour convertir l'âge en tranche
def get_age_group(age):
    if age < 18:
        return 1
    elif age <= 24:
        return 1
    elif age <= 29:
        return 2
    elif age <= 34:
        return 3
    elif age <= 39:
        return 4
    elif age <= 44:
        return 5
    elif age <= 49:
        return 6
    elif age <= 54:
        return 7
    elif age <= 59:
        return 8
    elif age <= 64:
        return 9
    elif age <= 69:
        return 10
    elif age <= 74:
        return 11
    elif age <= 79:
        return 12
    else:
        return 13

# Questions utilisateur
features = {
    "HighBP": st.radio("Avez-vous de l'hypertension ?", ["Non", "Oui"]),
    "HighChol": st.radio("Avez-vous de l'hypercholestérolémie ?", ["Non", "Oui"]),
    "CholCheck": st.radio("Avez-vous fait un test de cholestérol dans l'année ?", ["Non", "Oui"]),
    "BMI": st.number_input("Quel est votre IMC ?", min_value=10.0, max_value=50.0, step=0.1),
    "Smoker": st.radio("Êtes-vous fumeur ?", ["Non", "Oui"]),
    "Stroke": st.radio("Avez-vous eu un AVC ?", ["Non", "Oui"]),
    "HeartDiseaseorAttack": st.radio("Avez-vous des antécédents de maladie coronarienne ou d'infarctus ?", ["Non", "Oui"]),
    "PhysActivity": st.radio("Avez-vous pratiqué une activité physique au cours du dernier mois ?", ["Non", "Oui"]),
    "Fruits": st.radio("Mangez-vous au moins un fruit par jour ?", ["Non", "Oui"]),
    "Veggies": st.radio("Mangez-vous au moins un légume par jour ?", ["Non", "Oui"]),
    "HvyAlcoholConsump": st.radio(
        "Consommez-vous beaucoup d'alcool (homme : au moins 14 verres/semaine, femme : au moins 7 verres/semaine) ?", 
        ["Non", "Oui"]
    ),
    "AnyHealthcare": st.radio("Avez-vous une couverture médicale ?", ["Non", "Oui"]),
    "NoDocbcCost": st.radio("Pouvez-vous aller chez le médecin sans problème de coût ?", ["Non", "Oui"]),
    "GenHlth": st.selectbox(
        "Comment évalueriez-vous votre santé générale ?", 
        ["Excellent", "Très bonne", "Bonne", "Passable", "Mauvaise"]
    ),
    "MentHlth": st.slider("Combien de jours au cours des 30 derniers jours votre santé mentale n'était pas bonne ?", 0, 30, 0),
    "PhysHlth": st.slider("Combien de jours au cours des 30 derniers jours votre santé physique n'était pas bonne ?", 0, 30, 0),
    "DiffWalk": st.radio("Avez-vous des difficultés à monter les escaliers ?", ["Non", "Oui"]),
    "Sex": st.radio("Quel est votre sexe ?", ["Femme", "Homme"]),
    "Age": st.number_input("Quel est votre âge ?", min_value=18, max_value=120, step=1),
    "Education": st.selectbox(
        "Quel est votre niveau d'éducation ?", 
        [
            "Never attended school or only kindergarten",
            "Grades 1 through 8 (Elementary)",
            "Grades 9 through 11 (Some high school)",
            "Grade 12 or GED (High school graduate)",
            "College 1 year to 3 years (Some college or technical school)",
            "College 4 years or more (College graduate)"
        ]
    ),
    "Income": st.selectbox(
        "Quel est votre niveau de revenu ?", 
        [
            "Moins de 10 000€ par an",
            "Entre 10 000€ et 15 000€ par an",
            "Entre 15 000 € et 20 000€ par an",
            "Entre 20 000 € et 25 000€ par an",
            "Entre 25 000 € et 35 000€ par an",
            "Entre 35 000 € et 50 000€ par an",
            "Entre 50 000 € et 75 000€ par an",
            "Plus de 75 000 € par an"
        ]
    )
}

# Conversion des réponses utilisateur en format numérique
mapped_features = {
    "HighBP": 1 if features["HighBP"] == "Oui" else 0,
    "HighChol": 1 if features["HighChol"] == "Oui" else 0,
    "CholCheck": 1 if features["CholCheck"] == "Oui" else 0,
    "BMI": features["BMI"],
    "Smoker": 1 if features["Smoker"] == "Oui" else 0,
    "Stroke": 1 if features["Stroke"] == "Oui" else 0,
    "HeartDiseaseorAttack": 1 if features["HeartDiseaseorAttack"] == "Oui" else 0,
    "PhysActivity": 1 if features["PhysActivity"] == "Oui" else 0,
    "Fruits": 1 if features["Fruits"] == "Oui" else 0,
    "Veggies": 1 if features["Veggies"] == "Oui" else 0,
    "HvyAlcoholConsump": 1 if features["HvyAlcoholConsump"] == "Oui" else 0,
    "AnyHealthcare": 1 if features["AnyHealthcare"] == "Oui" else 0,
    "NoDocbcCost": 1 if features["NoDocbcCost"] == "Oui" else 0,
    "GenHlth": ["Excellent", "Très bonne", "Bonne", "Passable", "Mauvaise"].index(features["GenHlth"]) + 1,
    "MentHlth": features["MentHlth"],
    "PhysHlth": features["PhysHlth"],
    "DiffWalk": 1 if features["DiffWalk"] == "Oui" else 0,
    "Sex": 1 if features["Sex"] == "Homme" else 0,
    "Age": get_age_group(features["Age"]),
    "Education": [
        "Never attended school or only kindergarten",
        "Grades 1 through 8 (Elementary)",
        "Grades 9 through 11 (Some high school)",
        "Grade 12 or GED (High school graduate)",
        "College 1 year to 3 years (Some college or technical school)",
        "College 4 years or more (College graduate)"
    ].index(features["Education"]) + 1,
    "Income": [
        "Less than $10,000",
        "Less than $15,000 ($10,000 to less than $15,000)",
        "Less than $20,000 ($15,000 to less than $20,000)",
        "Less than $25,000 ($20,000 to less than $25,000)",
        "Less than $35,000 ($25,000 to less than $35,000)",
        "Less than $50,000 ($35,000 to less than $50,000)",
        "Less than $75,000 ($50,000 to less than $75,000)",
        "$75,000 or more"
    ].index(features["Income"]) + 1
}

# Prédire avec les données transformées
if st.button("Prédire"):
    payload = {"data": [list(mapped_features.values())]}
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        prediction = response.json().get("predictions", ["Erreur"])[0]
        st.success(f"Résultat de la prédiction : {'Diabète détecté' if prediction == 1 else 'Pas de diabète'}")
    else:
        st.error(f"Erreur : {response.text}")
