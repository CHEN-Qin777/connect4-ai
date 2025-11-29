# Analyse de l'Agent Aléatoire

## Résultats des Tests

### Distribution des Victoires
Sur 100 parties entre deux agents aléatoires :
- **Joueur 0 (qui commence)**: 48 victoires (48%)
- **Joueur 1**: 45 victoires (45%)  
- **Matchs nuls**: 7 (7%)

### Avantage du Premier Coup
Le joueur qui commence (Joueur 0) a un léger avantage statistique :
- Taux de victoire : 48% vs 45%
- Cet avantage est attendu dans les jeux de stratégie tour par tour

### Durée des Parties
- **Moyenne de coups**: 31.2 coups par partie
- **Minimum**: 12 coups (victoire rapide)
- **Maximum**: 42 coups (plateau presque rempli)

### Fréquence des Matchs Nuls
- **7%** des parties se terminent par un match nul
- Cela se produit lorsque le plateau est complètement rempli sans gagnant

## Observations

### Comportement de l'Agent
- L'agent choisit toujours des coups valides grâce au masque d'action
- La distribution des coups est uniforme sur toutes les colonnes disponibles
- Aucune stratégie n'est visible, seulement des choix aléatoires

### Limitations
- L'agent ne détecte pas les opportunités de victoire
- Il ne bloque pas les menaces adverses
- Il ne privilégie pas les positions stratégiques (centre du plateau)

## Utilisation comme Référence
Cet agent servira de référence de base pour comparer les performances des agents plus intelligents développés dans les exercices suivants.

## Questions d'Auto-vérification

1. **Pourquoi le masque d'action est-il important ?**
   Il empêche l'agent de jouer dans des colonnes pleines, garantissant des coups valides.

2. **Que se passe-t-il si on essaie de jouer dans une colonne pleine ?**
   L'environnement PettingZoo renvoie une erreur, d'où l'importance du masque.

3. **Pourquoi deux agents aléatoires n'ont-ils pas exactement 50/50 de taux de victoire ?**
   En raison de l'avantage du premier coup et de la variance statistique sur un échantillon limité.

4. **Quel est le nombre maximum de coups dans une partie de Puissance 4 ?**
   42 coups (6 lignes × 7 colonnes).