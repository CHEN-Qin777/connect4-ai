# Stratégie de l'Agent Intelligent

## Classement des Priorités

L'agent vérifie les règles dans l'ordre suivant :

1. **Victoire immédiate** : Si je peux gagner en un coup, je joue ce coup
2. **Blocage défensif** : Si l'adversaire peut gagner au prochain coup, je le bloque
3. **Position centrale** : Je privilégie les colonnes centrales pour plus d'options stratégiques
4. **Aléatoire** : Si aucune règle ci-dessus ne s'applique, je joue aléatoirement

## Règles Essentielles

### 1. Détection de Victoire Immédiate
- Vérifier chaque colonne valide pour voir si y jouer crée un alignement de 4
- Vérifier les 4 directions : horizontale, verticale, diagonale montante, diagonale descendante

### 2. Détection de Blocage Nécessaire
- Simuler le prochain coup de l'adversaire dans chaque colonne valide
- Si l'adversaire peut gagner, bloquer cette colonne

### 3. Préférence pour le Centre
- Colonne 3 (centre) > colonnes 2 et 4 > colonnes 1 et 5 > colonnes 0 et 6
- Le centre offre plus d'opportunités d'alignement

## Règles Souhaitables (Améliorations Futures)

### 1. Détection des Menaces Doubles
- Identifier les situations où un coup crée deux menaces de victoire simultanément
- Une menace double est imparable car l'adversaire ne peut bloquer qu'une menace

### 2. Construction d'Alignements
- Privilégier les coups qui construisent des alignements de 2 ou 3 pièces
- Éviter les coups qui aident l'adversaire à se développer

### 3. Positionnement Stratégique
- Contrôler le centre du plateau
- Créer des opportunités multiples tout en limitant celles de l'adversaire

## Décomposition de l'Algorithme
choose_action()
├── _get_valid_actions() - Obtenir les colonnes jouables
├── _find_winning_move() - Vérifier si je peux gagner immédiatement
├── _find_winning_move(adversaire) - Vérifier si je dois bloquer
├── evaluate_position() - Évaluer les positions stratégiques (amélioration future)
└── fallback_move() - Choix par défaut (centre ou aléatoire) 

## Justification des Choix

### Pourquoi vérifier la victoire avant le blocage ?
Si j'ai l'opportunité de gagner immédiatement, je dois la prendre plutôt que de bloquer l'adversaire. La victoire assure la partie, le blocage ne fait que la prolonger.

### Pourquoi privilégier le centre ?
Les colonnes centrales offrent plus de possibilités d'alignement dans toutes les directions. Statistiquement, les coups au centre mènent à plus de victoires.

### Complexité de la Détection de Victoire
La détection de victoire vérifie 4 directions depuis chaque position possible, ce qui donne une complexité raisonnable pour un plateau 6x7.
