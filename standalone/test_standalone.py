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

    # Click the "Launch Jdaviz" image (has title="Launch Jdaviz" in launcher.vue)
    page.locator("img[title='Launch Jdaviz']").first.click()

    page.locator("text=Viewer").wait_for(timeout=15_000)

    page.locator("text=Astroquery").first.click()

    page.locator("text=Input").wait_for(timeout=10_000)

    source = page.get_by_label("Source/Coordinates").click()
    source.fill("259.37380294, 43.20553169")

    radius_field = page.get_by_label("Radius")
    radius_field.fill("1")

    # Select Unit to 'deg' (the label in the template is "Unit")
    page.get_by_label("arcmin").click()
    # choose 'deg' (change if different units are shown)
    page.locator("text=arcmin").first.click()

    # Set Telescope -> Gaia
    page.get_by_label("Telescope").click()
    page.locator("text=Gaia").first.click()

    # Set Max Results to a small number to keep test quick
    max_results = page.get_by_label("Max Results")
    max_results.fill("10")

    # Click the Query Archive button
    page.locator("text=Query Archive").first.click()

    # Wait for "Observations" table title to appear in the Query Results section
    observations_locator = page.locator("text=Select Additional Columns")
    observations_locator.wait_for(timeout=60_000)

    page.get_by_label("Format").click()
    page.locator("text=Catalog").first.click()

    page.get_by_label("Viewer").click()
    page.locator("text=Table").first.click()

    page.locator("text=Import").first.click()


    page.locator("img[title='Launch Jdaviz']").first.click()

    page.locator("img[src*='information-outline.svg']").first.click()

    page.locator("text=Logger").first.click()

    regex_pattern = r"(?i)catalog.*sucessfully added",

    loc = page.locator(f"text=/{pat}/")
    loc.first.wait_for(timeout=5_000)
    matched_text = loc.first.inner_text()

    print("Found logger message matching catalog-added pattern:", matched_text)
    assert re.search(r"(?i)catalog", matched_text)

   