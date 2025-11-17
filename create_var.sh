#!/bin/bash

# Create required configuration files for Dropbox Automater
# Run this script before using the automater to set up your session data

echo "Creating required configuration files..."

# Create cookies.txt
if [ ! -f "cookies.txt" ]; then
    echo "[]" > cookies.txt
    echo "✓ Created cookies.txt (empty - please export your cookies using EditThisCookie extension)"
else
    echo "⊘ cookies.txt already exists, skipping..."
fi

# Create localstorage.json
if [ ! -f "localstorage.json" ]; then
    echo "{}" > localstorage.json
    echo "✓ Created localstorage.json (empty - please export using: copy(JSON.stringify(localStorage)))"
else
    echo "⊘ localstorage.json already exists, skipping..."
fi

# Create sessionstorage.json
if [ ! -f "sessionstorage.json" ]; then
    echo "{}" > sessionstorage.json
    echo "✓ Created sessionstorage.json (empty - please export using: copy(JSON.stringify(sessionStorage)))"
else
    echo "⊘ sessionstorage.json already exists, skipping..."
fi

# Create useragent.txt
if [ ! -f "useragent.txt" ]; then
    echo "Mozilla/5.0 (replace with your actual user agent from navigator.userAgent)" > useragent.txt
    echo "✓ Created useragent.txt (placeholder - please replace with your actual user agent)"
else
    echo "⊘ useragent.txt already exists, skipping..."
fi

echo ""
echo "============================================"
echo "Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Follow the instructions in HOW_TO_USE.md to export your session data"
echo "2. Fill in the created files with your exported data"
echo "3. Run: python main.py"
echo ""
