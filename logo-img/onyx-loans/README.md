# Onyx Loans — Logo System

Every part of the mark maps to what the site does:

| Element | Meaning |
|---|---|
| **Blue ring** (`#0F58C9`) | The borrower — blue = trust and stability. |
| **Orange ring** (`#FF8A1D`) | The cosigner / lender — the helping hand; warmth and energy. |
| **Rings woven over/under** | The match: two parties linked, neither on top — a fair bond. |
| **Onyx gem in the overlap** | The brand name; the value and security held *between* both parties. Faceted = transparent loan details. |
| **Opening in the blue ring** | An open door — no credit check, Canada-wide access. |
| **Orange ring ends in an up-right arrow** | Speed (funds ~10 min after approval) and money coming back (loan cashback / early-repayment rebate). |
| **Maple leaf (tagline lockup)** | Proudly Canadian. Kept off the main wordmark so it never reads as a fine-print asterisk. |

## Files (SVG = master, PNG = 2x export)

| File | Use |
|---|---|
| `onyx-loans-logo-horizontal` | **Primary.** Site header, light backgrounds. |
| `onyx-loans-logo-horizontal-reversed` | Footer, dark hero, dark backgrounds. |
| `onyx-loans-logo-tagline` | Large placements: landing hero, documents, email signatures. Not for small headers. |
| `onyx-loans-logo-stacked` | Square spaces, social posts. |
| `onyx-loans-logo-mono-navy` | One-colour: loan agreements, faxed/printed forms, stamps. |
| `onyx-loans-icon` | Favicon source (transparent). |
| `onyx-loans-icon-app` | App icon / social avatar (dark rounded square). |

## Rules
- Minimum header height: 36px for the horizontal logo; below that use the icon.
- Keep clear space around the logo equal to the gem's height.
- Don't recolour, stretch, add shadows, or put the full-colour logo on busy photos.
- Text is outlined in the SVGs (Poppins Bold/SemiBold) — no font needed.
- Regenerate with `python3 scripts/generate-onyx-logos.py logo-img/onyx-loans` (needs `cairosvg`, `fonttools`, Poppins installed).
