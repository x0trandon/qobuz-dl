#!/usr/bin/env python3
"""Store a Qobuz user_auth_token RAW into qobuz-dl's config.ini.

The token is read via getpass so it is never echoed to the terminal.
Run:  python3 set_token.py
"""
import configparser
import getpass
import os

config_file = os.path.join(os.environ["HOME"], ".config", "qobuz-dl", "config.ini")

if not os.path.exists(config_file):
    raise SystemExit(f"Config not found at {config_file}. Run `qobuz-dl -r` once first.")

token = getpass.getpass("Paste your user_auth_token (input hidden): ").strip()
if not token:
    raise SystemExit("No token entered, aborting.")

c = configparser.ConfigParser()
c.read(config_file)
c["DEFAULT"]["password"] = token  # stored RAW, not hashed
with open(config_file, "w") as f:
    c.write(f)

print("Token saved to config.ini. Try: qobuz-dl lucky daft punk discovery")
