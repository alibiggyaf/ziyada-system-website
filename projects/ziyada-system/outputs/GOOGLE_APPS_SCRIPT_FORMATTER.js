// ============================================================================
// ZIYADA SYSTEM - Google Docs Auto-Formatter
// ============================================================================
// This script will automatically format your sales guide document
// with Ziyada brand colors and professional styling
// ============================================================================

function formatSalesGuide() {
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody();
  const paragraphs = body.getParagraphs();

  // Color definitions (Ziyada Brand)
  const PRIMARY_BLUE = '#2563eb';    // Main headings
  const LIGHT_BLUE = '#3b82f6';      // Secondary elements
  const DARK_NAVY = '#0f172a';       // Body text

  Logger.log('📘 Starting Ziyada Sales Guide Formatter...');
  Logger.log(`Total paragraphs: ${paragraphs.length}`);

  let formatted = 0;

  for (let i = 0; i < paragraphs.length; i++) {
    const para = paragraphs[i];
    const text = para.getText().trim();

    // Skip empty paragraphs
    if (!text) continue;

    // ========================================================================
    // RULE 1: Main Section Headers (like "01 | محل العطارة")
    // ========================================================================
    if (text.match(/^\d{1,2}\s*\|/) && text.length < 100) {
      try {
        para.setHeading(DocumentApp.ParagraphHeading.HEADING1);

        const editText = para.editAsText();
        editText.setFontSize(0, text.length, 28);
        editText.setBold(0, text.length, true);
        editText.setForegroundColor(0, text.length, PRIMARY_BLUE);

        // Add bottom border
        para.setBorderBottom(DocumentApp.BorderStyle.SOLID, 2, LIGHT_BLUE);

        Logger.log(`✅ Formatted main header: ${text.substring(0, 30)}...`);
        formatted++;
      } catch (e) {
        Logger.log(`⚠️  Error formatting: ${text.substring(0, 30)}`);
      }
    }

    // ========================================================================
    // RULE 2: Section Subtitles (مقدمة, الخدمات, etc)
    // ========================================================================
    else if (
      (text.match(/^(مقدمة|أرقام|الخدمات|خطوات|لماذا|التحديات|الحل|الباقات|تواصل|لماذا|العرض|خطواتك)/) && text.length < 80) ||
      text.match(/^(مقدمة|المحل|الأولوية):.+/)
    ) {
      try {
        para.setHeading(DocumentApp.ParagraphHeading.HEADING2);

        const editText = para.editAsText();
        editText.setFontSize(0, text.length, 20);
        editText.setBold(0, text.length, true);
        editText.setForegroundColor(0, text.length, PRIMARY_BLUE);

        Logger.log(`✅ Formatted subtitle: ${text.substring(0, 30)}...`);
        formatted++;
      } catch (e) {
        Logger.log(`⚠️  Error formatting subtitle`);
      }
    }

    // ========================================================================
    // RULE 3: Step Headers (الخطوة الأولى, التحدي 1, etc)
    // ========================================================================
    else if (
      text.match(/^الخطوة\s+(الأولى|الثانية|الثالثة|الرابعة|الخامسة)/) ||
      text.match(/^التحدي\s+\d+:/)
    ) {
      try {
        para.setHeading(DocumentApp.ParagraphHeading.HEADING3);

        const editText = para.editAsText();
        editText.setFontSize(0, text.length, 18);
        editText.setBold(0, text.length, true);
        editText.setForegroundColor(0, text.length, PRIMARY_BLUE);

        Logger.log(`✅ Formatted step: ${text.substring(0, 30)}...`);
        formatted++;
      } catch (e) {
        Logger.log(`⚠️  Error formatting step`);
      }
    }

    // ========================================================================
    // RULE 4: Body Text - Ensure proper formatting
    // ========================================================================
    else if (text.length > 20 && !text.match(/^•|^\+|^-/)) {
      try {
        const editText = para.editAsText();
        editText.setFontSize(0, text.length, 14);
        editText.setForegroundColor(0, text.length, DARK_NAVY);

      } catch (e) {
        // Silent fail for body text
      }
    }
  }

  // ========================================================================
  // Format Tables
  // ========================================================================
  const tables = body.getTables();
  Logger.log(`📊 Found ${tables.length} tables`);

  for (let t = 0; t < tables.length; t++) {
    const table = tables[t];
    const rows = table.getNumRows();

    for (let r = 0; r < rows; r++) {
      const row = table.getRow(r);
      const cells = row.getNumCells();

      for (let c = 0; c < cells; c++) {
        const cell = row.getCell(c);
        const cellText = cell.editAsText();

        // Format header row
        if (r === 0) {
          cellText.setFontSize(0, cellText.getText().length, 13);
          cellText.setBold(0, cellText.getText().length, true);
          cellText.setForegroundColor(0, cellText.getText().length, '#ffffff');
          cell.setBackgroundColor(PRIMARY_BLUE);
        } else {
          // Alternate row colors
          if (r % 2 === 0) {
            cell.setBackgroundColor('#f8fafc');
          }
          cellText.setFontSize(0, cellText.getText().length, 13);
          cellText.setForegroundColor(0, cellText.getText().length, DARK_NAVY);
        }
      }
    }
  }

  // ========================================================================
  // Final Setup
  // ========================================================================

  // Set default margins
  const pageMargins = {
    top: 0.75,
    bottom: 0.75,
    left: 0.75,
    right: 0.75
  };

  body.setMarginTop(pageMargins.top * 72);
  body.setMarginBottom(pageMargins.bottom * 72);
  body.setMarginLeft(pageMargins.left * 72);
  body.setMarginRight(pageMargins.right * 72);

  // ========================================================================
  // Complete!
  // ========================================================================

  Logger.log('\n' + '='.repeat(70));
  Logger.log('✅ FORMATTING COMPLETE!');
  Logger.log('='.repeat(70));
  Logger.log(`📊 Formatted elements: ${formatted}`);
  Logger.log(`📋 Tables processed: ${tables.length}`);
  Logger.log('🎨 Colors applied: Ziyada Brand Colors');
  Logger.log('📐 Margins set: 0.75 inches');
  Logger.log('\n✨ Your document is now professionally formatted!');
  Logger.log('Check your Google Doc and enjoy the new look!\n');

  // Show completion dialog
  DocumentApp.getUi().alert(
    '✅ تم التنسيق بنجاح!\n\n' +
    'Formatting Complete!\n\n' +
    `Formatted: ${formatted} elements\n` +
    `Tables: ${tables.length}\n\n` +
    'Your document is ready to share with your sales team! 🎉'
  );
}

// ============================================================================
// Helper Function: Remove all manual formatting and start fresh
// ============================================================================

function resetDocument() {
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody();
  const paragraphs = body.getParagraphs();

  Logger.log('🔄 Resetting document formatting...');

  for (let i = 0; i < paragraphs.length; i++) {
    const para = paragraphs[i];
    const editText = para.editAsText();

    // Reset all formatting to default
    editText.setFontSize(0, editText.getText().length, 11);
    editText.setForegroundColor(0, editText.getText().length, '#000000');
    editText.setBold(0, editText.getText().length, false);
    editText.setItalic(0, editText.getText().length, false);
    editText.setUnderline(0, editText.getText().length, false);

    para.setHeading(DocumentApp.ParagraphHeading.NORMAL);
    para.setAlignment(DocumentApp.HorizontalAlignment.RIGHT); // RTL for Arabic
  }

  Logger.log('✅ Document reset complete!');
  DocumentApp.getUi().alert('✅ Document reset to default formatting.');
}

// ============================================================================
// Run from menu or execute directly
// ============================================================================

function onOpen(e) {
  DocumentApp.getUi()
    .createMenu('Ziyada Formatter')
    .addItem('Format Sales Guide', 'formatSalesGuide')
    .addItem('Reset Formatting', 'resetDocument')
    .addToUi();
}
