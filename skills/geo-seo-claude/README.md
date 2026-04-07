# GEO-SEO-Claude Skills Repository

This directory contains all skills from the **geo-seo-claude** GitHub repository (https://github.com/zubair-trabzada/geo-seo-claude).

## Overview

These skills provide a complete framework for **Generative Engine Optimization (GEO)** — optimizing websites to be discovered, cited, and recommended by AI systems like ChatGPT, Google Gemini, Perplexity AI, Claude, and Bing Copilot.

GEO is distinct from traditional SEO. While traditional SEO optimizes for Google's search rankings, GEO optimizes for AI citation and visibility across AI-powered search platforms. Research shows that GEO-optimized sites see **30-115% higher visibility in AI-generated responses**.

---

## Skills in This Collection

### Core Audit Skills

| Skill | File | Purpose |
|-------|------|---------|
| **GEO Audit Orchestration** | `01-geo-audit.md` | Comprehensive GEO audit across all dimensions (10 dimensions, composite scoring) |
| **AI Citability Scoring** | `02-geo-citability.md` | Analyze how likely AI systems are to cite/quote each page |
| **Content Quality & E-E-A-T** | `03-geo-content.md` | Evaluate Experience, Expertise, Authoritativeness, Trustworthiness signals |
| **AI Crawler Access Analysis** | `04-geo-crawlers.md` | Check robots.txt, meta tags, and HTTP headers for AI crawler access |
| **Brand Mention Scanner** | `05-geo-brand-mentions.md` | Measure brand authority across YouTube, Reddit, Wikipedia, LinkedIn, etc. |
| **Technical SEO Audit** | `06-geo-technical.md` | Crawlability, indexability, security, performance, SSR, Core Web Vitals |
| **Schema & Structured Data** | `07-geo-schema.md` | Validate and generate JSON-LD markup for entity recognition |
| **Platform Optimization** | `08-geo-platform-optimizer.md` | Optimize separately for Google AI Overviews, ChatGPT, Perplexity, Gemini, Copilot |

### Business & Reporting Skills

| Skill | File | Purpose |
|-------|------|---------|
| **GEO Client Report** | `09-geo-report.md` | Generate professional, client-facing GEO reports |
| **GEO PDF Report Generator** | `10-geo-report-pdf.md` | Create polished PDF reports with charts and visualizations |
| **Monthly Delta Report (geo-compare)** | `11-geo-compare.md` | Track progress month-to-month with before/after scoring |
| **GEO Proposal Generator** | `12-geo-proposal.md` | Auto-generate client-ready service proposals from audit data |
| **GEO Prospect Manager (CRM)** | `13-geo-prospect.md` | Manage prospects through sales pipeline (lead → qualified → proposal → won) |

### Emerging Standards

| Skill | File | Purpose |
|-------|------|---------|
| **llms.txt Generator** | `14-geo-llmstxt.md` | Analyze/generate llms.txt — emerging standard for AI readability |

---

## Quick Start

### 1. Run a Full GEO Audit
```
Use: 01-geo-audit.md
Input: Website URL
Output: GEO-AUDIT-REPORT.md (0-100 score with prioritized action plan)
```

### 2. Analyze Citability for AI Systems
```
Use: 02-geo-citability.md
Input: URL or existing page content
Output: GEO-CITABILITY-SCORE.md (per-section citability scores + rewrite suggestions)
```

### 3. Evaluate Content Quality Using E-E-A-T Framework
```
Use: 03-geo-content.md
Input: Website content (homepage, key pages)
Output: GEO-CONTENT-ANALYSIS.md (E-E-A-T breakdown, gaps, improvements)
```

### 4. Check AI Crawler Access
```
Use: 04-geo-crawlers.md
Input: Domain
Output: GEO-CRAWLER-ACCESS.md (which AI crawlers can access, which are blocked)
```

### 5. Generate Client Reports
```
Use: 09-geo-report.md (markdown) or 10-geo-report-pdf.md (PDF)
Input: GEO audit data
Output: Professional client deliverable
```

---

## Key Concepts

### Generative Engine Optimization (GEO)

GEO optimizes for AI citation and recommendation. Key differences from traditional SEO:

| Aspect | Traditional SEO | GEO |
|--------|---|---|
| Target | Google search rankings | AI system citation (ChatGPT, Perplexity, etc.) |
| Primary ranking factor | Backlinks, Domain Authority | Brand mentions on YouTube/Reddit/Wikipedia, E-E-A-T signals |
| Content optimization | Keyword density, featured snippets | Citability (134-167 word self-contained passages), answer-first structure |
| Entity recognition | Domain reputation | Cross-platform entity graph (Wikipedia, Wikidata, LinkedIn, sameAs properties) |
| Crawler access | Googlebot | Multiple AI crawlers (GPTBot, ClaudeBot, PerplexityBot, etc.) |

### GEO Readiness Score Components

All audit skills contribute to a **composite GEO Score (0-100)**:

- **AI Citability (25%)** — How extractable/quotable is your content for AI?
- **Brand Authority (20%)** — How visible is your brand across AI-indexed platforms?
- **Content E-E-A-T (20%)** — How authoritative and trustworthy is your content?
- **Technical GEO (15%)** — Are you accessible to AI crawlers? SSR? Performance?
- **Schema & Structured Data (10%)** — How complete is your entity graph?
- **Platform Optimization (10%)** — Are you optimized for Google AIO, ChatGPT, Perplexity, etc.?

**Score Interpretation:**
- **90-100** — Excellent: Top-tier GEO, AI platforms likely to cite
- **75-89** — Good: Strong foundation, clear optimization opportunities
- **60-74** — Fair: Moderate GEO presence, significant gaps
- **40-59** — Poor: Weak GEO signals, AI visibility at risk
- **0-39** — Critical: Minimal optimization, largely invisible to AI

---

## Critical GEO Insights from Research

### 1. Platform Preference Shifts Are Real
- Only **11% of domains** are cited by BOTH ChatGPT and Google AI Overviews
- Each AI platform has different crawling behavior, ranking logic, and source preferences
- Platform-specific optimization is not optional

### 2. Brand Mentions > Backlinks for AI
- Brand mentions correlate ~3x more strongly with AI visibility than traditional backlinks
- **YouTube mentions**: ~0.737 correlation with AI citation (strongest)
- **Reddit mentions**: Heavy emphasis by Perplexity and ChatGPT
- **Wikipedia presence**: Foundation for entity recognition across all AI systems

### 3. Content Citability Has Specific Patterns
- **Optimal passage length**: 134-167 words (self-contained)
- **Definition patterns increase citation**: 2.1x lift
- **Adding statistics**: +40% citation probability
- **Answer-first structure**: Key for AI extraction

### 4. AI Crawlers Don't Execute JavaScript
- GPTBot, ClaudeBot, PerplexityBot, etc. **do NOT execute JavaScript**
- Client-side rendered content is **invisible to AI crawlers**
- Server-side rendering (SSR) is mandatory for AI visibility
- Even Googlebot deprioritizes JS-rendered content

### 5. Entity Recognition Is Everything
- AI systems verify entities through Wikipedia, Wikidata, LinkedIn, and **sameAs properties**
- Incomplete entity graphs reduce citation probability
- Consistency across platforms is critical

---

## How to Use These Skills in Your Projects

### For Auditing a Website
1. Start with **01-geo-audit.md** for a comprehensive baseline
2. Dig deeper with specific skills as needed
3. Use **09-geo-report.md** to create a client-ready deliverable
4. Track progress with **11-geo-compare.md** for monthly/quarterly reviews

### For Content Optimization
1. Use **02-geo-citability.md** to score each page
2. Use **03-geo-content.md** to improve E-E-A-T
3. Use **07-geo-schema.md** to add proper structured data
4. Use **08-geo-platform-optimizer.md** to optimize per platform

### For Brand Building
1. Use **05-geo-brand-mentions.md** to understand current authority
2. Identify gaps across YouTube, Reddit, Wikipedia, LinkedIn
3. Create targeted campaigns to build presence on high-signal platforms

### For Agency/Business Development
1. Use **12-geo-proposal.md** to generate proposals for prospects
2. Use **13-geo-prospect.md** to manage your sales pipeline
3. Use **11-geo-compare.md** to show clients month-to-month progress
4. Use **10-geo-report-pdf.md** for polished client deliverables

---

## Output Files Generated by Each Skill

| Skill | Output File | Format |
|-------|---|---|
| 01-geo-audit.md | GEO-AUDIT-REPORT.md | Markdown |
| 02-geo-citability.md | GEO-CITABILITY-SCORE.md | Markdown |
| 03-geo-content.md | GEO-CONTENT-ANALYSIS.md | Markdown |
| 04-geo-crawlers.md | GEO-CRAWLER-ACCESS.md | Markdown |
| 05-geo-brand-mentions.md | GEO-BRAND-MENTIONS.md | Markdown |
| 06-geo-technical.md | GEO-TECHNICAL-AUDIT.md | Markdown |
| 07-geo-schema.md | GEO-SCHEMA-REPORT.md | Markdown |
| 08-geo-platform-optimizer.md | GEO-PLATFORM-OPTIMIZATION.md | Markdown |
| 09-geo-report.md | GEO-CLIENT-REPORT.md | Markdown |
| 10-geo-report-pdf.md | GEO-REPORT-[brand].pdf | PDF |
| 11-geo-compare.md | GEO-MONTHLY-[domain]-[date].md | Markdown |
| 12-geo-proposal.md | GEO-PROPOSAL-[domain].md | Markdown |
| 13-geo-prospect.md | prospects.json | JSON (CRM database) |
| 14-geo-llmstxt.md | llms.txt or GEO-LLMSTXT-ANALYSIS.md | Text/Markdown |

---

## Recommended Reading Order

1. **Start with**: 01-geo-audit.md (understand the full framework)
2. **Then explore**: 02-geo-citability.md (how AI chooses what to cite)
3. **Then add context**: 05-geo-brand-mentions.md (why platform presence matters)
4. **For implementation**: 06-geo-technical.md, 07-geo-schema.md, 08-geo-platform-optimizer.md
5. **For business**: 12-geo-proposal.md, 13-geo-prospect.md

---

## Important Notes

- These skills are designed to be **chained together** — the output of one often feeds into others
- All skills use **0-100 scoring rubrics** for consistency and client communication
- Heavy emphasis on **action items** — every finding should connect to a specific, implementable action
- **Platform-specific optimization** is critical — there's no "one size fits all" approach
- **Speed matters** — AI indexing happens faster than traditional search; IndexNow protocol is recommended

---

## Attribution

All skills are from the **geo-seo-claude** repository created by Zubair Trabzada.
Repository: https://github.com/zubair-trabzada/geo-seo-claude

Download date: April 2026
