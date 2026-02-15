
📘 Assistant d’Analyse des Suites et Séries
Projet de Licence 2 – Mathématiques
📌 Présentation
Ce projet est une application web développée dans le cadre d’une Licence 2 de Mathématiques.
Il permet d’étudier de manière interactive :
Suites numériques
Séries numériques
Suites de fonctions
Séries de fonctions
Séries entières
Développements en série entière
L’objectif est pédagogique : mettre en pratique les notions d’analyse vues en L2 tout en développant une application structurée combinant calcul symbolique et visualisation graphique.
Le projet reste en cours d’amélioration et n’est pas encore exhaustif.
🎯 Objectifs pédagogiques
Ce projet vise à :
Structurer un raisonnement mathématique rigoureux
Implémenter des critères classiques de convergence
Manipuler des expressions symboliques
Traduire un raisonnement mathématique en code
Concevoir une interface interactive cohérente
✨ Fonctionnalités actuelles
1️⃣ Suites numériques
Calcul symbolique de limite
Détermination convergence / divergence
Représentation graphique
2️⃣ Séries numériques
Construction des sommes partielles
Application de critères classiques
Visualisation des termes et des sommes
3️⃣ Suites de fonctions
Étude sur intervalle paramétrable
Analyse de convergence
Visualisation graphique
4️⃣ Séries de fonctions
Gestion de l’indice de départ
Étude sur intervalle choisi
Visualisation des sommes partielles
5️⃣ Séries entières
Mise sous la forme
uₙ(x) = aₙ · (z(x))ⁿ
Extraction automatique de aₙ et z(x)
Calcul du rayon de convergence :
Formule de Cauchy–Hadamard
Critère de d’Alembert
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
MathJax (rendu des formules mathématiques)
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
1️⃣ Cloner le dépôt
Copy code
Bash
git clone https://github.com/votre-username/nom-du-projet.git
cd nom-du-projet
2️⃣ Créer un environnement virtuel (recommandé)
Copy code
Bash
python -m venv venv
Activation :
Windows
Copy code
Bash
venv\Scripts\activate
Linux / macOS
Copy code
Bash
source venv/bin/activate
3️⃣ Installer les dépendances
Copy code
Bash
pip install flask sympy numpy matplotlib
4️⃣ Lancer l’application
Copy code
Bash
python app.py
5️⃣ Accéder à l’interface
Ouvrir le navigateur à l’adresse :
Copy code

http://127.0.0.1:5000
📖 Exemples d’utilisation
Exemple 1 — Série entière
Entrée :
Copy code

x^n/n!
Indice minimal : 0
Résultat attendu :
Rayon de convergence : +∞
Convergence sur ℝ
Fonction somme : exp(x)
Exemple 2 — Série numérique
Entrée :
Copy code

1/n^2
Indice minimal : 1
Résultat attendu :
Convergence
Visualisation graphique
🚧 Limites actuelles
Projet encore en développement
Certaines analyses restent perfectibles
Les performances peuvent varier selon la complexité des expressions
La partie Séries de Fourier est en cours d’implémentation
📚 Contexte académique
Projet réalisé dans le cadre d’une Licence 2 en Mathématiques.
Il s’agit d’un projet d’apprentissage visant à consolider les bases d’analyse réelle et de calcul formel.
🔄 Évolutions prévues
Finalisation des séries de Fourier
Amélioration de l’interface utilisateur
Optimisation des calculs symboliques
Enrichissement des critères de convergence
Gestion plus fine des cas limites
📄 Licence
