import json
import os
from typing import Dict

from app.config import settings

i18ns: Dict[str, Dict[str, str]] = {}


def load_translations():
    files = os.listdir(f"{settings.base_dir}/app/languages")
    for file in files:
        lang_code = file.split(".")[0]
        with open(f"{settings.base_dir}/app/languages/{file}", "r") as f:
            i18ns[lang_code] = json.loads(f.read())

        print(f"Loaded {lang_code} locale")


def i18n(template: str, **kwargs) -> str:
    return i18ns.get(settings.locale, {}).get(template, "").format(**kwargs)


load_translations()
