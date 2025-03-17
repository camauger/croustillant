# Croustillant - Application de Gestion de Recettes

## Description
Croustillant est une application web Flask qui permet de gérer des recettes de cuisine, de créer une sélection personnalisée et de générer automatiquement des listes de courses basées sur les recettes sélectionnées.

## Fonctionnalités
- Affichage d'une liste de recettes
- Consultation détaillée de chaque recette
- Ajout de nouvelles recettes
- Sélection de recettes favorites
- Génération automatique d'une liste de courses consolidée

## Installation et configuration

### Prérequis
- Python 3.6 ou supérieur
- Flask

### Installation
1. Clonez ou téléchargez ce dépôt
2. Installez les dépendances:
   ```
   pip install flask
   ```

### Configuration de la base de données
1. Initialisez la base de données:
   ```
   python init_db.py
   ```
2. (Optionnel) Pour réinitialiser la base de données:
   ```
   python reset_bd.py
   ```

### Ajout des recettes
Pour ajouter des recettes depuis des fichiers JSON:
1. Placez vos fichiers JSON dans le dossier "recettes_json"
2. Exécutez:
   ```
   python ajout_recettes.py
   ```

## Utilisation
1. Lancez l'application:
   ```
   python app.py
   ```
2. Ouvrez votre navigateur à l'adresse http://localhost:5000

### Navigation
- **Accueil**: Liste de toutes les recettes
- **Ajouter une recette**: Formulaire pour créer une nouvelle recette
- **Ma sélection**: Liste des recettes sélectionnées
- **Liste de courses**: Génération d'une liste de courses basée sur les recettes sélectionnées

## Structure des fichiers
- app.py: Application Flask principale
- init_db.py: Initialisation de la base de données
- reset_bd.py: Réinitialisation de la base de données
- ajout_recettes.py: Script pour ajouter des recettes depuis des fichiers JSON
- maj_recette.py: Script pour mettre à jour une recette existante
- templates/: Dossier contenant les templates HTML
  - base.html: Template de base
  - index.html: Page d'accueil
  - recipe.html: Affichage d'une recette
  - create_recipe.html: Formulaire de création de recette
  - my_list.html: Liste des recettes sélectionnées
  - shopping_list.html: Liste de courses générée
- static/css/: Feuilles de style

## Format des recettes JSON
Les recettes doivent être au format JSON avec la structure suivante:
```json
{
  "titre": "Nom de la recette",
  "temps_preparation": "XX minutes",
  "temps_cuisson": "XX minutes",
  "rendement": "X portions",
  "ingrédients": [
    {
      "nom": "Ingrédient",
      "quantité": X,
      "unité": "unité de mesure"
    }
  ],
  "instructions": [
    "Étape 1",
    "Étape 2"
  ]
}
```

Les ingrédients peuvent aussi être groupés:
```json
"ingrédients": [
  {
    "groupe": "Nom du groupe",
    "liste": [
      {
        "nom": "Ingrédient",
        "quantité": X,
        "unité": "unité de mesure"
      }
    ]
  }
]
```
