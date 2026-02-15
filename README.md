# Assistant Mathématique (L2) — Suites, Séries, Séries de fonctions, Séries entières

## 1) Présentation générale

Ce dépôt contient une application web pédagogique (niveau **Licence 2**) destinée à **assister** l’étude de plusieurs objets classiques d’analyse :

- **Suites numériques**
- **Séries numériques**
- **Suites de fonctions**
- **Séries de fonctions**
- **Séries entières** (rayon de convergence, convergence sur un intervalle, étude du bord)
- **Développement en série entière** (Taylor au voisinage de 0, visualisation des tronqués)

L’objectif n’est pas de remplacer un raisonnement de cours, mais d’offrir :
- des **calculs symboliques** (quand c’est possible),
- des **affichages structurés** (formules + explications),
- des **visualisations** (sommes partielles, fonctions limites, tronqués).

> Remarque : le projet est en cours d’amélioration et ne couvre pas encore tous les cas pathologiques ou très avancés.

---

## 2) Fonctionnalités (ce que l’application fait)

### 2.1 Suites numériques
- Saisie d’un terme général `u_n`
- Calcul de `lim_{n→∞} u_n` (si SymPy le permet)
- Conclusion convergence / divergence (selon la limite obtenue)
- Graphe de la suite (si la fonction de tracé est disponible)

### 2.2 Séries numériques
- Saisie du terme général `u_n`
- Saisie de l’indice de départ
- Construction des sommes partielles
- Application de critères (selon les fonctions du projet)
- Visualisation : terme général et sommes partielles (si disponible)

### 2.3 Suites de fonctions
- Saisie de `f_n(x)`
- Choix d’un intervalle d’étude `I`
- Limite simple `lim_{n→∞} f_n(x)` (si accessible)
- Graphe de plusieurs `f_n` et de la limite (si trouvée)

### 2.4 Séries de fonctions
- Saisie de `u_n(x)`
- Indice de départ
- Choix d’un intervalle d’étude `I`
- Visualisation des sommes partielles `S_N(x)` sur `I`

### 2.5 Séries entières (et séries de puissances)
- Saisie du terme général (ex : `x^n/n!`, `(-1)^n*x^n`, `(x-1)^n`, etc.)
- Réécriture sous une forme exploitable `a_n (z(x))^n` quand c’est possible
- Calcul détaillé du **rayon de convergence** via :
  - **Cauchy–Hadamard** (prioritaire)
  - puis **d’Alembert** en recours (si nécessaire)
- Détermination de la zone :
  - `|z(x)| < R` (convergence absolue)
  - `|z(x)| > R` (divergence)
  - étude du **bord** `|z(x)| = R` avec critères de séries numériques (si disponibles)
- Visualisation : sommes partielles + éventuelle fonction somme (si déterminable)

### 2.6 Développement en série entière (Taylor)
- Saisie d’une fonction `f(x)`
- Choix d’un ordre (par défaut 10)
- Calcul du polynôme tronqué et/ou forme de série
- Estimation du rayon de convergence quand possible
- Visualisation : `f(x)` et les tronqués de Taylor

---

## 3) Technologies utilisées

### Backend
- **Python 3**
- **Flask** : serveur web (routes `/` et `/compute`)
- **SymPy** : calcul symbolique (limites, sommes, simplifications, intégrales éventuelles)
- **NumPy** : évaluations numériques (vectorisation)
- **Matplotlib** : génération de figures (renvoyées en base64)

### Frontend
- **HTML/CSS/JavaScript**
- **MathJax** : rendu LaTeX dans le navigateur
- Communication via `fetch("/compute")` en JSON

---

## 4) Structure typique du dépôt

*(Les noms peuvent varier selon ton dépôt, mais la logique est la suivante.)*

- `app.py`  
  Serveur Flask, parsing des entrées, appels aux fonctions d’étude, renvoi des résultats.
- `templates/index.html`  
  Interface : choix du type d’étude, champs de saisie, bloc intervalle, zone résultats.
- `static/app.js`  
  Gestion UI : champs affichés/masqués selon le type, construction du payload, affichage des messages.
- `static/style.css`  
  Style de l’interface.

---

## 5) Installation et lancement

### 5.1 Cloner le projet

```bash
git clone https://github.com/ton-utilisateur/nom-du-repo.git
cd nom-du-repo
```

---

### 5.2 Vérifier la version de Python

Le projet nécessite Python 3.9 ou supérieur.

```bash
python --version
```

---

### 5.3 Créer un environnement virtuel (recommandé)

Créer l’environnement :

```bash
python -m venv venv
```

Activer l’environnement :

**Windows (PowerShell)**

```bash
venv\Scripts\Activate.ps1
```

**Windows (cmd)**

```bash
venv\Scripts\activate.bat
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### 5.4 Installer les dépendances

Installation minimale :

```bash
pip install flask sympy numpy matplotlib
```

Si un fichier `requirements.txt` est présent :

```bash
pip install -r requirements.txt
```

---

### 5.5 Lancer le serveur

```bash
python app.py
```

Puis ouvrir dans un navigateur :

```
http://127.0.0.1:5000
```

---

## 6) Guide d’utilisation

### 6.1 Choisir un type d’étude

Dans le menu déroulant, sélectionner le type souhaité :

- Suite numérique  
- Série numérique  
- Suite de fonctions  
- Série de fonctions  
- Série entière  
- Développement en série entière  

Chaque type adapte automatiquement les champs affichés.

---

### 6.2 Renseigner l’expression

La syntaxe utilisée est celle de **SymPy**.

Exemples valides :

```
1/n
(-1)**n/n
1/n**2
sin(n*x)/n
x**n/factorial(n)
exp(x)
1/(1-x)
log(1+x)
```

Rappels importants :

- Les puissances s’écrivent avec `**`
- Les factorielles : `factorial(n)`
- Le logarithme naturel : `log(x)` ou `ln(x)`
- Les constantes : `pi`, `E`
- Les fonctions trigonométriques : `sin`, `cos`, `tan`, etc.

---

### 6.3 Indice minimal (si demandé)

Selon le type choisi :

- **Séries numériques** → indice de départ obligatoire  
- **Séries de fonctions / séries entières** → indice requis selon le cas  

Si un indice est requis mais non renseigné, un message d’erreur s’affiche.

---

### 6.4 Intervalle d’étude (si affiché)

Si aucun intervalle n’est indiqué, l’étude est faite sur **ℝ**.

Vous pouvez entrer :

- Bornes finies : `-1`, `2`, `pi`
- Infinis : `oo` ou `-oo`

Choisir le type de borne via :

- `( a , b )` → intervalle ouvert  
- `[ a , b ]` → intervalle fermé  
- `] a , b [` → notation française de l’ouvert  

L’intervalle est interprété automatiquement avant l’étude mathématique.

---

## 7) Améliorations prévues

- Optimisation des calculs symboliques lourds  
- Gestion plus fine des cas limites  
- Ajout progressif des séries de Fourier  
- Amélioration des visualisations graphiques  
- Structuration modulaire plus poussée du backend  

---

## 8) Remarque

Ce projet est développé dans le cadre d’un niveau Licence 2.  
Il est fonctionnel mais reste en évolution.  
Certaines parties peuvent encore être optimisées ou enrichies.
