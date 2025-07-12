import csv
from io import StringIO
import logging

try:
    from kivy.logger import Logger
except ImportError:
    Logger = logging.getLogger(__name__)

import sys
from utils.error_handler import error_handler

@error_handler
def parse_menu_file(path):
    Logger.info(f"MenuParser: Parsing menu file from path -- {path}")
    with open(path, newline='', encoding='utf-8') as f:
        return parse_menu_stream(f)

@error_handler
def parse_menu_stream(stream):
    Logger.critical("MenuParser: Entered parse_menu_stream")

    try:
        if hasattr(stream, "seek"):
            stream.seek(0)
        if hasattr(stream, "getvalue"):
            Logger.critical(f"MenuParser: Stream content:\n{stream.getvalue()}")

        reader = csv.DictReader(stream)
        Logger.critical(f"MenuParser: Headers: {reader.fieldnames}")

        menu_data = []
        for row in reader:
            Logger.critical(f"MenuParser: Row: {row}")
            # Process ingredients into a list if they're comma-separated
            ingredients = row['ingredients'].split(',') if isinstance(row['ingredients'], str) else row['ingredients']
            ingredients = [ing.strip() for ing in ingredients]
            menu_data.append({
                'item': row['item'].strip(),
                'ingredients': ingredients
            })

        return menu_data
    except Exception as e:
        Logger.critical(f"MenuParser: Exception: {e}")
        raise

