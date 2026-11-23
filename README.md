# TeddyPups Website Clone

High-fidelity responsive clone of [https://puppy.instabizweb.com/](https://puppy.instabizweb.com/).

## 🚀 Key Features & Highlights
- **100% Visual & Functional Fidelity**: Matches layout, typography, custom color palette (`Veu4Sq_variable`, `hpvSLW_variable`), and fluid viewport scaling for PC and mobile devices.
- **Motions & Video**: Autoplaying background MP4 hero videos, responsive card tilt motions, and interactive sliders.
- **Complete Page Catalog**:
  - Homepage (`/`)
  - Catalog with Breed & Origin filter tabs (`/puppies`)
  - Individual puppy profile galleries (`/puppies/korean-teacup-maltipoo-female`, `/puppies/copper-male`, etc.)
  - Information pages (`/how-it-works`, `/happy-families`, `/gone-home`, `/faq`, `/contact`)
- **React Server Components (RSC) Flight Streaming**: Pre-cached component payloads (`.rsc`) enabling client-side soft navigation without error-boundary interruptions.
- **Enterprise Security Hardening**:
  - Path traversal and LFI guard via canonical confinement (`os.path.commonpath`).
  - Strict static file extension whitelist.
  - Modern HTTP security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection`, `Referrer-Policy`.
  - Obfuscated server runtime banners.

---

## 🛠️ How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/garv1garv/Puppy.git
   cd Puppy
   ```

2. Start the local server:
   ```bash
   python serve.py
   ```

3. Open your browser:
   ```
   http://localhost:3000
   ```

---

## 📂 Project Structure
```
├── clone/                      # Cleaned and beautified website build
│   ├── index.html              # Homepage
│   ├── puppies.html            # Puppy catalog
│   ├── puppies/                # Puppy profile pages
│   ├── media/                  # Optimized puppy photos and MP4 videos
│   ├── _rsc_cache/             # React flight component streams
│   └── _next/                  # Stylesheets, font faces, and script chunks
├── serve.py                    # Secure local server gateway & RSC router
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```
