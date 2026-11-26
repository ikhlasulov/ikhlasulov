# Expressive Profile

Renderer: https://github.com/metawka/expressive-profile (MIT).
Configuration: `profile.json`. Update: `.github/workflows/expressive-profile.yml`.
The workflow uses the profile repository's built-in `github.token`, not a
personal token and without access to private repositories.

The generator writes `README.md` and the light/dark SVG cards in `assets/`;
real public GitHub data supplies the statistics.

Two small post-processing steps run after the generator:

- `fix-hero.py` rebuilds the avatar cookie rim from the avatar cut-out, freezes
  it and republishes the hero cards under a `-v2` name so GitHub refreshes its
  image cache;
- `fix-stats.py` recomputes the language shares without HTML/CSS/JavaScript
  and redraws the bar and legend.

Google Sans Flex / Roboto Flex fonts: SIL OFL 1.1. Material Symbols:
Apache-2.0. Icons in `.profile/icons.json` are copied from Google's Material
Symbols rounded set.

## Русский

Профиль собран в Expressive Profile (MIT) и обновляется через GitHub Actions,
используя только встроенный токен репозитория. Личного токена и доступа к
закрытым репозиториям нет. Статистика берётся из публичных данных GitHub.
Оформление меняется через `profile.json`.
