# End-user manuals – NFE and ALP modules

Step-by-step user manuals with a screenshot for every step, in English and Arabic.

Signed-in users read them inside the application under **Documentation → User Manual** in the sidebar
(`/dashboard/manual/`): the page shows the manual of the user's module in the interface language, rendered from
the Markdown below with the screenshots, and offers the Word and PDF files for download. The admin panel manual is
only offered to accounts with staff or superuser status. See `student_registration/dashboard/manual_views.py`.

| Manual | Word | PDF | Markdown source |
|---|---|---|---|
| NFE module – English | `NFE_User_Manual_EN.docx` | `NFE_User_Manual_EN.pdf` | `en/NFE_User_Manual.md` |
| NFE module – Arabic | `NFE_User_Manual_AR.docx` | `NFE_User_Manual_AR.pdf` | `ar/NFE_User_Manual.md` |
| ALP module – English | `ALP_User_Manual_EN.docx` | `ALP_User_Manual_EN.pdf` | `en/ALP_User_Manual.md` |
| ALP module – Arabic | `ALP_User_Manual_AR.docx` | `ALP_User_Manual_AR.pdf` | `ar/ALP_User_Manual.md` |
| Admin panel (user management and permissions) – English | `Admin_User_Manual_EN.docx` | `Admin_User_Manual_EN.pdf` | `en/Admin_User_Manual.md` |
| Admin panel (user management and permissions) – Arabic | `Admin_User_Manual_AR.docx` | `Admin_User_Manual_AR.pdf` | `ar/Admin_User_Manual.md` |

The screenshots live in `screenshots/en/` and `screenshots/ar/` (same file names in both languages, taken
with the interface switched to that language). The data they show is demonstration data.

## Editing the text

The manual text is kept in `content_nfe.py`, `content_alp.py` and `content_admin.py` (one `EN` and one `AR` dictionary each).
Every section is a list of blocks: paragraphs, notes, bullet lists, numbered steps with an optional
screenshot and caption, stand-alone screenshots and tables. After editing, rebuild everything with:

```bash
pip install python-docx pillow            # once
python docs/user_manuals/build_manuals.py        # Markdown + DOCX (Arial / Calibri fonts)
python docs/user_manuals/build_manuals.py --pdf  # also export PDF through LibreOffice
```

The committed PDFs were rendered with `--font "Noto Naskh Arabic" --latin-font Inter` so that the Arabic
text is embedded with an open font.

## Re-taking the screenshots

`tools/` contains what was used to produce the screenshots against a throw-away local database:

* `demo_settings.py` – settings module layered on `config.settings.local` (local file storage, eager Celery).
* `seed_demo_data.py` – creates the locations, partner, centers, school, rounds, programmes, lookup tables,
  demo users (`nfe.center`, `nfe.partner`, `alp.school`) and demo children/teachers. Run it with
  `python manage.py shell < docs/user_manuals/tools/seed_demo_data.py`.
* `cleanup_demo_records.py` – removes the records created by a previous capture run so the run can be repeated.
* `flow.js`, `lib.js`, `cdn.js` – Playwright script that logs in, walks through every workflow of both modules
  (`admin_flow.js` does the same for the admin panel as the superuser `admin`)
  and saves the screenshots (`node flow.js en`, `node flow.js ar`; set `ONLY=login,attendance` to rerun some
  sections). `cdn.js` serves the front-end libraries from a local `node_modules` (see `vendor-package.json`)
  when the CDN is not reachable.

After capturing, downscale the images to 1200 px wide and copy them into `screenshots/<lang>/`, then rebuild.
