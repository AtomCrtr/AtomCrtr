# Maintenance du profil AtomCrtr

Le profil [AtomCrtr](https://github.com/AtomCrtr) affiche le `README.md` à la racine du dépôt [AtomCrtr/AtomCrtr](https://github.com/AtomCrtr/AtomCrtr).

## Fichiers

- `README.md` contient la présentation, les projets et les compétences.
- `assets/hero.jpg` contient la bannière cartographique. En cas de changement d’image, actualiser aussi le texte alternatif dans le README.
- `assets/contributions.svg` contient le calendrier sur douze mois.
- `scripts/build_contributions.py` génère le calendrier à partir des données GitHub.
- `.github/workflows/update-contributions.yml` lance la mise à jour quotidienne et enregistre le SVG lorsque son contenu évolue.

## Première synchronisation

Dans le dépôt, ouvrir **Actions → Update profile contribution dashboard → Run workflow**. Le workflow se lance aussi lors d’un push qui modifie le script de génération ou son fichier YAML. La planification quotidienne est fixée à 05 h 23 UTC.

GitHub Actions fournit automatiquement le `GITHUB_TOKEN`. La mise à jour dépend de l’autorisation d’écriture de GitHub Actions sur la branche du profil. Les données affichées reflètent la visibilité des contributions pour ce jeton.

## Utilisation locale

```bash
python scripts/build_contributions.py --offline
python -m unittest discover -s tests
```

Le mode hors ligne génère un visuel d’attente. Pour récupérer le calendrier réel localement, définir `GH_TOKEN` dans l’environnement et lancer le script sans option. Garder le jeton hors du dépôt.
