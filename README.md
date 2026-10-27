# LABCOL-1709 AI by Design for Collaboration

[Read the online guide](https://joshua-tan-wai-kiat.github.io/labcol-1709-ai-by-design-collaboration-lab-guide/)

The online guide follows the updated Word document supplied on 27 October 2026: **CLMEL26 - LABCOL-1709 AI by Design for Collaboration - Lab Guide (2).docx**, by Hussain Ali and Omer Ilyas.

The original section order, module names, instructional wording, numbered steps, bullet points, emphasis, yellow highlights, inline control icons, and instructional screenshots are retained. The Word table of contents becomes grouped web navigation with separate exercise pages; page numbers and blank page-layout paragraphs are omitted. Screenshots open at full resolution when clicked.

## Documentation layout and image audit

The layout follows the compact documentation pattern of the user-provided [LTRCCT-2000 lab reference](https://webexcc-sa.github.io/MEL26LTRCCT-2000/main/overview/): a dark header, grouped navigation, individual exercise pages, search, a light/dark toggle, and Previous/Next links. The complete guide remains available as one printable page; longer meeting background material can be expanded on its overview page.

[View the complete screenshot inventory](screenshots/index.html). All 61 Word image assets are accounted for: 41 instructional screenshots, seven control icons, and two branding images are published; ten images are withheld for privacy; one non-instructional menu icon is not used. The 50 published files were downloaded and matched byte-for-byte against the Word originals. No image failed the availability or fidelity check. The audit timestamp and per-image results are in `screenshot-audit.json`.

## Public edition

Ten images containing example credentials, private session details, or private account contact information are replaced by explicit omission notes. Eight paragraphs containing private access values or password construction rules use assigned-session placeholders. The remaining 50 image assets include the source branding, inline icons, and instructional screenshots. The original Word file is not published.

The source document is the authority for this synchronization. Technical suggestions from the previous review are not silently applied; this publication does not claim that the lab has been executed or validated. The older formatted Word file retained in repository history and the file tree is a previous edition, not the current online content.

## Edit and build

`content.html` contains the converted source body. Edit it and run `python build.py` to regenerate all exercise pages and the deployable `site/` directory. `source-manifest.json` records the section headings, source fingerprint, image inventory, and privacy exceptions. Keep its navigation entries synchronized when changing headings. `GUIDE.md` is a parallel readable source export and must be kept synchronized when editing content.

Run `python build.py` using Python 3.12 or later; the build has no third-party Python dependencies. Every push to `main` rebuilds and publishes the guide with GitHub Actions. The generated website uses relative asset links so it can be copied or transferred to another repository; enable Pages there and update the repository links.
