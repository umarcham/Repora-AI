# API Curl Examples

## 1. Upload Document
```bash
curl -X POST -F "file=@/path/to/my_doc.docx" http://localhost:5000/upload
```
**Response:**
```json
{
  "document_id": "1702377012345",
  "structure": { ... }
}
```

## 2. Edit Document
```bash
curl -X POST http://localhost:5000/doc/1702377012345/edit \
     -H "Content-Type: application/json" \
     -d '{
           "instruction": "Replace Acme with AcmeCorp",
           "context": null
         }'
```
**Response:**
```json
{
  "status": "ok",
  "preview_html_url": "...",
  "docx_download_url": "...",
  "changes": ["Replaced 5 occurrences..."]
}
```

## 3. Apply Manual Edits (Optional)
If you have a modified structure JSON:
```bash
curl -X POST http://localhost:5000/doc/1702377012345/apply \
     -H "Content-Type: application/json" \
     -d '{
           "structure": { ... }
         }'
```

## 4. Download Revision
```bash
curl -O http://localhost:5000/doc/1702377012345/download/1702377099999
```
