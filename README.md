💻 README.md

# 🛒 Projet 4 : Cod_Test (E-commerce)

Projet final de validation pour le module **Méthodes de Test et Validation de Logiciels (MVTL)** à l'IIT.
Ce projet implémente une plateforme e-commerce Django robuste, validée par une suite de tests automatisés complète.

## 📂 Structure du Projet
- **cooldeal/** : Configuration principale du projet.
- **shop/** : Gestion du catalogue et du panier (Cœur du métier).
- **customer/** : Gestion des clients et authentification.
- **contact/** : Formulaire de contact.
- **tests/** : Suite de tests automatisés (Unitaires, Intégration, Fonctionnels).

## 🚀 Installation

1. **Cloner le projet**
   
   git clone <votre-repo-url>
   cd cod_test

2.	Créer un environnement virtuel

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux

source venv/bin/activate
3.	Installer les dépendances

pip install -r requirements.txt requirements_2.txt

4.	Migrations et Démarrage

python manage.py migrate
python manage.py runserver

Exécution des Tests (QA)
Ce projet utilise pytest avec une configuration stricte pour garantir la qualité du code.
Lancer toute la suite de tests
pytest
Générer le rapport de couverture (Coverage)
La commande suivante lance les tests et génère un rapport HTML détaillé sur la couverture du code :
pytest --cov=shop --cov=customer --cov=contact --html=report.html
Une fois terminé :
•	Ouvrir report.html pour voir le détail des succès/échecs.
•	Ouvrir htmlcov/index.html pour explorer la couverture ligne par ligne.
📊 Matrice de Risques & Stratégie
Les tests ont été priorisés selon la criticité des modules :
•	Priorité Haute : Shop (Panier/Produits) & Customer (Auth).
•	Priorité Moyenne : Site Config.
•	Priorité Basse : Contact.
