# Ziyada System Project

This folder contains all Ziyada System work.

## Structure

- `scripts/` - Python automations
- `tools/` - Shell wrappers
- `workflows/` - SOPs
- `docs/` - Planning and implementation docs
- `assets/` - Brand and exported assets
- `notebooks/` - Jupyter notebooks
- `outputs/` - Generated outputs for sharing
- `.tmp/` - Disposable temporary files
- `app/ziyada-growth-suite/` - Frontend project

## Baseline Instruction Source

Global baseline remains in `.github/CLAUDE skool Ai-automation society.md`.
Project files extend that baseline; they do not replace it.

## Blog Workflow Init (Voice + Tone Locked)

The blog workflow injects Ziyada's canonical Arabic voice prompt automatically.
The canonical file is the **full approved brand voice guide** (writing AI + TTS/ElevenLabs + Reels + sales scripts).
Edit only `docs/ZIYADA_VOICE_PROMPT_SYSTEM.txt` when the approved voice changes, then re-deploy.

1. Canonical system prompt file:
	- `docs/ZIYADA_VOICE_PROMPT_SYSTEM.txt`
2. Initializer script (test + deploy):
	- `scripts/init_ziyada_blog_workflow.py`
3. Deployment script:
	- `scripts/deploy_n8n_blog_workflow.py`

Additional env vars for Sheets logging:

- `ZIYADA_BLOG_SHEET_ID` (Google Spreadsheet ID)
- `ZIYADA_BLOG_REQUEST_SHEET_TAB` (default: `ContentCalendar`)
- `ZIYADA_BLOG_RESULTS_SHEET_TAB` (default: `ContentCalendar`)
- `TELEGRAM_BOT_TOKEN` (for Telegram trigger webhook setup)

Run init:

```bash
python3 projects/ziyada-system/scripts/init_ziyada_blog_workflow.py
```

Expected behavior:

- Saves a preview payload to `projects/ziyada-system/outputs/ziyada_blog_workflow_init_preview.json`
- Verifies that `content_writer.system_prompt` and `content_writer.user_prompt` are present in workflow payload
- Deploys/updates the n8n workflow when N8N env vars are available

Recommended n8n incoming payload example:

```json
{
  "topic": "أتمتة متابعة العملاء في العيادات",
	"approval_status": "pending",
	"hooks": [
		"عميلك يرسل ومحد يرد بسرعة؟",
		"ضياع المتابعة يكلفك مبيعات كل أسبوع",
		"خل النظام يمسك الرد والمتابعة بدل الضغط اليومي"
	],
	"seo": {
		"seo_title": "أتمتة متابعة العملاء للعيادات في السعودية",
		"seo_description": "دليل عملي لتقليل ضياع العملاء وتسريع الرد عبر الأتمتة وCRM.",
		"seo_keywords": "أتمتة, CRM, عيادات, متابعة العملاء",
		"target_keyword": "أتمتة متابعة العملاء"
	},
	"cta": "تواصل معنا على الواتساب ونرتب لك عرض بسيط",
	"audience": "أصحاب العيادات ومدراء التشغيل",
  "tags": ["عيادات", "crm", "automation"],
  "author": "Ziyada System"
}
```

Behavior:

- If `approval_status` is approved/yes/true/1: workflow appends the full content + hooks + SEO row to Google Sheet, then publishes to website.
- Otherwise: workflow stores request status as pending in sheet for follow-up and does not publish website.

## Telegram Trigger Setup

1. Set bot token in env: `TELEGRAM_BOT_TOKEN`
2. Deploy workflow:

```bash
python3 projects/ziyada-system/scripts/init_ziyada_blog_workflow.py
```

3. Register Telegram webhook to n8n:

```bash
python3 projects/ziyada-system/scripts/setup_telegram_bot_webhook.py
```

4. In Telegram, send messages to your bot. Examples:

- `/blog approved أتمتة متابعة العملاء في العيادات`
- `/blog send draft email أتمتة رسائل متابعة العملاء`
