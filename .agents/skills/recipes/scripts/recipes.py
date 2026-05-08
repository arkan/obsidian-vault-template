#!/usr/bin/env python3
"""
Recipe Manager — version vault Hermes.

- Stockage : Resources/Recipes/<slug>.md
- Frontmatter snake_case + type: recipe + aliases: []
- Log automatique des mutations dans Areas/Claude/operations-log.md
"""

import argparse
import os
import re
import sys
import random
from datetime import datetime
from pathlib import Path

# Path resolution: script lives at <vault>/.claude/skills/recipes/scripts/recipes.py
SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
RECIPES_DIR = VAULT_ROOT / "Resources" / "Recipes"
OPS_LOG = VAULT_ROOT / "Areas" / "Claude" / "operations-log.md"

# Field order in frontmatter — keep stable for diff readability
FIELD_ORDER = [
    'type', 'aliases', 'url', 'rating', 'tags',
    'prep_time', 'cook_time', 'portions', 'difficulty',
    'favorite', 'created', 'last_used', 'use_count',
]


def slugify(text):
    """Lowercase, strip accents, non-alphanumerics → tirets."""
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def parse_frontmatter(content):
    """Parse minimal YAML frontmatter — handles strings, bools, null, ints, lists."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    fm = {}
    for line in parts[1].strip().split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split(',')
            value = [item.strip().strip('"\'') for item in items if item.strip()]
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value == 'null' or value == '':
            value = None
        elif value.lstrip('-').isdigit():
            value = int(value)
        else:
            value = value.strip('"\'')

        fm[key] = value

    body = parts[2].strip()
    return fm, body


def serialize_value(value):
    if isinstance(value, list):
        return f'[{", ".join(str(v) for v in value)}]'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'null'
    return str(value)


def write_recipe(filepath, frontmatter, body):
    """Re-écrit le fichier en respectant FIELD_ORDER."""
    lines = ['---']
    seen = set()

    for key in FIELD_ORDER:
        if key in frontmatter:
            lines.append(f'{key}: {serialize_value(frontmatter[key])}')
            seen.add(key)

    for key, value in frontmatter.items():
        if key not in seen:
            lines.append(f'{key}: {serialize_value(value)}')

    lines.append('---')
    lines.append('')
    lines.append(body)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        if not body.endswith('\n'):
            f.write('\n')


def load_recipes():
    """Charge toutes les recettes du dossier."""
    recipes = []
    if not RECIPES_DIR.exists():
        return recipes

    for filepath in sorted(RECIPES_DIR.glob('*.md')):
        # Skip the dashboard
        if filepath.name == 'Recipes.md':
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        fm, body = parse_frontmatter(content)
        if fm.get('type') and fm.get('type') != 'recipe':
            continue  # ignore non-recipe files
        title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filepath.stem
        recipes.append({
            'slug': filepath.stem,
            'filepath': filepath,
            'title': title,
            'frontmatter': fm,
            'body': body,
        })
    return recipes


def find_recipe(name, recipes=None):
    """Trouve une recette par slug exact, alias, ou partial match."""
    if recipes is None:
        recipes = load_recipes()
    needle = slugify(name)

    # Exact slug or slugified title
    for r in recipes:
        if r['slug'] == needle or slugify(r['title']) == needle:
            return r
    # Alias match
    for r in recipes:
        for a in r['frontmatter'].get('aliases', []) or []:
            if slugify(a) == needle:
                return r
    # Partial match
    for r in recipes:
        if needle in r['slug'] or needle in slugify(r['title']):
            return r
    return None


def log_op(action, summary, target_path):
    """Append a line to operations-log.md."""
    OPS_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not OPS_LOG.exists():
        with open(OPS_LOG, 'w', encoding='utf-8') as f:
            f.write("---\ntype: claude\n---\n# Operations Log\n\n"
                    "| Date | Type | Skill | Description | Cible |\n"
                    "|------|------|-------|-------------|-------|\n")
    rel_path = target_path.relative_to(VAULT_ROOT) if target_path else ''
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    line = f"| {ts} | {action} | recipes | {summary} | {rel_path} |\n"
    with open(OPS_LOG, 'a', encoding='utf-8') as f:
        f.write(line)


# ─── Commands ──────────────────────────────────────────────────────────────

def cmd_list(args):
    recipes = load_recipes()
    if not recipes:
        print("Aucune recette trouvée.")
        return

    if args.tag:
        recipes = [r for r in recipes
                   if args.tag.lower() in [t.lower() for t in (r['frontmatter'].get('tags') or [])]]
    if args.favorite:
        recipes = [r for r in recipes if r['frontmatter'].get('favorite')]

    if args.sort == 'rating':
        recipes.sort(key=lambda r: r['frontmatter'].get('rating') or 0, reverse=True)
    elif args.sort == 'use_count':
        recipes.sort(key=lambda r: r['frontmatter'].get('use_count') or 0, reverse=True)
    elif args.sort == 'last_used':
        recipes.sort(key=lambda r: r['frontmatter'].get('last_used') or '', reverse=True)
    else:
        recipes.sort(key=lambda r: r['title'].lower())

    print(f"📖 {len(recipes)} recette(s)\n")
    for r in recipes:
        fm = r['frontmatter']
        rating = '⭐' * (fm.get('rating') or 0)
        favorite = '❤️ ' if fm.get('favorite') else ''
        tags = ', '.join(fm.get('tags') or [])
        print(f"• {favorite}{r['title']} {rating}".rstrip())
        if tags:
            print(f"  Tags: {tags}")
        times = []
        if fm.get('prep_time'):
            times.append(f"prep {fm['prep_time']}")
        if fm.get('cook_time'):
            times.append(f"cuisson {fm['cook_time']}")
        if times:
            print(f"  Temps: {', '.join(times)}")
        if fm.get('use_count'):
            print(f"  Utilisée {fm['use_count']}x" + (f" (dernier: {fm.get('last_used')})" if fm.get('last_used') else ""))
        print()


def cmd_search(args):
    recipes = load_recipes()
    term = args.term.lower()

    results = []
    for r in recipes:
        body_low = r['body'].lower()
        title_low = r['title'].lower()
        tags_low = [t.lower() for t in (r['frontmatter'].get('tags') or [])]
        aliases_low = [a.lower() for a in (r['frontmatter'].get('aliases') or [])]
        if (term in title_low or term in body_low or
                any(term in t for t in tags_low) or
                any(term in a for a in aliases_low)):
            results.append(r)

    if not results:
        print(f"Aucune recette pour '{args.term}'")
        return

    print(f"🔍 {len(results)} résultat(s) pour '{args.term}'\n")
    for r in results:
        tags = ', '.join(r['frontmatter'].get('tags') or [])
        print(f"• {r['title']}  ({r['slug']})")
        if tags:
            print(f"  Tags: {tags}")
        print()


def cmd_show(args):
    recipe = find_recipe(args.name)
    if not recipe:
        print(f"Recette '{args.name}' non trouvée.")
        sys.exit(1)

    fm = recipe['frontmatter']
    print('=' * 50)
    print(recipe['body'])
    print('=' * 50)
    print()
    if fm.get('url'):
        print(f"🔗 Source: {fm['url']}")
    if fm.get('rating'):
        print(f"⭐ Note: {'⭐' * fm['rating']} ({fm['rating']}/5)")
    if fm.get('tags'):
        print(f"🏷️ Tags: {', '.join(fm['tags'])}")
    times = []
    if fm.get('prep_time'):
        times.append(f"prépa {fm['prep_time']}")
    if fm.get('cook_time'):
        times.append(f"cuisson {fm['cook_time']}")
    if times:
        print(f"⏱️ Temps: {', '.join(times)}")
    if fm.get('portions'):
        print(f"👥 Portions: {fm['portions']}")
    if fm.get('difficulty'):
        print(f"📊 Difficulté: {fm['difficulty']}")
    if fm.get('use_count'):
        print(f"📈 Utilisée: {fm['use_count']}x")
    if fm.get('last_used'):
        print(f"📅 Dernière utilisation: {fm['last_used']}")
    print(f"📁 {recipe['filepath'].relative_to(VAULT_ROOT)}")


def cmd_add(args):
    slug = slugify(args.name)
    filepath = RECIPES_DIR / f"{slug}.md"
    if filepath.exists():
        print(f"La recette '{args.name}' existe déjà ({filepath.relative_to(VAULT_ROOT)})")
        sys.exit(1)

    fm = {
        'type': 'recipe',
        'aliases': [],
        'url': args.url or None,
        'rating': None,
        'tags': args.tags.split(',') if args.tags else [],
        'prep_time': args.prep_time or None,
        'cook_time': args.cook_time or None,
        'portions': int(args.portions) if args.portions else None,
        'difficulty': args.difficulty or None,
        'favorite': False,
        'created': datetime.now().strftime('%Y-%m-%d'),
        'last_used': None,
        'use_count': 0,
    }
    body = (
        f"# {args.name}\n\n"
        "## Ingrédients\n- \n\n"
        "## Préparation\n1. \n\n"
        "## Notes\n"
    )
    write_recipe(filepath, fm, body)
    log_op('create', f"add: {args.name}", filepath)
    print(f"✅ Recette créée: {filepath.relative_to(VAULT_ROOT)}")
    print(f"   Édite le fichier pour ajouter ingrédients et préparation.")


def cmd_used(args):
    recipe = find_recipe(args.name)
    if not recipe:
        print(f"Recette '{args.name}' non trouvée.")
        sys.exit(1)
    fm = recipe['frontmatter']
    fm['use_count'] = (fm.get('use_count') or 0) + 1
    fm['last_used'] = datetime.now().strftime('%Y-%m-%d')
    write_recipe(recipe['filepath'], fm, recipe['body'])
    log_op('update', f"used: {recipe['title']} ({fm['use_count']}x)", recipe['filepath'])
    print(f"✅ {recipe['title']} marquée cuisinée ({fm['use_count']}x, last: {fm['last_used']})")


def cmd_rate(args):
    rating = int(args.rating)
    if not 1 <= rating <= 5:
        print("La note doit être entre 1 et 5.")
        sys.exit(1)
    recipe = find_recipe(args.name)
    if not recipe:
        print(f"Recette '{args.name}' non trouvée.")
        sys.exit(1)
    recipe['frontmatter']['rating'] = rating
    write_recipe(recipe['filepath'], recipe['frontmatter'], recipe['body'])
    log_op('update', f"rate: {recipe['title']} → {rating}⭐", recipe['filepath'])
    print(f"✅ {recipe['title']} notée {'⭐' * rating}")


def cmd_favorite(args):
    recipe = find_recipe(args.name)
    if not recipe:
        print(f"Recette '{args.name}' non trouvée.")
        sys.exit(1)
    fm = recipe['frontmatter']
    fm['favorite'] = not fm.get('favorite', False)
    write_recipe(recipe['filepath'], fm, recipe['body'])
    status = "❤️ favorite" if fm['favorite'] else "💔 retirée des favoris"
    log_op('update', f"favorite toggle: {recipe['title']} → {fm['favorite']}", recipe['filepath'])
    print(f"{recipe['title']} {status}")


def cmd_delete(args):
    recipe = find_recipe(args.name)
    if not recipe:
        print(f"Recette '{args.name}' non trouvée.")
        sys.exit(1)
    title = recipe['title']
    path = recipe['filepath']
    path.unlink()
    log_op('delete', f"delete: {title}", path)
    print(f"🗑️ Recette '{title}' supprimée.")


def cmd_random(args):
    recipes = load_recipes()
    if args.tag:
        recipes = [r for r in recipes
                   if args.tag.lower() in [t.lower() for t in (r['frontmatter'].get('tags') or [])]]
    if not recipes:
        print("Aucune recette trouvée.")
        return
    recipe = random.choice(recipes)
    args.name = recipe['slug']
    cmd_show(args)


def cmd_edit(args):
    recipe = find_recipe(args.name)
    if not recipe:
        print(f"Recette '{args.name}' non trouvée.")
        sys.exit(1)
    fm = recipe['frontmatter']
    print(f"📝 Édition de **{recipe['title']}**\n")
    print("**Métadonnées :**")
    for k in FIELD_ORDER:
        v = fm.get(k)
        print(f"  {k}: {serialize_value(v) if v is not None else '*(non défini)*'}")
    print(f"\n📁 Fichier : `{recipe['filepath'].relative_to(VAULT_ROOT)}`")
    print("\n**Que veux-tu modifier ?**")


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Gestionnaire de recettes (vault Hermes)')
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('list', help='Liste les recettes')
    p.add_argument('--tag')
    p.add_argument('--favorite', action='store_true')
    p.add_argument('--sort', choices=['rating', 'use_count', 'last_used'])

    p = sub.add_parser('search', help='Recherche')
    p.add_argument('term')

    p = sub.add_parser('show', help='Affiche une recette')
    p.add_argument('name')

    p = sub.add_parser('add', help='Ajoute une recette')
    p.add_argument('name')
    p.add_argument('--url')
    p.add_argument('--tags', help='Tags séparés par virgule')
    p.add_argument('--prep-time', dest='prep_time')
    p.add_argument('--cook-time', dest='cook_time')
    p.add_argument('--portions')
    p.add_argument('--difficulty', choices=['facile', 'moyen', 'difficile'])

    p = sub.add_parser('used', help='Marque comme cuisinée')
    p.add_argument('name')

    p = sub.add_parser('rate', help='Note une recette')
    p.add_argument('name')
    p.add_argument('rating')

    p = sub.add_parser('favorite', help='Toggle favorite')
    p.add_argument('name')

    p = sub.add_parser('delete', help='Supprime une recette')
    p.add_argument('name')

    p = sub.add_parser('random', help='Recette aléatoire')
    p.add_argument('--tag')

    p = sub.add_parser('edit', help='Affiche métadonnées pour édition')
    p.add_argument('name')

    args = parser.parse_args()

    handlers = {
        'list': cmd_list, 'search': cmd_search, 'show': cmd_show, 'add': cmd_add,
        'used': cmd_used, 'rate': cmd_rate, 'favorite': cmd_favorite,
        'delete': cmd_delete, 'random': cmd_random, 'edit': cmd_edit,
    }
    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        sys.exit(1)
    handler(args)


if __name__ == '__main__':
    main()
