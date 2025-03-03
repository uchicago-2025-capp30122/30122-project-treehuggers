import pytest
import json
from scripts.google import cached_google_get, clean_google
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
