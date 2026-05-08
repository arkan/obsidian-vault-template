---
name: resume
description: >
  Synthétise des documents longs (PDF, Markdown, URL) en résumés concis en français.
  Utilise un découpage hiérarchique par table des matières avec sous-agents parallèles
  pour traiter des centaines de pages sans perte de contexte. Use when user wants to
  summarize a long document, says "résume ce rapport", "fais une synthèse de ce
  document", "donne-moi l'essentiel", "que dit ce PDF", or mentions /resume. Triggers
  on any request to summarize, synthesize, or extract key points from reports,
  commission reports, white papers, or long-form content.
argument_hint: "<fichier|url> [--words N] [--detailed|--concise] [--lang en]"
---

# resume — Synthèse de documents longs

Synthèse hiérarchique avec sous-agents parallèles. Stratégie B (table des matières) avec fallback A (taille fixe).

## Paramètres

| Paramètre | Effet |
|-----------|-------|
| `<source>` | Chemin PDF/Markdown ou URL |
| `--words N` | Longueur cible en mots (défaut : ~500) |
| `--detailed` | Résumé long (~1000 mots) |
| `--concise` | Résumé court (~250 mots) |
| `--lang en` | Langue de sortie (défaut : fr) |

## Workflow

### 1. Obtenir le texte

- **URL HTML** → `webfetch` avec `extract_main: true`
- **URL PDF** → `curl -L <url> -o /tmp/resume-input.pdf`
- **PDF local** → `python3 .claude/skills/resume/scripts/extract_pdf.py <pdf> > /tmp/resume-extracted.json`
- **Markdown** → lecture directe avec Read

Le script produit un JSON : `{text, toc: [{title, page, level}], pages}`.

### 2. Détecter la structure et découper

**Si table des matières disponible (Stratégie B)** :
- Regrouper les entrées ToC en chunks de ~12K tokens max
- Chaque chunk = une ou plusieurs sections contiguës
- Conserver les titres comme en-tête de chunk

**Si pas de ToC (Stratégie A, fallback automatique)** :
- Découper le texte en blocs de ~12K tokens
- Chevauchement de 200 tokens entre blocs

**Si < 2 pages** → résumé direct, pas de chunking.

### 3. Résumer les chunks en parallèle

Lancer un sous-agent par chunk avec cette consigne :

```
Résume le texte suivant en {langue}. Capture :
- Les faits et constats principaux
- Les chiffres et données clés
- Les conclusions et recommandations
- Le contexte essentiel

Longueur : {1-2% de la taille du chunk, max 800 mots}.
```

Collecter tous les résumés. Utiliser le modèle le moins cher capable de résumer correctement pour les chunks.

### 4. Synthèse finale

Avec tous les résumés de chunks assemblés, produire la synthèse définitive :

- **Langue** : français par défaut, celle demandée via `--lang`
- **Longueur** : selon `--words`, `--detailed`, ou `--concise`
- **Format** : libre, structuré naturellement selon le contenu
- Prioriser : conclusions, implications, controverses si présentes

Utiliser le modèle principal pour cette étape.

### 5. Écrire la sortie

Créer le fichier dans `Resources/` avec ce frontmatter :

```yaml
type: summary
source: "<url ou chemin>"
source_type: <pdf|markdown|url>
lang: <fr|en>
tags: [summary]
created: <YYYY-MM-DD>
```

Afficher le résumé dans le chat, puis confirmer le chemin : `Résumé sauvegardé : Resources/<slug>.md`.

## Gestion d'erreurs

| Cas | Action |
|-----|--------|
| PDF sans texte (scan) | Message : "Ce PDF est un scan sans OCR. Utilise un outil d'OCR d'abord." |
| URL inaccessible | Afficher le code HTTP, arrêter |
| Document sans ToC | Fallback silencieux en Stratégie A |
| Document < 2 pages | Résumé direct sans chunking |
| pymupdf absent | Message : `pip install pymupdf` |
| Chunk > 12K tokens | Re-découpage récursif de ce chunk |

## Notes

- Texte extrait → `/tmp/`, nettoyé après usage
- Toujours inclure la source exacte dans le frontmatter
- Slug du fichier = titre du document en kebab-case
- Pour les URLs, `webfetch` avec `prefer_llms_txt: auto` par défaut
