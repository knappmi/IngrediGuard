"""
Centralized feature flag definitions. Toggle optional functionality by editing the
values below (or by overriding them via environment variables or other config
mechanisms in the future).
"""

# --- OCR ---------------------------------------------------------------
# Set to ``True`` to enable OCR related features like taking pictures of menus
# and extracting text using the OCR.space API. In the default configuration we
# keep this disabled so that the rest of the application can run without the
# additional permissions, screens and dependencies required for OCR.
OCR_ENABLED = False 