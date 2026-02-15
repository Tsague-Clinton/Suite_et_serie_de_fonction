# ============================================================
# app.py (Flask + SymPy)
# Ce fichier a été assemblé manuellement pour remplacer Streamlit
# par une interface HTML/CSS/JS, sans modifier la logique mathématique.
# ============================================================

from flask import Flask, request, jsonify, render_template

import sympy as sp
from sympy import symbols, re, im, conjugate, I
from sympy import *
from sympy import ln as log
import matplotlib
matplotlib.use("Agg")  # backend non-interactif côté serveur
import matplotlib.pyplot as plt
from sympy.calculus.util import continuous_domain
from sympy import S
from sympy.assumptions import Q, ask

import io
import base64

app = Flask(__name__)

# ------------------------------------------------------------
# Symbole global k utilisé dans les séries
# Dans ton code Streamlit, k était parfois défini hors fonctions.
# Ici on le rend global pour que test_Riemann/test_Leibniz/etc. ne plantent pas.
# ------------------------------------------------------------
k = sp.symbols('k', integer=True, positive=True)

# ============================================================
# Faux Streamlit : garde les appels st.latex(), st.info(), st.error(), st.pyplot()
# ============================================================

class _StreamlitCompat:
    def __init__(self):
        self._out = []

    def set_out(self, out):
        self._out = out

    def set_page_config(self, **kwargs):
        pass

    def title(self, txt):
        pass

    def markdown(self, txt):
        pass

    def radio(self, *args, **kwargs):
        return None

    def text_input(self, *args, **kwargs):
        return None

    def button(self, *args, **kwargs):
        return False

    def latex(self, msg):
        self._out.append({"type": "latex", "content": msg})

    def info(self, msg):
        self._out.append({"type": "info", "content": str(msg)})

    def error(self, msg):
        self._out.append({"type": "error", "content": str(msg)})

    def pyplot(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        self._out.append({"type": "plot", "content": b64})


st = _StreamlitCompat()

# ============================================================
# Dictionnaire des fonctions bornées connues (aucune fonction composée ici)
# ============================================================

BORNES_CONNUES = {
    sp.sin: (-1, 1),
    sp.cos: (-1, 1),
    sp.sign: (-1, 1),
    sp.Abs: (0, None),
}




def signe_asymptotique(expr, n):
    # 1. Test direct
    if expr.is_positive:
        return 1
    if expr.is_negative:
        return -1

    # 2. Test par la limite
    try:
        L = sp.limit(expr, n, sp.oo)
        if L.is_positive:
            return 1
        if L.is_negative:
            return -1
    except:
        pass

    # 3. Terme dominant
    try:
        lead = expr.as_leading_term(n)
        if lead.is_positive:
            return 1
        if lead.is_negative:
            return -1
    except:
        pass

    # 4. Dernier recours seulement
    try:
        sol = sp.solve_univariate_inequality(expr > 0, n, relational=False)
        if sol.sup == sp.oo:
            return 1
        sol2 = sp.solve_univariate_inequality(expr < 0, n, relational=False)
        if sol2.sup == sp.oo:
            return -1
    except:
        pass

    return 0   # signe indéterminé


def domination_log(expression, n):
    """
    Détecte des formes du type 1/(log(n))^a avec a > 0
    et renvoie une borne inférieure simple : 1/n
    """
    try:
        num, den = expression.as_numer_denom()
        if num == 1:
            # cas 1/log(n)
            if den == sp.log(n):
                return 1/n

            # cas 1/(log(n))^a
            if den.is_Pow:
                base, exp = den.as_base_exp()
                if base == sp.log(n) and exp.is_positive:
                    return 1/n
    except:
        pass

    return None

def min_borne(a, b):
    diff = sp.simplify(a - b)
    if diff.is_nonpositive:
        return a
    elif diff.is_nonnegative:
        return b
    return a


def max_borne(a, b):
    diff = sp.simplify(a - b)
    if diff.is_nonnegative:
        return a
    elif diff.is_nonpositive:
        return b
    return b


def borne_constante_variable(expression, variable):
    if expression.is_Number:
        return expression, expression
    if expression == variable:
        return expression, expression
    if expression.is_Pow and expression.base == -1 and expression.exp.has(variable):
        return sp.sympify(-1), sp.sympify(1)
    return None


def borne_fonction(expression):
    if expression.is_Function and expression.func in BORNES_CONNUES:
        bmin, bmax = BORNES_CONNUES[expression.func]
        if bmin is not None and bmax is not None:
            return sp.sympify(bmin), sp.sympify(bmax)
        else:
            return expression, expression
    return None


def borne_somme(expression, variable):
    if expression.is_Add:
        somme_min, somme_max = 0, 0
        for terme in expression.args:
            tmin, tmax = encadrements(terme, variable)
            somme_min += tmin
            somme_max += tmax
        return sp.simplify(somme_min), sp.simplify(somme_max)
    return None


def borne_produit(expression, variable):
    if expression.is_Mul:
        prod_min, prod_max = 1, 1
        for facteur in expression.args:
            fmin, fmax = encadrements(facteur, variable)
            c1 = min_borne(prod_min * fmin, prod_min * fmax)
            c2 = min_borne(prod_max * fmin, prod_max * fmax)
            prod_min = min_borne(c1, c2)
            c3 = max_borne(prod_min * fmin, prod_min * fmax)
            c4 = max_borne(prod_max * fmin, prod_max * fmax)
            prod_max = max_borne(c3, c4)
        return sp.simplify(prod_min), sp.simplify(prod_max)
    return None


def borne_puissance(expression, variable):
    if not expression.is_Pow:
        return None

    base, exposant = expression.as_base_exp()
    res = encadrements(base, variable)
    if res is None:
        return None
    bmin, bmax = res

    try:
        # Cas exposant = -1  → inversion
        if exposant == -1:
            # inversion seulement si le signe est contrôlé
            if bmin.is_positive:
                # 0 < bmin ≤ base ≤ bmax
                return sp.simplify(1/bmax), sp.simplify(1/bmin)

            if bmax.is_negative:
                # bmin ≤ base ≤ bmax < 0
                return sp.simplify(1/bmin), sp.simplify(1/bmax)

            # signe inconnu → on refuse
            return None

        # Cas exposant entier pair
        if exposant.is_Integer and exposant % 2 == 0:
            # base toujours ≥ 0
            if bmin.is_nonnegative:
                return sp.simplify(bmin**exposant), sp.simplify(bmax**exposant)

            # base toujours ≤ 0
            if bmax.is_nonpositive:
                return sp.simplify(bmax**exposant), sp.simplify(bmin**exposant)

            # base change de signe
            return 0, sp.simplify(max(abs(bmin), abs(bmax))**exposant)

        # Cas exposant impair
        if exposant.is_Integer and exposant % 2 == 1:
            return sp.simplify(bmin**exposant), sp.simplify(bmax**exposant)

        return None

    except:
        return None


def borne_fraction(expression, variable):
    try:
        numerateur, denominateur = expression.as_numer_denom()
        if denominateur == 1:
            return None

        nmin, nmax = encadrements(numerateur, variable)
        dmin, dmax = encadrements(denominateur, variable)

        signe = signe_asymptotique(denominateur, variable)

        # dénominateur positif à l’infini
        if signe == 1:
            min_total = min_borne(nmin / dmax, nmax / dmax)
            max_total = max_borne(nmin / dmin, nmax / dmin)
            return sp.simplify(min_total), sp.simplify(max_total)

        # dénominateur négatif à l’infini
        if signe == -1:
            min_total = min_borne(nmax / dmax, nmin / dmax)
            max_total = max_borne(nmax / dmin, nmin / dmin)
            return sp.simplify(min_total), sp.simplify(max_total)

        # signe incertain → on refuse l’encadrement
        return None

    except:
        return None


def encadrements(expression, variable):
    resultat = borne_constante_variable(expression, variable)
    if resultat is not None:
        return resultat
    resultat = borne_fonction(expression)
    if resultat is not None:
        return resultat
    resultat = borne_somme(expression, variable)
    if resultat is not None:
        return resultat
    resultat = borne_produit(expression, variable)
    if resultat is not None:
        return resultat
    resultat = borne_puissance(expression, variable)
    if resultat is not None:
        return resultat
    resultat = borne_fraction(expression, variable)
    if resultat is not None:
        return resultat
    return expression, expression


def graphe(u_n, n, c):
    """
    Version corrigée : supporte
    - suite u_n
    - somme partielle S_n = Sum(...)
    """
    try:
        domaine = continuous_domain(u_n, n, S.Reals)
    except:
        domaine = S.Reals

    x_ = []
    y_ = []

    # Cas Sum : on calcule numériquement S_N = sum_{j=n_min..N} expr(j)
    if isinstance(u_n, sp.Sum):
        expr = u_n.function
        lims = u_n.limits[0]     # (k, n_min, n)
        kk, n_min, _ = lims[0], lims[1], lims[2]

        f = sp.lambdify(kk, expr, 'numpy')

        for N in range(0, 400):
            if domaine.contains(N):
                try:
                    if N < int(n_min):
                        continue
                    s = 0.0
                    for j in range(int(n_min), N + 1):
                        s += float(f(j))
                    x_.append(N)
                    y_.append(s)
                except: 
                    pass

    # Cas suite simple
    else:
        u = sp.lambdify(n, u_n, 'numpy')
        for N in range(0, 1500):
            if domaine.contains(N):
                try:
                    yk = float(u(N))
                    x_.append(N)
                    y_.append(yk)
                except:
                    pass

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(x_, y_, color=c, label=r"$" + sp.latex(u_n) + "$")
    ax.set_xlabel("n")
    ax.set_ylabel("$" + sp.latex(u_n) + "$")
    ax.legend()

    st.pyplot(fig)


def positivite(u_n, n, n_min):
    ###
    # Teste la positivité de la suite u_n à partir de n_min et retourne :(True/False/None, message_latex/None)
    ###
    try:
        try:
            x = sp.symbols('x', real=True, positive=True)

            pos = sp.solve_univariate_inequality(
                u_n.subs(n, x) >= 0,
                x,
                relational=False,
                domain=S.Reals.intersect(sp.Interval(n_min, sp.oo))
            )
            resultat = (u_n.is_nonnegative or (pos != sp.EmptySet))
            if resultat is True:
                msg = r"\text{La suite } \left( " + sp.latex(u_n) + r" \right)_{ n \in \mathbb{N}} \text{ est bien toujours positive pour tout } n \geq " + sp.latex(n_min)
                return True, msg
        except:
            resultat = u_n.is_nonnegative

            if resultat is True:
                msg = r"\text{La suite } \left( " + sp.latex(u_n) + r" \right)_{ n \in \mathbb{N}} \text{ est bien toujours positive pour tout n}"
                return True, msg
            else:
                return None, None

    except:
        return None, None


def facteur(expression):
    facteur, reste = expression.as_coeff_Mul()
    return facteur


def decroissance(a_n, n):
    try:
        a_n1 = a_n.subs(n, n + 1)
        diff = sp.diff(a_n, n)
        delta = sp.simplify(a_n1 - a_n)
        lim_diff = sp.limit_seq(diff, n)
        quot = sp.simplify(a_n1 / a_n)

        if delta.is_nonpositive is True:
            msg = (r"\left(" + sp.latex(a_n) + r"\right)_{n \in \mathbb{N}}"
                   r"\text{ est décroissante , en effet : } \forall n \in \mathbb {N}  , a_{n+1} - a_n  = "
                   + sp.latex(a_n1) + " - " + sp.latex(a_n) + " =" + sp.latex(delta) + r"\le 0 ")
            return True, msg

        if (sp.simplify(quot - 1)).is_nonpositive and a_n.is_nonnegative:
            msg = "(" + sp.latex(a_n) + r")_{n \in \mathbb{N}}"
            msg += r"\text{ est décroissante , en effet :  }  \forall n \in \mathbb {N}  , \frac{a_{n+1}}{a_n}  = "
            msg += sp.latex(quot) + r"\le 1 "
            return True, msg

        if diff.is_nonpositive:
            msg = r"\left(" + sp.latex(a_n) + r"\right)_{n \in \mathbb{N}} \text{ est décroissante, en effet : } "
            msg += r"\text{considérons } f(n) = " + sp.latex(a_n) + r", \text{ on a } f'(n) = " + sp.latex(diff) + r" \le 0"
            return True, msg

        else:
            try:
                x = sp.symbols('x', real=True)
                diffx = diff.subs(n, x)

                negative = sp.solve_univariate_inequality(diffx <= 0, x, relational=False)
                derivable = continuous_domain(diffx, x, domain=S.Reals)
                negative2 = derivable.intersect(negative)

                if lim_diff.is_negative:
                    if derivable.sup == sp.oo:
                        msg = (
                            r"Soit la suite définie par \( a_n = " + sp.latex(a_n) + r"\) pour \( n \in \mathbb{N}^* \). "
                            r"La suite \( \left(a_n\right)_{n \in \mathbb{N}^*} \) est décroissante à partir d'un certain rang. En effet :\\"
                            r"Considérons la fonction \( f \) définie par \( f(n) = a_n \).\\"
                            r"La fonction \( f \) est dérivable sur " + sp.latex(derivable) + r", et l'on a :\\"
                            r"\( f'(n) = " + sp.latex(diff) + r", \quad \lim\limits_{n \to \infty} f'(n) = " + sp.latex(lim_diff) + r" \leq 0 \)."
                        )
                        return True, msg

                if negative2.sup == sp.oo and negative2 != EmptySet:
                    msg = (
                        r"\text{Soit la suite définie par } a_n = " + sp.latex(a_n) + r" \text{ pour } n \in \mathbb{N}^*.\\"
                        r"\text{La suite } \left(a_n\right)_{n \in \mathbb{N}^*} \text{ est décroissante à partir d'un certain rang. En effet :}\\"
                        r"\text{On considère la fonction } f : \mathbb{R} \to \mathbb{R} \text{ définie par } f(x) = " + sp.latex(a_n.subs(n, x)) + r".\\"
                        r"\text{On a } f(n) = a_n. \text{ La fonction } f \text{ est dérivable sur } " + sp.latex(derivable) + r", \text{ et sa dérivée vaut :}\\"
                        r"f'(n) = " + sp.latex(diff) + r", \text{ donc } f'(n) \leq 0 \text{ pour } n \in " + sp.latex(negative2) + r".\\"
                        r"\text{Il existe donc un rang } N \in \mathbb{N} \text{ tel que pour tout } n \geq N, \ a_{n+1} - a_n < 0."
                    )
                    return True, msg

            except:
                pass

    except Exception as e:
        msg = f"Détail technique (décroissance) : {e}"
        return None, msg

    return False, None


def identif_fonction_log(expression, variable):
    log_bool = False
    n_bool = False
    dictionnaire_fonctions = expression.as_powers_dict()
    for fonction in dictionnaire_fonctions:
        if not ((fonction - variable).equals(0)) and not fonction.has(sp.log):
            return False
        if (fonction - variable).equals(0):
            n_bool = True
        if (fonction.has(sp.log)):
            log_bool = True
    return n_bool and log_bool


def detecte_alternance(expression, symbole):
    for puissance in expression.atoms(sp.Pow):
        base, exposant = puissance.args
        if base == -1 and exposant.has(symbole):
            return True
    return False


def extraire_partie_positive(expression, symbole, debut):
    for puissance in expression.atoms(sp.Pow):
        base, exposant = puissance.args
        if base == -1 and exposant.has(symbole):
            quotient = expression / puissance
            if quotient.is_nonnegative or positivite(quotient, symbole, debut)[0]:
                return sp.simplify(quotient)
            elif quotient.is_nonpositive:
                return sp.simplify(-quotient)
            else:
                return None


def dl(u_n, n):
    try:
        x = sp.symbols('x')
        u_x = u_n.subs(n, 1 / x)
        dl_x = sp.series(u_x, x, 0, 10)
        dl_n = sp.simplify(dl_x.subs(x, 1 / n))
        dl = dl_x.as_leading_term(x).subs(x, 1 / n)

        if sp.simplify(dl) == sp.simplify(u_n):
            return None

        st.latex(r"\text{Développement limité de } " + sp.latex(u_n) + r" \text{ en } \frac{1}{n} \text{ à l'ordre 2 autour de 0 : } ")
        st.latex(sp.latex(u_n) + "=" + sp.latex(dl_n) + r"\Longrightarrow" + sp.latex(u_n) + r"\sim " + sp.latex(dl) + r"\text { à l'infini }")
        return dl
    except:
        return None


def diverge(u_n, n):
    try:
        lim = sp.limit_seq(u_n, n)
        if lim is None:
            st.latex(r"\lim_{n \to \infty} " + sp.latex(u_n) + r" \text{ n'existe pas.}")
            return True
        if lim.is_zero is True:
            return False
        elif lim.is_zero is False:
            return True
        else:
            return True
    except Exception as e:
        st.info(f"Détail technique : {e}")
        return True


def prepare_Riemann(expression, n):
    expression_approx = expression.evalf()
    facteur_val = facteur(expression_approx)
    if facteur_val == 0:
        facteur_val = 1
    expression_approx = expression_approx / facteur_val

    numerateur = expression_approx.as_numer_denom()[0]
    try:
        num = int(numerateur)
    except (TypeError, ValueError):
        return None

    dict = expression.as_numer_denom()[1].as_powers_dict()
    return num, dict


def test_Riemann(u_n, n, n_min):
    S_n = sp.Sum(u_n.subs(n, k), (k, n_min, n))
    P = prepare_Riemann(u_n, n)
    if P is None:
        return None
    else:
        num, dict = P
        if int(num) == 1 and len(dict) == 1 and list(dict.keys())[0] == n:
            s = dict[n]
            if s > 1:
                st.latex(r"\text{Puisque } " + sp.latex(s) + r" > 1, \quad \sum " + sp.latex(1 / n**s) +
                         r" \text{ converge par le critère de Riemann . Donc la série de somme partielle }" +
                         sp.latex(S_n) + r"\text{ aussi }")
                return True
            else:
                st.latex(r"\text{Puisque } " + sp.latex(s) + r" \leq 1, \quad \sum " + sp.latex(1 / n**s) +
                         r" \text{ diverge par le critère de Riemann .Donc la série de somme partielle}" +
                         sp.latex(S_n) + r"\text{ aussi }")
                return False
    return None


def test_Leibniz(u_n, n, n_min):
    S_n = sp.Sum(u_n.subs(n, k), (k, n_min, n))

    if (detecte_alternance(sp.simplify(u_n), n)) or (detecte_alternance(sp.simplify(u_n), n + 1)):
        a_n = extraire_partie_positive(u_n, n, n_min)
        if a_n is None:
            return None

        p, affichage_p = positivite(a_n, n, n_min)
        l = sp.limit_seq(a_n, n)
        d, affichage_d = decroissance(a_n, n)

        if p and d and (l == 0):
            st.latex(affichage_p)
            st.latex(affichage_d)
            st.latex(r"\text{ De plus}" + " " + r"\lim_{n \to \infty} " + sp.latex(a_n) + r"=" + sp.latex(l))
            st.latex(r"\text{ La serie de somme partielle}" + sp.latex(S_n) + r" \text{ converge donc par le critère de Leibniz} ")
            try:
                graphe(a_n, n, 'violet')
            except:
                pass
            return True
    return None


def test_bertrand(u_n, n, n_min):
    S_n = sp.Sum(u_n.subs(n, k), (k, n_min, n))
    u_n = sp.simplify(u_n)

    v_n = u_n / facteur(u_n)
    numerateur, denominateur = v_n.as_numer_denom()

    try:
        n_numerateur = sp.sympify(int(numerateur))
    except:
        return None

    # On ne traite que les formes du type : 1 / (n * (log(n))^a)
    # Correction : on remplace as_factors() par l'utilisation correcte de .args
    if denominateur.is_Mul:
        facteurs = denominateur.args
    else:
        facteurs = [denominateur]

    if n in facteurs:
        autres = [f for f in facteurs if f != n]

        exposant_log = 0
        for f in autres:
            if f.is_Pow:
                base, exp = f.as_base_exp()
                if base == sp.log(n):
                    exposant_log += exp
                else:
                    return None
            elif f == sp.log(n):
                exposant_log += 1
            else:
                return None

        if exposant_log > 1:
            st.latex(
                r"\text{La série } " + sp.latex(S_n) +
                r"\text{ converge par le critère de Bertrand.}"
            )
            return True

        if exposant_log <= 1:
            st.latex(
                r"\text{La série } " + sp.latex(S_n) +
                r"\text{ diverge par le critère de Bertrand.}"
            )
            return False

    return None

def test_Alembert(u_n, n, n_min):
    S_n = sp.Sum(u_n.subs(n, k), (k, n_min, n))
    u_n1 = u_n.subs(n, n + 1)
    if u_n.is_nonnegative:
        st.latex(positivite(u_n, n, n_min)[1])
        if u_n != 0:
            quotient = sp.simplify(sp.Abs(u_n1 / u_n))
            L = sp.limit(quotient, n, sp.oo)

            if L < 1:
                st.latex(r"\text{En effet }\lim_{n \to \infty} \left| {\frac{u_{n+1}}{u_n}} \right| = "
                         + r"\lim_{n \to \infty}" + sp.latex(quotient) + "=" + sp.latex(L) + r"\text { <  1}")
                st.latex(r"\text {La série de somme partielle }" + sp.latex(S_n) + r"\text { converge donc par le critère d'Alembert}")
                return True
            if L > 1:
                st.latex(r"\text{En effet }\lim_{n \to \infty} \left| {\frac{u_{n+1}}{u_n}} \right|  = "
                         + r"\lim_{n \to \infty}" + sp.latex(quotient) + "=" + sp.latex(L) + r"\text { >  1}")
                st.latex(r"\text {La série de somme partielle }" + sp.latex(S_n) + r"\text{ diverge donc par le critère d'Alembert}")
                return False
    return None


def test_equivalence(u_n, n, n_min):
    S_n = sp.Sum(u_n.subs(n, k), (k, n_min, n))
    equivalent = dl(u_n, n)

    if equivalent is not None:
        if not sp.simplify(u_n - equivalent).equals(0):
            try:
                C = critere(equivalent, n, n_min)
                if C is True:
                    st.latex(r"\text { La  série de somme partielle}" + sp.latex(S_n) + r"\text { converge par équivalence }")
                    return True
                if C is False:
                    st.latex(r"\text { La  série de somme partielle}" + sp.latex(S_n) + r"\text { diverge par équivalence }")
                    return False
            except Exception as e:
                st.info(f"Erreur dans l'évaluation de l'équivalent : {e}")
    return None


def test_comparaison(u_n, n, n_min):
    S_n = sp.Sum(u_n.subs(n, k), (k, n_min, n))

    # Cas spécial : 1 / (log(n))^a  → toujours divergent par comparaison avec 1/n
    try:
        num, den = sp.simplify(u_n).as_numer_denom()
        if num == 1:
            # 1/log(n)
            if den == sp.log(n):
                st.latex(
                    r"\text{On a } \log(n) < n \text{ pour } n \text{ assez grand, donc } "
                    + sp.latex(u_n) + r" \ge \frac{1}{n}."
                )
                st.latex(
                    r"\text{Or } \sum \frac{1}{n} \text{ diverge, donc par comparaison } "
                    + sp.latex(S_n) + r" \text{ diverge.}"
                )
                return False

            # 1/(log(n))^a
            if den.is_Pow:
                base, exp = den.as_base_exp()
                if base == sp.log(n) and exp.is_positive:
                    st.latex(
                        r"\text{On a } \log(n) < n \text{ pour } n \text{ assez grand, donc } "
                        + sp.latex(u_n) + r" \ge \frac{1}{n}."
                    )
                    st.latex(
                        r"\text{Or } \sum \frac{1}{n} \text{ diverge, donc par comparaison } "
                        + sp.latex(S_n) + r" \text{ diverge.}"
                    )
                    return False
    except:
        pass

    # Encadrement classique sinon
    a, b = encadrements(u_n, n)
    min_un = min_borne(a, b)
    max_un = max_borne(a, b)

    if not min_un.is_nonnegative:
        return None

    # Comparaison par majoration
    try:
        test_sup = critere(max_un, n, n_min)
        if test_sup is True:
            st.latex(
                r"\text{Comme } " + sp.latex(u_n) + r" \le " + sp.latex(max_un) +
                r"\text{ et que la série de référence converge, alors } "
                + sp.latex(S_n) + r"\text{ converge.}"
            )
            return True
    except:
        pass

    # Comparaison par minoration
    try:
        test_inf = critere(min_un, n, n_min)
        if test_inf is False:
            st.latex(
                r"\text{Comme } " + sp.latex(u_n) + r" \ge " + sp.latex(min_un) +
                r"\text{ et que la série de référence diverge, alors } "
                + sp.latex(S_n) + r"\text{ diverge.}"
            )
            return False
    except:
        pass

    return None
def convergence_absolue(u_n, n, n_min):
    # On teste seulement les critères simples sur |u_n|
    v_n = sp.Abs(u_n)

    # On évite absolument toute récursion
    R = test_Riemann(v_n, n, n_min)
    if R is not None:
        st.latex(r"\text{ La série de somme partielle } \sum " + sp.latex(u_n) +
                 r" \text{ converge absolument.}")
        return True

    B = test_bertrand(v_n, n, n_min)
    if B is not None:
        st.latex(r"\text{ La série de somme partielle } \sum " + sp.latex(u_n) +
                 r" \text{ converge absolument.}")
        return True

    A = test_Alembert(v_n, n, n_min)
    if A is not None:
        st.latex(r"\text{ La série de somme partielle } \sum " + sp.latex(u_n) +
                 r" \text{ converge absolument.}")
        return True

    return None


def critere(u_n, n, n_min):

    # pile de protection contre les appels circulaires
    if not hasattr(critere, "_pile"):
        critere._pile = []

    u_s = sp.simplify(u_n)

    # si on retombe sur la même suite → on coupe
    for old in critere._pile:
        if sp.simplify(old - u_s).equals(0):
            return None

    critere._pile.append(u_s)

    try:
        L = test_Leibniz(u_n, n, n_min)
        if L is not None:
            return L

        R = test_Riemann(u_n, n, n_min)
        if R is not None:
            return R

        B = test_bertrand(u_n, n, n_min)
        if B is not None:
            return B

        A = test_Alembert(u_n, n, n_min)
        if A is not None:
            return A

        C = test_comparaison(u_n, n, n_min)
        if C is not None:
            return C

        Cv = convergence_absolue(u_n, n, n_min)
        if Cv is True:
            return True

        E = test_equivalence(u_n, n, n_min)
        if E is not None:
            return E

        return None

    finally:
        critere._pile.pop()


# ============================================================
# Routes Flask
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compute", methods=["POST"])
def compute():
    data = request.get_json(force=True) or {}
    out = []
    st.set_out(out)

    type_input = data.get("type_input", "")
    user_input1 = (data.get("user_input1") or "").strip()
    user_input2 = (data.get("user_input2") or "").strip()

    try:
        # Déclaration de n comme dans ton code
        n = sp.symbols('n', integer=True, positive=True)
        x = sp.symbols('x', real=True)

        u = sp.sympify(
            user_input1,
            locals={
                "n": n,
                "arctan": atan, "arcsin": asin, "arccos": acos,
                "arctanh": atanh, "arcsinh": asinh, "arccosh": acosh,
                "arcsec": asec, "arccot": acot, "arccsc": acsc,
                "sin": sin
            }
        )
        u_n = sp.simplify(u)

        if type_input == "Série":
            if user_input1 and not user_input2:
                st.latex(r"\text{Veuillez donner la valeur de l'indice de depart}")
                return jsonify({"messages": out})

            if (not user_input1) and user_input2:
                st.latex(r"\text{Veuillez entre le terme général de la série}")
                return jsonify({"messages": out})

            if user_input1 and user_input2:
                n_min = int(user_input2)

                # S_n exactement comme ton code (avec k global)
                S_n = sp.Sum(u.subs(n, k), (k, n_min, n))

                st.latex(r"\text {Vous avez entré la série de somme partielle }" + sp.latex(S_n))
                st.latex(sp.latex(S_n))
                st.latex(r"\text{Considérons donc son terme général de rang n ,} u_n =" + sp.latex(u_n))

                if diverge(u_n, n):
                    lim = sp.limit_seq(u_n, n)
                    if lim is not None:
                        st.latex(r"\lim_{n \to \infty}" + sp.latex(u_n) + " = " + sp.latex(lim) + r"\neq 0")
                        st.latex(r"\text{❌ d'où la série diverge grossièrement .}")
                else:
                    critere(u, n, n_min)
                    graphe(S_n, n, 'blue')
                    graphe(u_n, n, 'red')

        else:
            if user_input1:
                st.latex(r"\text {Vous avez entré la suite définie par }" + r"u_n " + "=" + sp.latex(u))
                u_n = sp.simplify(u)
                lim = sp.limit_seq(u_n, n)

                if lim.is_real:
                    st.latex(r"\lim_{n \to \infty}" + sp.latex(u_n) + " = " + sp.latex(lim))
                    st.latex(r"\text{ d'où cette suite converge.}")
                else:
                    st.latex(r"\lim_{n \to \infty}" + sp.latex(u_n) + " = " + sp.latex(lim))
                    st.latex(r"\text{ d'où cette suite diverge .}")

                graphe(u_n, n, 'blue')

    except (SyntaxError, TypeError, ValueError, Exception) as e:
        st.error("Entrée invalide. Veuillez entrer une expression correcte.")
        st.info(f"Détail technique : {e}")

    return jsonify({"messages": out})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)