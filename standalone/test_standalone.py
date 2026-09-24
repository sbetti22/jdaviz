import re

from playwright.sync_api import Page, expect
import os
import sys
import ssl
import certifi
from astroquery.gaia import Gaia
from astropy import units as u
from astropy.coordinates import SkyCoord
import time
from pathlib import Path


def test_solara_basics(page: Page):

    page.goto("http://localhost:8765/")
    
    page.locator('text=Welcome to Jdaviz!').wait_for()
    
    # # when jdaviz is loaded (button at the top left)
    page.locator('img[alt="Launch Jdaviz"]').click()
    page.screenshot(path="debug1.png")

    # # Find the string text "Source"
    # # 1. Wait for any text block containing "Source" to appear globally
    page.locator(".v-input", has_text="Source").click()
    
    page.screenshot(path="debug2.png")

    print("Dropdown clicked successfully.")


    # # 5. STEP D: Interact with the detached option overlay menu
    # # Vuetify spawns option layouts under the role 'listbox' 
    dropdown_menu = page.get_by_role("listbox")
    dropdown_menu.wait_for(state="visible")

    # # Select your target element "astroquery" from your CLI configuration panel
    target_option = dropdown_menu.get_by_role("option", name="astroquery")
    target_option.wait_for(state="visible")
    target_option.click()
    page.screenshot(path="debug3.png")
    
    print("did it.")

    source = page.get_by_label("Source/Coordinates")
    source.wait_for()
    source.click()
    source.fill("259.37380294, 43.20553169")

    radius_field = page.get_by_label("Radius")
    radius_field.fill("1")

    page.screenshot(path="debug4.png")
        
    print("did it.")

    # # Select Unit to 'deg' (the label in the template is "Unit")
    arcmin = page.locator(".v-input", has_text="Unit").click()
    dropdown_menu = page.get_by_role("listbox")
    dropdown_menu.wait_for(state="visible")
    target_option = dropdown_menu.get_by_role("option", name="arcmin")
    target_option.wait_for(state="visible")
    target_option.click()


    page.screenshot(path="debug5.png")
        
    print("did it.")
    # Set Telescope -> Gaia
    page.locator(".v-input", has_text="Telescope").click()
    dropdown_menu = page.get_by_role("listbox")
    dropdown_menu.wait_for(state="visible")
    target_option = dropdown_menu.get_by_role("option", name="Gaia")
    target_option.wait_for(state="visible")
    target_option.click()


    # Set Max Results to a small number to keep test quick
    max_results = page.get_by_label("Max Results")
    max_results.fill("10")

    page.screenshot(path="debug6.png")
        
    print("did it.")

    # # Click the Query Archive button
    page.locator("text=Query Archive").first.click()
    page.screenshot(path="debug7.png")
            
    print("did it.")

    # # Wait for "Observations" table title to appear in the Query Results section
    observations_locator = page.get_by_text("Select Additional Columns", exact=True)
    observations_locator.scroll_into_view_if_needed()

    observations_locator.wait_for(timeout=60_000)

    page.screenshot(path="debug8.png")
            
    print("did it.")

    page.locator(".v-input", has_text="Format").click()
    dropdown_menu = page.get_by_role("listbox")
    dropdown_menu.wait_for(state="visible")
    target_option = dropdown_menu.get_by_role("option", name="Catalog")
    target_option.wait_for(state="visible")
    target_option.click()


    page.screenshot(path="debug9.png")
            
    print("did it9.")

    impor = page.get_by_role("button", name="Import")
    impor.scroll_into_view_if_needed()
    impor.first.click()

    page.get_by_label("Metadata, mouseover markers, and logger").click()
    page.locator("text=Logger").first.click()

    page.screenshot(path="debug10.png")
            
    print("did it10.")

    regex_pattern = r"(?i)catalog.*sucessfully added",

    loc = page.locator(f"text=/{pat}/")
    loc.first.wait_for(timeout=5_000)
    matched_text = loc.first.inner_text()

    print("Found logger message matching catalog-added pattern:", matched_text)
    assert re.search(r"(?i)catalog", matched_text)

   