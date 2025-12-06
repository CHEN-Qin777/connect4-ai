# 🎯 Projet Puissance 4 - Intelligence Artificielle

Ce projet implémente le jeu **Puissance 4** avec plusieurs agents intelligents développés en Python utilisant le framework **PettingZoo**. Les agents sont optimisés pour la compétition sur [ML-Arena](https://ml-arena.com/viewcompetition/2).

---

## 🌐 Démonstration en Ligne

**Essayez le jeu maintenant !** 🎮  
- **URL** : https://huggingface.co/spaces/clearlove777qin/connect4-ai-master  
- **Plateforme** : Hugging Face Spaces  
- **Fonctionnalités** : Interface web interactive avec un agent de base  
- **Note** : Cette démo présente une version simplifiée avec un agent standard. Le dépôt complet contient tous les agents avancés.

---

## 🏆 Agents Implémentés

### 1. RandomAgent
- **Stratégie** : Choix aléatoire parmi les coups valides  
- **Utilisation** : Référence de base pour la comparaison  
- **Force** : Aucune stratégie, purement aléatoire

### 2. SmartAgent  
- **Stratégie** : Règles heuristiques simples  
- **Priorités** :  
  1. Victoire immédiate  
  2. Blocage de l'adversaire  
  3. Position centrale  
  4. Coup aléatoire  
- **Force** : Bat systématiquement RandomAgent (>80 % de victoires)

### 3. MinimaxAgent
- **Stratégie** : Algorithme Minimax avec élagage alpha-bêta  
- **Profondeur** : Configurable (3-4 par défaut)  
- **Optimisations** :  
  - Ordonnancement des coups (centre d'abord)  
  - Fonction d'évaluation positionnelle  
- **Force** : Bat SmartAgent, pensée à moyen terme

### 4. AdvancedAgent 🚀 (Agent Principal)
- **Stratégie** : Minimax avancé avec mémorisation  
- **Profondeur** : 6 (optimisé pour 3 secondes/coup)  
- **Caractéristiques uniques** :  
  - **Table de transposition** : Mémorisation des positions  
  - **Détection de suicide** : Évite les coups perdants  
  - **Réaction ultra-rapide** : Vérification des victoires/blocages immédiats  
  - **Ordonnancement intelligent** : Priorité au centre  
- **Optimisations** :  
  - Élagage alpha-bêta amélioré  
  - Fonction d'évaluation agressive  
  - Gestion mémoire efficace  
- **Performance** : Conçu pour MLArena (<3 s/coup, <384 Mo)

### 5. MCTSAgent (Optionnel)
- **Stratégie** : Monte Carlo Tree Search avec simulations intelligentes
- **Tests de constante d'exploration** : C = 0.5, 1.0, 1.41, 2.0 (C = 1.41 optimal)
- **Optimisations** :
  - Simulations intelligentes : Utilisation d'heuristiques au lieu du pur aléatoire
  - Terminaison anticipée : Arrêt de la simulation si le gagnant est clair
- **Avantage** : Pas besoin de fonction d'évaluation complexe
- **Utilisation** : Exploration probabiliste avec guidage heuristique

---

## 📊 Comparaison des Agents

| Agent       | Stratégie    | Profondeur | Temps/Coup | Victoire vs Random |
|-------------|--------------|------------|------------|-------------------|
| Random      | Aléatoire    | –          | < 0,01 s   | 50 %              |
| Smart       | Règles       | 1          | < 0,01 s   | > 80 %            |
| Minimax     | Arbre de jeu | 3–4        | 1–2 s      | > 95 %            |
| **Advanced**| **Minimax++**| **6**      | **2–3 s**  | **100 %**         |
| MCTS        | Simulation   | Variable   | 1–5 s      | > 50 %            |

---

## 🎯 Agent Recommandé pour MLArena

**AdvancedAgent** est spécialement conçu pour la compétition MLArena :

### ✅ Respect des Contraintes
- **Temps** : < 3 secondes par coup  
- **Mémoire** : < 384 Mo  
- **CPU** : Single core

### ✅ Avantages Compétitifs
1. **Profondeur 6** : Anticipation supérieure  
2. **Mémorisation** : Évite les calculs redondants  
3. **Détection suicide** : Évite les pièges évidents  
4. **Optimisations** : Temps de réponse constant

### 🚀 Performance
- Taux de victoire contre RandomAgent : 100 %  
- Taux de victoire contre SmartAgent : 100 %  
- Stabilité : Performances constantes

---

## 🛠 Installation

```bash
# Cloner le dépôt
git clone https://github.com/CHEN-Qin777/connect4-ai.git
cd connect4-ai

# Installer les dépendances
pip install -r requirements.txt
```


