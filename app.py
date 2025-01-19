import streamlit as st
import requests
import json
import os

# URL de l'API (assurez-vous qu'elle est configurée dans vos variables d'environnement)
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
    "BMI": st.number_input("Quel est votre IMC ?", min_value=10.0, max_value=50.0, step=0.1),
    "GenHlth": st.selectbox(
        "Comment évalueriez-vous votre santé générale ?", 
        ["Excellent", "Très bonne", "Bonne", "Passable", "Mauvaise"]
    ),
    "Age": st.number_input("Quel est votre âge ?", min_value=18, max_value=120, step=1),
    "PhysHlth": st.slider("Combien de jours au cours des 30 derniers jours votre santé physique n'était pas bonne ?", 0, 30, 0),
    "Income": st.selectbox(
        "Quel est votre niveau de revenu ?", 
        [
            "Moins de 10 000 $",
            "Entre 10 000 $ et 14 999 $",
            "Entre 15 000 $ et 19 999 $",
            "Entre 20 000 $ et 24 999 $",
            "Entre 25 000 $ et 34 999 $",
            "Entre 35 000 $ et 49 999 $",
            "Entre 50 000 $ et 74 999 $",
            "75 000 $ ou plus"
        ]
    ),
    "Education": st.selectbox(
        "Quel est votre niveau d'éducation ?", 
        [
            "Jamais été à l'école ou seulement en maternelle",
            "Élémentaire (classes 1 à 8)",
            "Quelques années de lycée (classes 9 à 11)",
            "Diplômé du lycée ou GED",
            "1 à 3 ans d'études supérieures ou techniques",
            "4 ans ou plus d'études supérieures"
        ]
    ),
    "MentHlth": st.slider("Combien de jours au cours des 30 derniers jours votre santé mentale n'était pas bonne ?", 0, 30, 0),
    "HighChol": st.radio("Avez-vous de l'hypercholestérolémie ?", ["Non", "Oui"]),
    "DiffWalk": st.radio("Avez-vous des difficultés à monter les escaliers ?", ["Non", "Oui"]),
    "HeartDiseaseorAttack": st.radio("Avez-vous des antécédents de maladie cardiaque ou d'infarctus ?", ["Non", "Oui"])
}

# Conversion des réponses utilisateur en valeurs numériques pour l'API
mapped_features = {
    "HighBP": 1 if features["HighBP"] == "Oui" else 0,
    "BMI": features["BMI"],
    "GenHlth": ["Excellent", "Très bonne", "Bonne", "Passable", "Mauvaise"].index(features["GenHlth"]) + 1,
    "Age": get_age_group(features["Age"]),
    "PhysHlth": features["PhysHlth"],
    "Income": [
        "Moins de 10 000 $",
        "Entre 10 000 $ et 14 999 $",
        "Entre 15 000 $ et 19 999 $",
        "Entre 20 000 $ et 24 999 $",
        "Entre 25 000 $ et 34 999 $",
        "Entre 35 000 $ et 49 999 $",
        "Entre 50 000 $ et 74 999 $",
        "75 000 $ ou plus"
    ].index(features["Income"]) + 1,
    "Education": [
        "Jamais été à l'école ou seulement en maternelle",
        "Élémentaire (classes 1 à 8)",
        "Quelques années de lycée (classes 9 à 11)",
        "Diplômé du lycée ou GED",
        "1 à 3 ans d'études supérieures ou techniques",
        "4 ans ou plus d'études supérieures"
    ].index(features["Education"]) + 1,
    "MentHlth": features["MentHlth"],
    "HighChol": 1 if features["HighChol"] == "Oui" else 0,
    "DiffWalk": 1 if features["DiffWalk"] == "Oui" else 0,
    "HeartDiseaseorAttack": 1 if features["HeartDiseaseorAttack"] == "Oui" else 0
}

# Envoi des données à l'API et affichage du résultat
if st.button("Prédire"):
    payload = {"data": [list(mapped_features.values())]}
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        prediction = response.json().get("predictions", ["Erreur"])[0]
        st.success(f"Résultat de la prédiction : {'Diabète détecté' if prediction == 1 else 'Pas de diabète'}")
    else:
        st.error(f"Erreur : {response.text}")
