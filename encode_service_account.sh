#!/bin/bash

# Script to encode service account JSON for GitHub secrets

echo "🔐 Service Account Encoder for GitHub Secrets"
echo "==========================================="

# Check if service account file exists
SERVICE_ACCOUNT_FILE=".credentials/google-drive-service-account.json"

if [ ! -f "$SERVICE_ACCOUNT_FILE" ]; then
    echo "❌ Error: Service account file not found at $SERVICE_ACCOUNT_FILE"
    exit 1
fi

echo "✅ Found service account file"

# Encode the file
echo "🔄 Encoding service account..."
ENCODED=$(base64 -i "$SERVICE_ACCOUNT_FILE" | tr -d '\n')

# Save to temporary file
TEMP_FILE="service-account-encoded.txt"
echo "$ENCODED" > "$TEMP_FILE"

echo "✅ Encoded service account saved to: $TEMP_FILE"
echo ""
echo "📋 Next steps:"
echo "1. Copy the content of $TEMP_FILE"
echo "2. Go to: https://github.com/udhaya10/BlueDot-Trading-System/settings/secrets/actions"
echo "3. Click 'New repository secret'"
echo "4. Name: GOOGLE_DRIVE_SERVICE_ACCOUNT"
echo "5. Value: Paste the encoded content"
echo "6. Click 'Add secret'"
echo ""
echo "🧹 After adding the secret, delete the temporary file:"
echo "   rm $TEMP_FILE"
echo ""

# Try to copy to clipboard if possible
if command -v pbcopy &> /dev/null; then
    cat "$TEMP_FILE" | pbcopy
    echo "✅ Encoded content copied to clipboard!"
elif command -v xclip &> /dev/null; then
    cat "$TEMP_FILE" | xclip -selection clipboard
    echo "✅ Encoded content copied to clipboard!"
else
    echo "📝 Open $TEMP_FILE and copy the content manually"
fi