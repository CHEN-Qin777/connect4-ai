# Plan de Test pour l'Agent Puissance 4

## 1. Que tester ?

### Tests Fonctionnels
- [x] Sélection de coup valide : l'agent ne joue que dans des colonnes non pleines
- [x] Respect du masque d'action : l'utilise correctement pour déterminer les coups valides
- [x] Gestion de la fin de partie : ne pas jouer si la partie est terminée
- [x] Détection de victoire : reconnaître quand il peut gagner
- [x] Détection de blocage : reconnaître quand il doit bloquer l'adversaire

### Tests de Performance
- [ ] Temps par coup : moins de 3 secondes par coup
- [ ] Utilisation de la mémoire : moins de 384 Mo
- [ ] Stabilité : pas de fuites de mémoire après plusieurs parties

### Tests Stratégiques
- [ ] Gagne contre un agent aléatoire : taux de victoire > 80%
- [ ] Bloque les menaces évidentes : dans des scénarios prédéfinis
- [ ] Prend les victoires immédiates : dans des scénarios prédéfinis

## 2. Comment tester ?

### Coups valides
- Créer des plateaux avec certaines colonnes pleines et vérifier que l'agent ne choisit que des colonnes valides.

### Taux de victoire
- Jouer N parties contre l'agent aléatoire et calculer le pourcentage de victoires.

### Tournoi
- Faire jouer plusieurs agents (RandomAgent, SmartAgent, etc.) dans un tournoi round-robin.

### Performance
- Utiliser `time.time()` pour mesurer le temps de décision.
- Utiliser `tracemalloc` pour mesurer l'utilisation de la mémoire.

## 3. Critères de Succès

Pour l'agent intelligent (SmartAgent) :
- Taux de victoire contre RandomAgent > 80% sur 100 parties
- Temps moyen par coup < 0.1 secondes
- Utilisation de mémoire < 10 MB

Pour l'agent avancé (MinimaxAgent, optionnel) :
- Taux de victoire contre SmartAgent > 70% sur 50 parties
- Temps moyen par coup < 3 secondes (contrainte MLArena)

## 4. Scénarios de Test

### Scénario 1 : Détecter une victoire immédiate
État du plateau :
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
X X X . . . . <- Ligne du bas, 3 alignés

Attendu : L'agent joue la colonne 3 pour gagner

### Scénario 2 : Bloquer la victoire de l'adversaire
État du plateau :
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
O O O . . . . <- L'adversaire a 3 alignés

Attendu : L'agent joue la colonne 3 pour bloquer

### Scénario 3 : Préférence pour le centre
État du plateau :
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . . <- Plateau vide

Attendu : L'agent joue la colonne 3 (centre)

### Scénario 4 : Éviter les colonnes pleines
État du plateau :
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
X . . . . . .
X . . . . . . <- Colonne 0 pleine

Attendu : L'agent ne joue pas la colonne 0

### Scénario 5 : Victoire en diagonale
État du plateau :
. . . . . . .
. . . . . . .
. . . X . . .
. . X O . . .
. X O O . . .
X O O X . . . <- Diagonale descendante

Attendu : L'agent (X) joue la colonne 3 pour gagner (alignement diagonal)

## 5. Plan d'Exécution

1. Exécuter les tests unitaires pour chaque agent
2. Exécuter les tests de performance
3. Exécuter le tournoi entre agents
4. Générer un rapport de test
