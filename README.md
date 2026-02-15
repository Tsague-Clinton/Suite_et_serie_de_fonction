
📘 Assistant d’Analyse des Suites et Séries (Projet L2)


📌 Présentation

Ce projet est une application web développée dans le cadre d’un niveau Licence 2 en Mathématiques.
Il propose un environnement interactif permettant d’étudier :
Suites numériques
Séries numériques
Suites de fonctions
Séries de fonctions
Séries entières
Développements en série entière

L’objectif est double :
Mettre en pratique les notions d’analyse vues en L2
Concevoir un outil structuré combinant calcul symbolique et visualisation graphique
Le projet n’est pas encore complet et reste évolutif.
🎯 Objectifs pédagogiques
Ce projet vise à :
Structurer un raisonnement mathématique formel
Implémenter des critères de convergence
Manipuler des expressions symboliques
Traduire un raisonnement mathématique en code
Concevoir une interface interactive pour l’analyse

✨ Fonctionnalités actuelles


1️⃣ Suites numériques
Calcul de limite symbolique
Détermination convergence / divergence
Représentation graphique

2️⃣ Séries numériques
Construction des sommes partielles
Application de critères classiques
Visualisation des termes et des sommes

3️⃣ Suites de fonctions
Étude sur un intervalle paramétrable
Analyse de convergence simple
Visualisation graphique
*
4️⃣ Séries de fonctions
Gestion de l’indice de départ
Étude sur intervalle choisi
Visualisation des sommes partielles
*
5️⃣ Séries entières
Mise sous forme
$$ u_n(x) = a_n (z(x))^n $$
Extraction automatique de � et �
Calcul du rayon de convergence :
Cauchy–Hadamard
d’Alembert
Étude des zones de convergence
Analyse du bord
Traduction sur un intervalle choisi
Visualisation graphique

6️⃣ Développement en série entière
Calcul de développement de Taylor
Détermination de l’intervalle de convergence
Visualisation des polynômes tronqués
🛠 Technologies utilisées
Backend
Python 3
Flask
SymPy
NumPy
Matplotlib
Frontend
HTML5
CSS3
JavaScript
MathJax (rendu LaTeX)
📂 Structure du projet
Copy code

project/
│
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── README.md
⚙️ Installation

1. Cloner le dépôt
Copy code
Bash
git clone https://github.com/votre-username/nom-du-projet.git
cd nom-du-projet
2. Créer un environnement virtuel (recommandé)
Copy code
Bash
python -m venv venv
Activation :
Windows :
Copy code
Bash
venv\Scripts\activate
Linux / macOS :
Copy code
Bash
source venv/bin/activate

4. Installer les dépendances
Copy code
Bash
pip install flask sympy numpy matplotlib

6. Lancer l’application
Copy code
Bash
python app.py
7. Accéder à l’interface
Ouvrir le navigateur :
Copy code

http://127.0.0.1:5000
📖 Exemples d’utilisation
Série entière
Entrée :
Copy code

x^n/n!
Indice minimal : 0
Résultat :
Rayon de convergence : +∞
Convergence sur ℝ
Fonction somme : exp(x)
Série numérique
Entrée :
Copy code

1/n^2
Indice minimal : 1
Résultat :
Convergence
Visualisation graphique
🚧 Limites actuelles
Projet encore en développement
Certaines analyses restent perfectibles
Les performances peuvent varier selon la complexité des expressions
Les séries de Fourier sont en cours d’implémentation
📚 Niveau et contexte
Projet réalisé dans le cadre d’une formation de Licence 2 en Mathématiques.
Il s’agit d’un projet d’apprentissage visant à consolider les bases d’analyse réelle et de calcul formel.
🔄 Évolutions prévues
Finalisation des séries de Fourier
Amélioration de l’interface
Optimisation des calculs symboliques
Enrichissement des critères de convergence
Meilleure gestion des cas limites
📄 Licence
Projet à usage pédagogique.
