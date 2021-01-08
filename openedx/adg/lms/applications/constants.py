"""
Constants related to applications.
"""
from datetime import datetime

MINIMUM_YEAR_OPTION = 1900
MAXIMUM_YEAR_OPTION = datetime.today().year
LOGO_IMAGE_MAX_SIZE = 200 * 1024
ALLOWED_LOGO_EXTENSIONS = ('png', 'jpg', 'svg')
MAXIMUM_AGE_LIMIT = 60
MINIMUM_AGE_LIMIT = 21
RESUME_FILE_MAX_SIZE = 4 * 1024 * 1024
