# Ziyada Frontend Canonical Target

Purpose: prevent agents from editing or deploying the wrong frontend copy.

## Canonical App (use this)

- projects/ziyada-system/app/ziyada-system-website

All frontend fixes, QA, and deployment prep for Ziyada website must happen in this path.

## Non-Canonical Duplicate (do not use unless user explicitly asks)

- projects/ziyada-system/files from antigraviti to claude/ziyada system زيادة سيستم/ziyada-system-website

## Required Agent Flow

1. Identify candidate frontend roots first.
2. Verify canonical target from this file and AGENTS rules.
3. Run local comparison ports only when needed.
4. Apply edits only in canonical app path.
5. Never deploy from non-canonical duplicate paths.

## CSS Guardrails (Do Not Break)

For any frontend/layout update, agents must keep these rules intact:

1. Keep horizontal overflow blocked at all levels:
	- `html`, `body`, and `#root` must not allow horizontal scroll.
	- Layout shell must keep `overflow-x` clipped.
2. Top bar must degrade early on smaller widths:
	- Hide desktop nav and CTA at medium widths before they can overflow.
	- Keep mobile menu trigger available from medium widths downward.
	- Keep brand wordmark ellipsized instead of forcing width expansion.
3. Never use off-canvas positioning tricks that can expand page width:
	- Avoid patterns like `left: -9999px`.
	- Use visually-hidden patterns that keep element geometry contained.
4. For iOS/mobile input focus behavior:
	- Keep interactive controls at 16px font size on mobile breakpoints.

## Deployment Guardrails (Canonical Only)

- Before deploy, verify cwd is exactly:
  - `projects/ziyada-system/app/ziyada-system-website`
- Run build from canonical app only.
- Deploy/publish from canonical app only.
- If another copy exists, do not run deploy command there.

## Current UX Rules (locked)

- Chat widget launcher and panel must stay on right side in all languages.
- Voice widget launcher and panel must stay on right side in all languages.
- Keep mobile right-hand accessibility priority.

## Last Updated

- 2026-04-15
