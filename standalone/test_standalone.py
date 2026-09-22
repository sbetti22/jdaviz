import re

from playwright.sync_api import Page, expect
import os
import sys
import ssl
import certifi
from astroquery.gaia import Gaia
from astropy import units as u
from astropy.coordinates import SkyCoord


def test_solara_basics(page: Page):
    page.goto("http://localhost:8765/")

    # when jdaviz is loaded (button at the top left)
    page.locator("text=Welcome to Jdaviz").wait_for()


def _ensure_certifi_cafile():
    """
    Ensure a usable CA bundle is available at runtime.
    Prefer a certifi bundle extracted by PyInstaller (sys._MEIPASS) when frozen,
    otherwise fall back to the installed certifi.
    Do not override an explicitly set SSL_CERT_FILE.
    """
    cafile = None
    if getattr(sys, "frozen", False):
        candidate = os.path.join(sys._MEIPASS, "certifi", "cacert.pem")
        if os.path.exists(candidate):
            cafile = candidate

    if cafile is None:
        cafile = certifi.where()

    os.environ.setdefault("SSL_CERT_FILE", cafile)

    print("SSL_CERT_FILE:", os.environ.get("SSL_CERT_FILE"))
    print("ssl.get_default_verify_paths():", ssl.get_default_verify_paths())


def test_astroquery_gaia_can_query():
    """
    Simple runtime test: run a small Gaia ADQL query and ensure we get results.
    This prefers a bundled certifi cacert.pem when running from a PyInstaller app
    (so the frozen app can verify TLS).
    """
    _ensure_certifi_cafile()

    Gaia.ROW_LIMIT = 10

    skycoord_center = SkyCoord(259.37380294, 43.20553169, unit='deg')
    radius = 5 * u.arcmin

    try:
        output = Gaia.query_object(skycoord_center, radius=radius)
    except Exception as e:
        ssl_paths = ssl.get_default_verify_paths()
        raise RuntimeError(
            "Gaia query failed. SSL_CERT_FILE=%r, ssl.get_default_verify_paths()=%r, exception=%s"
            % (os.environ.get("SSL_CERT_FILE"), ssl_paths, e)
        ) from e

    assert len(output) > 0, "Gaia query returned no rows; check network/endpoint and CA bundle"

    print(output[:1])