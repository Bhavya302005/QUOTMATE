```markdown
# Design System Specification: Architectural Minimalism

## 1. Overview & Creative North Star: "The Digital Blueprint"
This design system is a rejection of the "soft" web. It moves away from the rounded, shadow-heavy trends of the last decade in favor of **Architectural Minimalism**. The Creative North Star is the "Digital Blueprint"—a high-precision, editorial environment where every pixel is intentional, and every line serves a structural purpose.

We achieve a high-end feel not through decoration, but through **extreme restraint**. The signature look is defined by razor-sharp 0px radii, high-contrast black-on-white layouts, and a rigid adherence to an underlying architectural grid. By stripping away shadows and gradients, we force the user’s focus toward typography, proportion, and the "white space" that acts as a structural element in itself.

---

## 2. Colors: High-Contrast Monochromatism
The palette is restricted to an absolute binary of deep black and pure white, with a surgical application of neutral grays for structural nuance.

| Token | Value | Role |
| :--- | :--- | :--- |
| `primary` | #000000 | Core branding, primary actions, and headlines. |
| `surface` | #F9F9F9 | Main canvas. Use to provide a "gallery" feel. |
| `surface_container_lowest` | #FFFFFF | Active work surfaces or cards. |
| `on_surface` | #1A1C1C | Primary body text. Never pure black for long-form. |
| `outline` | #777777 | Secondary structural lines. |
| `outline_variant` | #C6C6C6 | Tertiary decorative lines. |
| `error` | #BA1A1A | The only permitted chromatic break. |

### The "Razor-Thin" Rule
Sectioning must never be achieved through soft shadows. Boundaries are defined by the `px` (1px) token using `#000000` or `#C6C6C6`. 

### Surface Hierarchy
To create depth without shadows, use the "Inking" method:
- **Level 0 (Base):** `surface` (#F9F9F9)
- **Level 1 (Navigation/Sidebars):** `surface_container` (#EEEEEE) 
- **Level 2 (Active Cards):** `surface_container_lowest` (#FFFFFF) with a `1px` border of `primary`.

---

## 3. Typography: The Editorial Mix
We utilize a dual-font strategy to balance human-centric headlines with machine-precise data.

### Header/Display: Inter (Sans-Serif)
Use Inter for all `display`, `headline`, and `title` roles. It should be tracked slightly tighter (-2%) in large sizes to feel like a high-end fashion masthead.
- **Display-LG:** 3.5rem / Bold / All-Caps (Optional for impact)
- **Headline-MD:** 1.75rem / Semi-Bold

### Data/Labels: Space Grotesk / JetBrains Mono (Monospace)
Use the monospaced font for `label-md`, `label-sm`, and any numerical data. This creates an "architectural annotation" look that feels technical and premium.
- **Label-MD:** 0.75rem / Medium / Monospace.
- **Context:** Use for timestamps, metadata, and breadcrumbs.

---

## 4. Elevation & Structural Rigidity
In this system, "Elevation" does not mean Z-axis height; it means **line weight and contrast.**

*   **The Layering Principle:** Depth is achieved by nesting. A white container (`surface_container_lowest`) sits inside a light gray section (`surface_container`), framed by a 1px black border.
*   **Zero Shadows:** Traditional shadows are strictly prohibited. If an element needs to "pop," increase its border weight to 2px or invert the color scheme (White text on Black background).
*   **The Architectural Grid:** All elements must align to the `spacing scale`. Use `20` (4.5rem) for major section gutters and `4` (0.9rem) for internal component padding.
*   **Sharp Edges:** All `border-radius` tokens are set to `0px`. No exceptions. This reinforces the engineering-led aesthetic.

---

## 5. Components: Precision Primitives

### Buttons
*   **Primary:** Background `#000000`, Text `#FFFFFF`, `0px` radius. Padding: `spacing-4` (vertical) `spacing-8` (horizontal).
*   **Secondary:** Background `transparent`, Border `1px #000000`, Text `#000000`.
*   **Tertiary:** Text `#000000`, Monospaced font, all-caps, with a `1px` underline.

### Input Fields
*   **State - Default:** `1px` border using `outline_variant`.
*   **State - Focus:** `1px` border using `primary` (#000000). No "glow" or blue outlines.
*   **Label:** Always use `label-sm` (Monospace) positioned above the field, never floating inside.

### Cards & Lists
*   **Cards:** Forbid divider lines within a card. Use `spacing-6` (1.3rem) of vertical white space to separate content chunks.
*   **Lists:** Separate items with a `1px` border using `outline_variant`. The hover state should invert the item: Background `#000000`, Text `#FFFFFF`.

### Technical Specs (The Data Block)
*   Unique to this system: Any metadata should be housed in a "Data Block"—a `surface_container_high` box with a `1px` dashed border and monospaced text.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical layouts. Place a large `display-lg` header on the far left and the body text in a narrow column on the far right.
*   **Do** embrace "dead space." If a screen feels empty, it is likely working as intended.
*   **Do** use 1px vertical lines to separate columns, mimicking a ledger or blueprint.

### Don't
*   **Don't** use border-radii, even for checkboxes or radio buttons. Everything is a square.
*   **Don't** use "Soft Grays" for text. Stick to `on_surface` (#1A1C1C) to maintain the high-contrast "Ink on Paper" feel.
*   **Don't** use animation transitions like "Pop" or "Bounce." Use "Slide" or "Instant Fade" (0.1s) to maintain the rigid, mechanical feel.

### Accessibility Note
While the system is high-contrast, ensure that `outline` tokens used for decorative lines do not get confused with interactive borders. Always ensure the `primary` #000000 is used for the "Active" state of any component.```