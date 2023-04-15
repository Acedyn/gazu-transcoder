import gazu

from gazu_transcoder.ingest.module import extract_gazu_modules


def main():
    EXCLUDED_MODULE_PREFIXES = ["__"]
    extract_gazu_modules(gazu, EXCLUDED_MODULE_PREFIXES)
