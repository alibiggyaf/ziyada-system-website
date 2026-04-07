#!/bin/bash

# Ziyada Chat Widget Setup - Automated Script
# This script automates the entire setup process

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ZIYADA CHAT WIDGET - AUTOMATED SETUP (Gemini Flash)          ║"
echo "║  Cheapest model available: $0.075/1M input tokens             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
success() {
    echo -e "${GREEN}✓${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}→${NC} $1"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check for required tools
check_requirements() {
    step "Checking requirements"

    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
        exit 1
    fi
    success "Python 3 found"

    if ! command -v npm &> /dev/null; then
        error "npm is not installed"
        exit 1
    fi
    success "npm found"

    if ! command -v node &> /dev/null; then
        error "Node.js is not installed"
        exit 1
    fi
    success "Node.js found"
}

# Get Gemini API Key
get_gemini_key() {
    step "Getting Gemini API Key"

    echo ""
    echo "To get your free Gemini API key:"
    echo "  1. Visit: https://aistudio.google.com/app/apikey"
    echo "  2. Click 'Create API Key'"
    echo "  3. Copy the full API key"
    echo ""
    echo "Paste your Gemini API key (it will be hidden):"
    read -s GEMINI_KEY

    if [ -z "$GEMINI_KEY" ]; then
        error "No API key provided"
        exit 1
    fi

    success "Gemini API key received"
}

# Create N8N workflow
create_workflow() {
    step "Creating N8N Workflow"

    info "Running workflow setup script..."
    echo "$GEMINI_KEY" | python3 setup_gemini_chat.py

    if [ $? -eq 0 ]; then
        success "N8N workflow created"
    else
        error "Failed to create workflow"
        exit 1
    fi
}

# Update environment file
update_env() {
    step "Updating Environment Configuration"

    ENV_FILE="projects/ziyada-system/app/ziyada-system-website/.env.local"

    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file not found: $ENV_FILE"
        exit 1
    fi

    info "Current .env.local settings:"
    grep "VITE_CHATBOT" "$ENV_FILE" || true

    echo ""
    echo "Please enter your Webhook ID (from the setup output above):"
    echo "Format: 390b23bb-a7e4-48c4-8768-c3b89cc0ef36"
    read WEBHOOK_ID

    if [ -z "$WEBHOOK_ID" ]; then
        error "No webhook ID provided"
        exit 1
    fi

    # Update the .env.local file
    sed -i '' "s|VITE_CHATBOT_WEBHOOK=.*|VITE_CHATBOT_WEBHOOK=/n8n/webhook/$WEBHOOK_ID/chat|g" "$ENV_FILE"
    sed -i '' 's/VITE_CHATBOT_ENABLED=.*/VITE_CHATBOT_ENABLED=true/g' "$ENV_FILE"

    success ".env.local updated"
    info "Your webhook URL: /n8n/webhook/$WEBHOOK_ID/chat"
}

# Check files
verify_files() {
    step "Verifying Chat Widget Files"

    FILES=(
        "projects/ziyada-system/app/ziyada-system-website/src/components/ui/floating-chat-widget.jsx"
        "projects/ziyada-system/app/ziyada-system-website/.env.local"
        "projects/ziyada-system/app/ziyada-system-website/vite.config.js"
    )

    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            success "$file"
        else
            error "$file not found"
        fi
    done
}

# Install dependencies
install_deps() {
    step "Installing Dependencies"

    cd projects/ziyada-system/app/ziyada-system-website

    if [ ! -d "node_modules" ]; then
        info "Running npm install..."
        npm install --quiet
        success "Dependencies installed"
    else
        success "Dependencies already installed"
    fi

    cd - > /dev/null
}

# Quick test
test_setup() {
    step "Quick Test"

    echo ""
    echo "To test the setup manually:"
    echo ""
    echo "  1. Start the dev server:"
    echo "     cd projects/ziyada-system/app/ziyada-system-website"
    echo "     npm run dev"
    echo ""
    echo "  2. Open browser:"
    echo "     http://localhost:5173"
    echo ""
    echo "  3. Click the purple chat button (bottom-right)"
    echo "     and send a message"
    echo ""
    echo "  4. Monitor N8N workflow:"
    echo "     https://n8n.srv953562.hstgr.cloud/workflow/[WORKFLOW_ID]"
    echo "     Check 'Executions' tab for logs"
    echo ""
}

# Show summary
show_summary() {
    step "Setup Complete ✓"

    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 SETUP SUCCESSFUL! 🎉                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  Model:      Gemini Flash 2.0 (cheapest available)"
    echo "  Cost:       ~\$0.02/month for 1000 messages"
    echo "  Speed:      < 500ms response time"
    echo "  Quality:    Excellent for chat use cases"
    echo ""
    echo "📚 Documentation:"
    echo "   • QUICK_REFERENCE.md - Quick start guide"
    echo "   • CHAT_WIDGET_COMPLETE_GUIDE.md - Full documentation"
    echo "   • N8N_CHAT_WORKFLOW_SETUP.md - Detailed setup"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. cd projects/ziyada-system/app/ziyada-system-website"
    echo "   2. npm run dev"
    echo "   3. Open http://localhost:5173 in your browser"
    echo "   4. Click the chat button and test!"
    echo ""
    echo "📞 Having issues? Check the troubleshooting section in:"
    echo "   CHAT_WIDGET_COMPLETE_GUIDE.md"
    echo ""
}

# Main execution
main() {
    check_requirements
    get_gemini_key
    create_workflow
    install_deps
    update_env
    verify_files
    test_setup
    show_summary
}

# Run if script is executed (not sourced)
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main
fi
