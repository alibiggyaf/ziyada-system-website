#!/usr/bin/env python3
"""
Apply Ziyada System brand design guidelines + RTL Arabic formatting
to the existing Sales Guide Google Document.
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

DOC_ID = '1V0b11fxwn6WysNcfunvGSJJsng4XDImtfmRGr0KxQz4'
TOKEN_FILE = '/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/token_docs.json'

# Ziyada Brand Colors
C_NAVY = {'red': 15/255, 'green': 23/255, 'blue': 42/255}          # #0F172A
C_BLUE = {'red': 37/255, 'green': 99/255, 'blue': 235/255}         # #2563EB
C_LIGHT_BLUE = {'red': 59/255, 'green': 130/255, 'blue': 246/255}  # #3B82F6
C_MUTED = {'red': 71/255, 'green': 85/255, 'blue': 105/255}        # #475569
C_WHITE = {'red': 1, 'green': 1, 'blue': 1}
C_LIGHT_BG = {'red': 248/255, 'green': 250/255, 'blue': 252/255}   # #F8FAFC
C_ACCENT_BG = {'red': 239/255, 'green': 246/255, 'blue': 255/255}  # #EFF6FF (blue-50)


def get_creds():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_doc_structure(docs_service):
    """Get document structure to build targeted formatting requests."""
    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    body = doc.get('body', {})
    content = body.get('content', [])

    paragraphs = []
    for elem in content:
        if 'paragraph' in elem:
            p = elem['paragraph']
            start = p['elements'][0]['startIndex']
            end = p['elements'][-1]['endIndex']
            text = ''.join([e.get('textRun', {}).get('content', '') for e in p.get('elements', [])])
            style_type = p.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL_TEXT')
            paragraphs.append({
                'start': start,
                'end': end,
                'text': text.strip(),
                'style_type': style_type,
            })
    return paragraphs, doc


def build_design_requests(paragraphs, doc):
    """Build all formatting requests for Ziyada brand guidelines + RTL."""
    requests = []

    end_index = doc['body']['content'][-1].get('endIndex', 1)

    # ═══════════════════════════════════════
    # 1. SET ENTIRE DOCUMENT TO RTL
    # ═══════════════════════════════════════
    requests.append({
        'updateParagraphStyle': {
            'range': {'startIndex': 1, 'endIndex': end_index},
            'paragraphStyle': {
                'direction': 'RIGHT_TO_LEFT',
            },
            'fields': 'direction'
        }
    })

    # ═══════════════════════════════════════
    # 2. UPDATE NAMED STYLES (document-wide defaults)
    # ═══════════════════════════════════════
    requests.append({
        'updateDocumentStyle': {
            'documentStyle': {
                'background': {
                    'color': {'color': {'rgbColor': C_WHITE}}
                },
                'marginTop': {'magnitude': 50, 'unit': 'PT'},
                'marginBottom': {'magnitude': 50, 'unit': 'PT'},
                'marginLeft': {'magnitude': 60, 'unit': 'PT'},
                'marginRight': {'magnitude': 60, 'unit': 'PT'},
                'pageSize': {
                    'width': {'magnitude': 612, 'unit': 'PT'},
                    'height': {'magnitude': 792, 'unit': 'PT'},
                }
            },
            'fields': 'background,marginTop,marginBottom,marginLeft,marginRight,pageSize'
        }
    })

    # ═══════════════════════════════════════
    # 3. STYLE HEADINGS WITH BRAND COLORS
    # ═══════════════════════════════════════
    for p in paragraphs:
        start = p['start']
        end = p['end']
        text = p['text']
        style = p['style_type']

        if not text:
            continue

        # HEADING_1 — Main section headings (large, navy, bold)
        if style == 'HEADING_1':
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 26, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': C_NAVY}},
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            # Add spacing after heading
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'alignment': 'START',
                        'spaceAbove': {'magnitude': 24, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                        'borderBottom': {
                            'color': {'color': {'rgbColor': C_BLUE}},
                            'width': {'magnitude': 2, 'unit': 'PT'},
                            'padding': {'magnitude': 6, 'unit': 'PT'},
                            'dashStyle': 'SOLID',
                        }
                    },
                    'fields': 'direction,alignment,spaceAbove,spaceBelow,borderBottom'
                }
            })

        # HEADING_2 — Sub-section headings (blue, bold)
        elif style == 'HEADING_2':
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 20, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': C_BLUE}},
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'alignment': 'START',
                        'spaceAbove': {'magnitude': 18, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                    },
                    'fields': 'direction,alignment,spaceAbove,spaceBelow'
                }
            })

        # HEADING_3 — Step/item headings (light blue, bold)
        elif style == 'HEADING_3':
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 16, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': C_LIGHT_BLUE}},
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'alignment': 'START',
                        'spaceAbove': {'magnitude': 14, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 6, 'unit': 'PT'},
                        'indentStart': {'magnitude': 14, 'unit': 'PT'},
                    },
                    'fields': 'direction,alignment,spaceAbove,spaceBelow,indentStart'
                }
            })

    # ═══════════════════════════════════════
    # 4. STYLE BODY TEXT PARAGRAPHS
    # ═══════════════════════════════════════
    for p in paragraphs:
        start = p['start']
        end = p['end']
        text = p['text']
        style = p['style_type']

        if style != 'NORMAL_TEXT' or not text:
            continue

        # Separator lines (━━━) — make thin, blue, centered
        if text.startswith('━'):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 6, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_BLUE}},
                    },
                    'fields': 'fontSize,foregroundColor'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                        'spaceAbove': {'magnitude': 4, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 4, 'unit': 'PT'},
                    },
                    'fields': 'alignment,spaceAbove,spaceBelow'
                }
            })
            continue

        # Bullet items (  •  ) — indent and style
        if text.startswith('•'):
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'indentStart': {'magnitude': 28, 'unit': 'PT'},
                        'indentFirstLine': {'magnitude': 14, 'unit': 'PT'},
                        'spaceAbove': {'magnitude': 3, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 3, 'unit': 'PT'},
                        'lineSpacing': 130,
                    },
                    'fields': 'direction,indentStart,indentFirstLine,spaceAbove,spaceBelow,lineSpacing'
                }
            })
            continue

        # "المشكلة:" lines — muted color, slightly smaller
        if text.startswith('المشكلة:'):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 11, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_MUTED}},
                        'italic': True,
                    },
                    'fields': 'fontSize,foregroundColor,italic'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'indentStart': {'magnitude': 28, 'unit': 'PT'},
                        'spaceAbove': {'magnitude': 2, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'},
                    },
                    'fields': 'direction,indentStart,spaceAbove,spaceBelow'
                }
            })
            continue

        # "الحل:" lines — blue, emphasized
        if text.startswith('الحل:'):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 12, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_BLUE}},
                        'bold': True,
                    },
                    'fields': 'fontSize,foregroundColor,bold'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'indentStart': {'magnitude': 28, 'unit': 'PT'},
                        'spaceAbove': {'magnitude': 2, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'},
                    },
                    'fields': 'direction,indentStart,spaceAbove,spaceBelow'
                }
            })
            continue

        # "النتيجة:" lines — navy, bold
        if text.startswith('النتيجة:'):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 12, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_NAVY}},
                        'bold': True,
                    },
                    'fields': 'fontSize,foregroundColor,bold'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'indentStart': {'magnitude': 28, 'unit': 'PT'},
                        'spaceAbove': {'magnitude': 2, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 6, 'unit': 'PT'},
                    },
                    'fields': 'direction,indentStart,spaceAbove,spaceBelow'
                }
            })
            continue

        # "الفكرة:" lines — muted italic tip
        if text.startswith('الفكرة:'):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 10, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_MUTED}},
                        'italic': True,
                    },
                    'fields': 'fontSize,foregroundColor,italic'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'indentStart': {'magnitude': 36, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                    },
                    'fields': 'direction,indentStart,spaceBelow'
                }
            })
            continue

        # Package metadata ("المدة:", "مناسبة لـ:")
        if text.startswith(('المدة:', 'مناسبة لـ:')):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 11, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_MUTED}},
                        'italic': True,
                    },
                    'fields': 'fontSize,foregroundColor,italic'
                }
            })
            continue

        # "كل ما بالباقة" lines — blue highlight
        if text.startswith('كل ما بالباقة'):
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 13, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': C_BLUE}},
                        'bold': True,
                    },
                    'fields': 'fontSize,foregroundColor,bold'
                }
            })
            continue

        # Quote-like paragraphs (start with " or تخيل )
        if text.startswith(('"', 'تخيل', 'هذي نحن', 'نصيحة ذهبية')):
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'indentStart': {'magnitude': 24, 'unit': 'PT'},
                        'indentEnd': {'magnitude': 24, 'unit': 'PT'},
                        'borderLeft': {
                            'color': {'color': {'rgbColor': C_BLUE}},
                            'width': {'magnitude': 3, 'unit': 'PT'},
                            'padding': {'magnitude': 10, 'unit': 'PT'},
                            'dashStyle': 'SOLID',
                        },
                        'shading': {
                            'backgroundColor': {'color': {'rgbColor': C_ACCENT_BG}}
                        },
                        'spaceAbove': {'magnitude': 10, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 10, 'unit': 'PT'},
                    },
                    'fields': 'direction,indentStart,indentEnd,borderLeft,shading,spaceAbove,spaceBelow'
                }
            })
            continue

        # CTA / numbered steps (1.  2.  3.)
        if text and text[0].isdigit() and '.' in text[:4]:
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 14, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': C_NAVY}},
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'spaceAbove': {'magnitude': 6, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 6, 'unit': 'PT'},
                    },
                    'fields': 'direction,spaceAbove,spaceBelow'
                }
            })
            continue

        # Default body text — clean, readable
        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {
                    'direction': 'RIGHT_TO_LEFT',
                    'lineSpacing': 140,
                    'spaceAbove': {'magnitude': 3, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 3, 'unit': 'PT'},
                },
                'fields': 'direction,lineSpacing,spaceAbove,spaceBelow'
            }
        })

    # ═══════════════════════════════════════
    # 5. COVER PAGE — special styling
    # ═══════════════════════════════════════
    # Find the cover page title (first HEADING_1)
    for p in paragraphs:
        if p['style_type'] == 'HEADING_1' and 'دليل المبيعات' in p['text']:
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end'] - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 36, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': C_NAVY}},
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'direction': 'RIGHT_TO_LEFT',
                        'alignment': 'CENTER',
                        'spaceAbove': {'magnitude': 120, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                        'borderBottom': {
                            'color': {'color': {'rgbColor': C_BLUE}},
                            'width': {'magnitude': 3, 'unit': 'PT'},
                            'padding': {'magnitude': 12, 'unit': 'PT'},
                            'dashStyle': 'SOLID',
                        }
                    },
                    'fields': 'direction,alignment,spaceAbove,spaceBelow,borderBottom'
                }
            })
            break

    # "زيادة سيستم" subtitle — centered
    for p in paragraphs:
        if p['style_type'] == 'HEADING_2' and 'زيادة سيستم' in p['text']:
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end'] - 1},
                    'textStyle': {
                        'fontSize': {'magnitude': 24, 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': C_BLUE}},
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                        'spaceAbove': {'magnitude': 16, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 24, 'unit': 'PT'},
                    },
                    'fields': 'alignment,spaceAbove,spaceBelow'
                }
            })
            break

    # Cover subtitle "محل العطارة..."
    for p in paragraphs:
        if 'نموذج مبيعات 2026' in p['text']:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                    },
                    'fields': 'alignment'
                }
            })
            break

    # "Build once..." tagline — centered
    for p in paragraphs:
        if 'Build once.' in p['text']:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                    },
                    'fields': 'alignment'
                }
            })

    # Date line — centered
    for p in paragraphs:
        if 'تاريخ الوثيقة' in p['text']:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                    },
                    'fields': 'alignment'
                }
            })
            break

    # ═══════════════════════════════════════
    # 6. TOC HEADING — centered
    # ═══════════════════════════════════════
    for p in paragraphs:
        if 'فهرس المحتويات' in p['text']:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                        'spaceAbove': {'magnitude': 40, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 20, 'unit': 'PT'},
                    },
                    'fields': 'alignment,spaceAbove,spaceBelow'
                }
            })
            break

    # ═══════════════════════════════════════
    # 7. FOOTER — centered
    # ═══════════════════════════════════════
    for p in paragraphs:
        if '2026 ZIYADA SYSTEM' in p['text']:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                    },
                    'fields': 'alignment'
                }
            })
    for p in paragraphs:
        if 'للمزيد من المعلومات' in p['text']:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': p['start'], 'endIndex': p['end']},
                    'paragraphStyle': {
                        'alignment': 'CENTER',
                    },
                    'fields': 'alignment'
                }
            })

    return requests


def main():
    print("Applying Ziyada brand design + RTL formatting...")
    print("=" * 60)

    creds = get_creds()
    docs = build('docs', 'v1', credentials=creds)

    # Get document structure
    paragraphs, doc = get_doc_structure(docs)
    print(f"Found {len(paragraphs)} paragraphs")

    # Build formatting requests
    all_requests = build_design_requests(paragraphs, doc)
    print(f"Generated {len(all_requests)} formatting requests")

    # Apply in batches
    batch_size = 100
    for i in range(0, len(all_requests), batch_size):
        batch = all_requests[i:i + batch_size]
        docs.documents().batchUpdate(
            documentId=DOC_ID,
            body={'requests': batch}
        ).execute()
        print(f"  Batch {i // batch_size + 1} applied ({len(batch)} requests)")

    print()
    print("=" * 60)
    print("SUCCESS! Ziyada brand design applied.")
    print("=" * 60)
    print(f"\nLink: https://docs.google.com/document/d/{DOC_ID}/edit?usp=sharing")


if __name__ == '__main__':
    main()
