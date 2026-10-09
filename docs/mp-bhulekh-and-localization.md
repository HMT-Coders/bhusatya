# MP Bhulekh Reference & Localization

## Official reference
- https://webgis2.mpbhulekh.gov.in/#/home
- Use the site as a reference for terminology, navigation and the land-record workflow only.
- Do not claim a live API or direct government data connection. Do not scrape protected pages or bypass authentication/CAPTCHA. Any live comparison needs an authorized, documented source.

## UI language support
- Default locale: Hindi (`hi`).
- User-selectable locales: English (`en`), Marathi (`mr`), Gujarati (`gu`), Punjabi (`pa`), Bengali (`bn`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Malayalam (`ml`), Odia (`or`), Urdu (`ur`).
- Language choice is persisted in browser local storage. Urdu sets RTL direction.
- The current prototype translates core navigation and common actions. Backend findings and technical evidence may remain in the source language until localized at the API/report layer.

## OCR language support
- Tesseract image OCR attempts `hin+eng`, then falls back to `eng` if Hindi trained data is unavailable.
- Install Tesseract and Hindi (`hin`) plus English (`eng`) language data for best results on bilingual Hindi/English scans.
- OCR output remains uncertain and must be manually verified.


## Document screening workspace translations

The document-screening workspace has explicit translations for all 12 supported language codes: Hindi (default), English, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam, Odia, and Urdu. Upload prompts, supported file types, analysis actions, OCR limitations, guided-case labels, and local API status messages use the selected language rather than falling back to English.
