import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
import time
import random
import re
import json

#cd C:\Users\Daniela\Programming\Python\test_NAD
# streamlit run web_app_01.py

def fetch_html(url):
    """Holt den HTML-Code einer Webseite."""
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abruf von {url}: {e}")
        return None


def analyze_html(html):
    """Analysiert eine Webseite nach künstlerischen oder konventionellen Merkmalen und gibt die Punkte aus."""
    soup = BeautifulSoup(html, 'html.parser')

    found_features = {"artistic": [], "conventional": []}

    # --- Suchkriterien für künstlerische Webseiten ---
    artistic_features = 0

    # Ungewöhnliche HTML-Elemente
    if soup.find_all(['frameset', 'iframe']):  # Verwendung von Frames für Layout oder Navigation
        artistic_features += 2
        found_features["artistic"].append("Uses frameset or iframe")
    if soup.find_all(['marquee', 'blink']):  # Blinken oder bewegter Text (veraltet, aber künstlerisch genutzt)
        artistic_features += 1
        found_features["artistic"].append("Blinking or scrolling text")
    if soup.find_all(['xmp', 'listing', 'plaintext']):  # Veraltete Code- und Plaintext-Darstellung
        artistic_features += 2
        found_features["artistic"].append("Deprecated code or plaintext elements")
    if soup.find_all(['isindex', 'keygen', 'command']):  # Seltene Hypertext-Elemente
        artistic_features += 1
        found_features["artistic"].append("Rare HTML elements (isindex, keygen, command)")

    # Multimedia- und interaktive Inhalte
    if soup.find_all(['canvas', 'embed', 'audio', 'video']):  # Nutzung von Multimedia-Elementen
        artistic_features += 2
        found_features["artistic"].append("Includes multimedia elements")
    if soup.find_all(['applet', 'noembed', 'param']):  # Veraltete oder alternative Medieneinbindungen
        artistic_features += 2
        found_features["artistic"].append("Uses deprecated or alternative media embedding")
    if soup.find_all('a', href=True, recursive=True) and soup.find_all('img'):  # Kombination aus Bildern & Links
        artistic_features += 2
        found_features["artistic"].append("Combination of images & links")
    if soup.find_all('img', src=re.compile(r'\.gif$', re.IGNORECASE)):  # GIFs als gestalterisches Mittel
        artistic_features += 2
        found_features["artistic"].append("GIF images used")
    if not soup.find(['nav', 'header', 'footer']):  # Keine klassische Navigation
        artistic_features += 2
        found_features["artistic"].append("No traditional navigation structure")

    # Dynamische Effekte und Navigation
    if re.search(r'window\.location\.href|setTimeout', html):  # Dynamische Navigation oder Umleitungen
        artistic_features += 2
        found_features["artistic"].append("Uses dynamic navigation or timed effects")
    if re.search(r'document\.write|innerHTML', html):  # Direkte HTML-Manipulation durch JavaScript
        artistic_features += 2
        found_features["artistic"].append("Direct HTML manipulation via JavaScript")
    if re.search(r'setTimeout|setInterval', html):  # Verzögerte oder wiederholte Skriptaktionen
        artistic_features += 2
        found_features["artistic"].append("Uses delayed or looping script actions")
    if re.search(r'onmousemove|onkeydown|onkeyup', html):  # Interaktive Nutzersteuerung
        artistic_features += 2
        found_features["artistic"].append("Interactive user input triggers effects")
    if re.search(r'Math\.random', html):  # Zufallsgesteuerte Inhalte
        artistic_features += 2
        found_features["artistic"].append("Uses randomization in content")

    # Typografie und Layout
    if re.search(r'position:\s*absolute', html):  # Absolute Positionierung für individuelles Layout
        artistic_features += 2
        found_features["artistic"].append("Manual layout using absolute positioning")
    if re.search(r'font-family:\s*(monospace|cursive|fantasy)', html):  # Ungewöhnliche Schriftarten
        artistic_features += 1
        found_features["artistic"].append("Unconventional fonts used")
    if re.search(r'color:\s*(#[0-9A-Fa-f]{3,6}|rgba?\(.*?\)|hsl\(.*?\))', html):  # Experimentelle Farbgestaltung
        artistic_features += 1
        found_features["artistic"].append("Experimental color scheme detected")
    if soup.find_all(['spacer', 'rb', 'rtc']):  # Ungewöhnliche Formatierungselemente
        artistic_features += 1
        found_features["artistic"].append("Unconventional formating elements")

    # JavaScript-basierte Manipulationen
    if re.search(r'script_type-retype\.js', html, re.IGNORECASE):  # Dynamische Typografie & Animationen
        artistic_features += 2
        found_features["artistic"].append("Dynamic typography and animation")
    if re.search(r'--font-size|--backgroundHover', html, re.IGNORECASE):  # CSS-Variablen für dynamische Gestaltung
        artistic_features += 1
        found_features["artistic"].append("CSS-variables for dynamic design")

    # --- Ausschlusskriterien für konventionelle Webseiten ---
    conventional_features = 0

    # Klassische Navigation & Strukturen
    if soup.find(['nav', 'header', 'footer']) or soup.find(class_=re.compile(r'menu|navigation|navbar', re.IGNORECASE)):
        conventional_features += 2
        found_features["conventional"].append("Has a traditional navigation menu")
    if soup.find(['form', 'input', 'button', 'search']):  # Interaktive Formulare & Buttons
        conventional_features += 2
        found_features["conventional"].append("Contains interactive forms or search fields")
    if soup.find(['section', 'aside', 'article']):  # Moderne Webseitenstruktur
        conventional_features += 2
        found_features["conventional"].append("Includes SEO or tracking elements")

    # Tracking & Werbung
    if re.search(
            r'gtag|google-analytics|meta name="description"|meta property="og:image"|<script src="analytics\.js"|<script src="gtag\.js"|fbq\(|window\.dataLayer|GoogleTagManager|doubleclick\.net|adservice\.google\.com',
            html):
        conventional_features += 2
        found_features["conventional"].append("Uses Google anaytics and meta tags")
    if re.search(r'cookie-banner|cookie-consent|gdpr-banner', html, re.IGNORECASE):
        conventional_features += 2
        found_features["conventional"].append("Includes cookies")
    if re.search(r'adsbygoogle|googlesyndication|adservice|doubleclick|banner-ad', html, re.IGNORECASE):
        conventional_features += 3
        found_features["conventional"].append("Includes ads")
    if re.search(r'google_ads_iframe|taboola-|google-one-tap', html, re.IGNORECASE):  # Adblocker erkennen
        conventional_features -= 2

    # Nutzung von CMS oder Frameworks
    if re.search(r'bootstrap|tailwind|viewport|stylesheet', html):  # Moderne Webdesign-Frameworks
        conventional_features += 1
        found_features["conventional"].append("Uses modern web design frameworks")
    if re.search(r'display:\s*(grid|flex)', html):  # Nutzung von CSS-Grid oder Flexbox für Layouts
        conventional_features += 2
        found_features["conventional"].append("Uses Grid or Flexbox")
    if re.search(r'wp-content|wp-includes|joomla|drupal', html, re.IGNORECASE):  # Typische CMS-Frameworks
        conventional_features += 2
        found_features["conventional"].append("Uses typical CMS frameworks")

    # E-Commerce-Funktionalitäten
    if re.search(r'Warenkorb|Checkout|Login|Mein Konto', html, re.IGNORECASE):  # Kommerzielle Webseitenmerkmale
        conventional_features += 3
        found_features["conventional"].append("Includes commercial elements")

    # --- Bewertung der Seite ---
    score = artistic_features - conventional_features

    if score >= 2:
        result = "Likely an artistic website."
    elif score >= 0:
        result = "Possibly artistic, but unclear."
    else:
        result = "Likely a conventional website."

    return result, artistic_features, conventional_features, found_features


# Beispiel-URLs zum Testen
#urls = [
    #"https://www.trashloop.com/",
    #"https://www.bbc.com/",
    #"https://www.apple.com/",
    #"https://www.libraryofbabel.info/",
    #"https://www.wikipedia.org/",
    #"https://jonaslund.com/capitalism/",
    #"https://mollysoda.exposed/",
    #"http://www.entropy8zuper.org/godlove/fuxation/",
    #"https://geo.craigslist.org/iso/de",
    #"https://www.gusto-graeser.info/"
#]

# Streamlit UI
st.title("NAD Web App – Crawling & URL-Analyse")

# Wahl zwischen Crawling und Analyse
mode = st.radio("Choose a mode:", ["Crawl the Web", "Analyze a List of URLs"])

if mode == "Crawl the Web":
    start_url = st.text_input("Enter the Starting URL:")
    depth = st.slider("Set Crawl Depth (1 = Just the Starting URL):", 1, 3, 1)

    if st.button("Start Crawling"):
        st.write("Crawling not yet implemented...")
        #

elif mode == "Analyze a List of URLs":
    urls_input = st.text_area("Enter URLs (one per line):")

    if st.button("Analyze URLs"):
        urls = urls_input.strip().split("\n")
        results = []

        for url in urls:
            html = fetch_html(url.strip())
            if html:
                result, art_points, conv_points, found_features = analyze_html(html)
                results.append({
                    "URL": url,
                    "Result": result,
                    "Artistic Features": ", ".join(found_features["artistic"]),
                    "Conventional Features": ", ".join(found_features["conventional"])
                })

        if results:
            st.write("### Analysis Results")

            # Liste zum Speichern der JSON-Daten für den Download
            json_results = []

            for res in results:
                with st.expander(f"🔗 {res['URL']}"):
                    st.write(f"**Result:** {res['Result']}")

                    # JSON-kompatible Struktur erstellen
                    result_data = {
                        "URL": res["URL"],
                        "Result": res["Result"],
                        "Artistic Features": res["Artistic Features"] if res["Artistic Features"] else [
                            "None detected"],
                        "Conventional Features": res["Conventional Features"] if res["Conventional Features"] else [
                            "None detected"]
                    }

                    # JSON anzeigen
                    st.json(result_data)

                    # Daten für den Download speichern
                    json_results.append(result_data)

            # JSON-Datei erstellen und als Download anbieten
            json_str = json.dumps(json_results, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="web_analysis_results.json",
                mime="application/json"
            )