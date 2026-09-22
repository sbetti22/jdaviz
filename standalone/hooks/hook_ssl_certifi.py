import os
import ssl
import sys

# Use certificate from certifi only if cafile could not find by ssl.
if ssl.get_default_verify_paths().cafile is None:
    os.environ['SSL_CERT_FILE'] = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')