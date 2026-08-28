# qobuz-dl — local setup notes

This clone is **patched** to work around Qobuz killing the old email/password
login API. Read this before touching auth or when downloads stop working.

## Why it's patched

Qobuz disabled the direct `user/login` email+password endpoint (moved to
OAuth + reCAPTCHA). Upstream `vitiko98/qobuz-dl` is unmaintained and now fails
with `AuthenticationError: Invalid credentials` for everyone — it is **not** a
bad-password problem.

Fix (per upstream issue #329): `qobuz_dl/qopy.py` `auth()` was rewritten to log
in with a **browser `user_auth_token`** instead of email/password. The token is
stored RAW in `config.ini`'s `password` field, refreshed each run via
`extra=partner`, and auto-saved back. Original is backed up at
`qobuz_dl/qopy.py.orig.bak`.

## Requirements

- An **active PAID Qobuz subscription** (Studio plan). Free accounts
  (`Membership: Qobuz Member`) only return 30-sec demos → every track logs
  `Demo. Skipping` and nothing downloads. Paid shows `Membership: Studio`.

## Get / refresh the token (do this when login starts failing)

The token is a JWT and expires after hours/days. To grab a fresh one:

1. Log into **play.qobuz.com** in a browser and play any track.
2. Open DevTools (Cmd+Opt+I) → **Network** tab → filter box: `api.json`.
3. Click any request → **Headers** → **Request Headers** → copy the value of
   **`x-user-auth-token`**.
   (Alternatives: a `user_auth_token=` query param on those requests, or
   DevTools → Application/Storage → Local Storage / Cookies for play.qobuz.com.)
4. Store it (input stays hidden, never echoed):
   ```
   python3 set_token.py
   ```
   Do **NOT** use `qobuz-dl -r` to enter the token — `cli.py` MD5-hashes the
   password field, which destroys a token.

## Usage

```
# search + grab top result (full album)
qobuz-dl lucky <search terms>

# download by URL (album / track / playlist / artist / label)
qobuz-dl dl https://play.qobuz.com/album/<id>

# interactive browse/select
qobuz-dl fun -l 15
```

## Where downloads land

`default_folder` in `config.ini` supports date tokens, expanded at run time:

```
default_folder = ~/audio/library/{year}
```

`{year}` / `{month}` / `{day}` are the **download** date, so the folder rolls
over on its own each January -- no yearly hand-edit. (Don't confuse this with
`folder_format`'s `{year}`, which is the album's *release* year.)

strftime codes like `%Y` do **not** work here: `%` is interpolation syntax to
configparser, so `cli.py` errors out reading a config that contains one.
Expansion lives in `utils.expand_directory`, applied only to the configured
root -- never to album or playlist names, which can contain a literal `{`.

Useful flags:
- `-q 6` CD lossless 16/44.1 · `-q 7` 24-bit ≤96kHz · `-q 27` max hi-res
  (default here is 27; you get the highest the track actually has)
- `-d "Crate name"` custom output folder
- `--embed-art` bake cover art into the files (otherwise saved as cover.jpg)
- `--no-db` re-download something already in the local "downloaded IDs" database
  (the DB records an ID even if a prior attempt only skipped demos)

## Files added/changed in this clone (not upstream)

- `qobuz_dl/qopy.py` — token-auth patch (backup: `qobuz_dl/qopy.py.orig.bak`)
- `qobuz_dl/utils.py` — `expand_directory()` for `{year}` folder tokens
- `qobuz_dl/core.py` — blank-line fix in the `-f` text-file reader; download
  root now goes through `expand_directory()`
- `set_token.py` — helper to store the token raw into config.ini
- `NOTES.md` — this file
