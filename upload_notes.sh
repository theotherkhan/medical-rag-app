#!/bin/bash

# Function to upload a single note
upload_note() {
    local file=$1
    local title=$(basename "$file" .txt)
    local content=$(cat "$file")
    
    curl -X POST http://localhost:8000/documents/ \
    -H "Content-Type: application/json" \
    -d "{
        \"title\": \"$title\",
        \"content\": $(echo "$content" | jq -Rs .)
    }"
    echo -e "\n"
}

# Upload each SOAP note
for file in medical_notes/soap_note_*.txt; do
    echo "Uploading $file..."
    upload_note "$file"
done 