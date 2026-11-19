# Maintenance du profil AtomCrtr

Le README visible sur https://github.com/AtomCrtr provient de la racine du dépôt `AtomCrtr/AtomCrtr`.

## Fichiers

- `README.md` : présentation, projets, compétences et parcours.
- `assets/hero.svg` : bannière SVG autonome inspirée d'un terminal ; monogramme `EC` au lieu d'un portrait sans photo.
- `assets/contributions.svg` : calendrier sur 12 mois, mis à jour quotidiennement depuis les données réelles GitHub.
- `scripts/build_hero.py` : générateur de la bannière.
- `scripts/build_contributions.py` : client GraphQL GitHub et générateur du calendrier SVG.
- `.github/workflows/update-contributions.yml` : automatisation de la mise à jour.

## Première synchronisation

Sur GitHub, ouvrir le dépôt **AtomCrtr/AtomCrtr** → **Actions** → **Update profile contribution dashboard** → **Run workflow**.

Le workflow est aussi déclenché par un push qui modifie son script ou le fichier YAML. Ensuite, il s'exécute chaque jour vers 05:23 UTC (planification indicative de GitHub).

Aucun jeton personnel n'est nécessaire : `GITHUB_TOKEN` est fourni automatiquement par GitHub Actions. L'autorisation de pousser les modifications dépend toutefois des paramètres du dépôt : **Settings → Actions → General → Workflow permissions**.

## Utilisation locale

```bash
python scripts/build_hero.py
python scripts/build_contributions.py --offline    # visuel neutre, aucun faux chiffre
GH_TOKEN=... python scripts/build_contributions.py # calendrier réel
python -m unittest discover -s tests
```

Ne jamais publier de jeton dans un dépôt. Les données affichées respectent les paramètres de visibilité du profil GitHub et reflètent ce que l'API expose au workflow.

Les SVG sont autonomes : ils ne téléchargent ni script ni police ni badge externe. Les animations légères du bandeau respectent `prefers-reduced-motion`.