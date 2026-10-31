# Aegis Communication website

Static site for www.aegiscomm.com.my. Plain HTML, one stylesheet, one small script, and a PHP contact handler. No framework, no build tooling beyond Python.

## Folder layout

| Path | What it is |
|---|---|
| `index.html`, `about.html`, `approach.html`, `contact.html`, `404.html`, `services/*.html` | Generated pages. Do not edit these directly. |
| `_src/pages/*.html` | Page content fragments. Edit copy here. |
| `_src/build.py` | Wraps each fragment with the shared header, footer and meta tags, and writes `sitemap.xml` and `robots.txt`. |
| `_src/tools/` | Scripts: `extract_pics.py` and `assets.py` pulled logos and photos from the decks; `diagrams.py` generates the inline SVG framework diagrams (run it, then build, after changing a diagram). |
| `assets/fonts/` | Self-hosted Inter and Newsreader (latin subset). |
| `assets/mark.svg`, `assets/favicon.svg`, `assets/og-image.png` | Brand motif used as watermark and bullets, favicon, and the link-preview image. |
| `assets/style.css`, `assets/site.js` | Styles and behaviour. Colour tokens sit at the top of the stylesheet: slate text #0F172A, brand blue #0E6BB4, brand teal #1AB191, hairline #E2E8F0. |
| `assets/photos/` | Event photos extracted from the decks. |
| `assets/network/` | Media and investment-community logo composites from the deck. |
| `contact.php` | Receives the contact form, emails aegis@aegiscomm.com.my and saves a copy to the backend's Enquiries. |
| `aegis/` | Content backend at `/aegis/`. See Content backend below. |
| `_src/cms.py` | Build helper that tags editable text for the backend and re-applies saved edits. |

## Editing copy

1. Edit the fragment in `_src/pages/`. Each fragment starts with `title`, `description` and `path`, then `---`, then the page body.
2. Run the build:

```bash
python _src/build.py
```

3. Preview locally:

```bash
python -m http.server 8080
```

Then open http://127.0.0.1:8080/ in a browser.

To change the navigation or footer, edit `NAV`, `header()` or `footer()` in `_src/build.py` and rebuild.

## Going live (Plesk)

1. Back up the current site files in Plesk File Manager.
2. Upload everything except `_src/`, `_work/`, `README.md` and `.claude/` to the web root (`httpdocs`). That includes the `aegis/` folder (see Content backend below). `robots.txt` already blocks `_src/` in case it is uploaded.
3. Photos ship as JPG with a WebP copy beside each; keep both.
4. Set the 404 document to `404.html` in Plesk (Apache & nginx settings, or `.htaccess`: `ErrorDocument 404 /404.html`).
5. Send a test enquiry from the contact page and confirm the email arrives. If PHP `mail()` is disabled on the hosting, switch `contact.php` to the hosting's SMTP relay or a form service.
6. Submit `https://www.aegiscomm.com.my/sitemap.xml` in Google Search Console.

## Deploying from GitHub (Plesk Git)

The code lives in the private repository https://github.com/thenja96/Aegis-Website.

1. Plesk, Websites & Domains, the domain, **Git**. Add a remote repository with `https://github.com/thenja96/Aegis-Website.git`. A private repository needs access: use the SSH key Plesk shows, added under the repository's Settings, Deploy keys (read-only), and the SSH address `git@github.com:thenja96/Aegis-Website.git`.
2. Deployment mode: **Manual** (deploy on button press). Deployment path: `httpdocs`.
3. Turn on **Enable additional deployment actions** and enter `php aegis/republish.php`. A deploy copies the repository's pages over the live ones; this re-applies the edits saved in the backend.
4. Press **Deploy**. The root `.htaccess` sets the 404 page and blocks `_src/`, `.git` and `README.md` from the web.

After changing pages locally: run `python _src/build.py`, commit, push, then press Deploy in Plesk.

## Client confidentiality

Client logos, client names and any photo showing a client's name were removed because of non-disclosure agreements. Do not add them back without written client consent. Event photos must not show a client's name on screens, backdrops or banners.

The Track Record page is hidden. Its text is kept, without logos, in `_src/hidden/track-record.html`. To bring it back: move it to `_src/pages/`, add it back to `NAV`, `NEXT` and `footer()` in `_src/build.py`, remove its `RedirectMatch` line from `.htaccess`, then rebuild.

## Content backend (`/aegis`)

A small PHP admin at `https://www.aegiscomm.com.my/aegis/` for changing text, page titles, image descriptions and images, and for reading contact-form enquiries. Nothing on the public site links to it. Content is stored in files, no database.

| Path | What it is |
|---|---|
| `aegis/index.php` | The admin screens: sign-in, Pages, Menu and footer, Images, Enquiries, Account, User guide. |
| `aegis/lib.php` | Shared code: storage, applying edits to the pages, cleaning edited text, sign-in limits. Never served directly. |
| `aegis/data/manifest.php` | Written by `_src/build.py`: every editable text block and image, with its original wording. Upload it with every rebuild. |
| `aegis/data/content.php` | Saved edits. Created by the backend. **Lives on the server; never overwrite it from a local copy without downloading it first.** |
| `aegis/data/users.php`, `enquiries.php`, `attempts.php` | Admin account (password hashed), enquiries, sign-in attempt counter. Created on the server. |
| `assets/theme.css` | Written by the backend's Design screen (colours, text size, heading font, button corners). Committed empty; `aegis/republish.php` rewrites it after every deploy. |
| `aegis/data/setup.php` | One-time setup key, created on the server the first time `/aegis/` is opened. Deleted automatically once the admin account is created. |

Every data file starts with a PHP exit line and the folder has `Require all denied`, so none of it can be read in a browser.

**First use on the hosting**

1. Upload the site as above, including the `aegis/` folder.
2. In Plesk File Manager, make sure PHP can write to `aegis/data/` and to the page files (`*.html`, `services/*.html`, `assets/photos/`, `assets/team/`, `assets/clients/`). With the usual Plesk setup, files uploaded by FTP are already writable by PHP.
3. Open `/aegis/` once in a browser (this creates the key), then open `aegis/data/setup.php` in File Manager and copy the key after `"key":`.
4. Go to `/aegis/`, paste the key, choose a username and a password of at least 10 characters.

**How edits work.** The build tags each text block with `data-e="<key>"`, a hash of its original wording. When you save in the backend, it rewrites only those blocks in the page files. Running `python _src/build.py` locally re-applies the edits in `aegis/data/content.php`. So before rebuilding, download `aegis/data/content.php` from the server into the local `aegis/data/`. Then upload the rebuilt pages together with the new `manifest.php`. If wording is later changed in `_src/pages`, any backend edit to that same block no longer matches its key and is dropped.

**Testing locally** needs PHP 8.x: `php -S 127.0.0.1:8090 -t .` in the site folder, then open http://127.0.0.1:8090/aegis/. The built-in server ignores `.htaccess`, but the data files are still protected by their exit line. Email does not send locally.

## Content rules used

- Copy comes from the approved pitch decks (Company Profile V5, IPO Services Pitch FINAL, IRPR Services Pitch FINAL). Deck disclaimers are kept verbatim.
- No fees, no share prices, no market-cap figures, no "strictly private and confidential" material.
- Client names appear only as logos (with the company name in the image `alt` text), never as written lists. Photo captions name the event type, not the client.

## Known gaps

- Team photos: drop square head-and-shoulders JPGs (at least 600px) into `assets/team/` named `jason-fong.jpg`, `aden-then.jpg`, `ryan-low.jpg`, `cherise-lai.jpg`, `wong-seng-chun.jpg`, `kelly-cheah.jpg`, `janice-lee.jpg`. The People page picks them up automatically; initials show until a file exists. Bio lines for the four executives are placeholders describing their role areas and should be confirmed.
- Phone numbers: the decks show 03-6413 0580 for both Executive Directors and 03-5023 1848 as the office line. Confirm which is current.
- The Google Maps embed on the contact page needs an internet connection to render.
