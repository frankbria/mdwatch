#!/bin/bash
# Simulates a showboat demo being built incrementally.
# Run this in one terminal while mdwatch watches the file in another.
# Usage: ./scripts/simulate_demo.sh /tmp/test-demo.md

FILE="${1:-/tmp/test-demo.md}"
rm -f "$FILE"

echo "Simulating showboat demo → $FILE"
echo "Start mdwatch in another terminal: uv run mdwatch $FILE"
echo ""
sleep 2

# showboat init
cat > "$FILE" << 'EOF'
# Authentication Feature Demo

*2026-03-04T14:30:00Z*
EOF
echo "[+] Init: title + timestamp"
sleep 3

# showboat note
cat >> "$FILE" << 'EOF'

Let's verify the login page renders correctly with the new auth flow.
EOF
echo "[+] Note: narrative"
sleep 3

# showboat exec
cat >> "$FILE" << 'EOF'

```bash
curl -s http://localhost:3000/login | head -5
```

```output
<!DOCTYPE html>
<html lang="en">
<head><title>Login - MyApp</title></head>
<body>
<div id="login-form">
```
EOF
echo "[+] Exec: curl + output"
sleep 3

# showboat note
cat >> "$FILE" << 'EOF'

The login form is rendering. Now let's test the authentication endpoint.
EOF
echo "[+] Note: narrative"
sleep 3

# showboat exec
cat >> "$FILE" << 'EOF'

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret"}'
```

```output
{"token":"eyJhbGciOiJIUzI1NiJ9...","user":{"id":"123","email":"test@example.com"}}
```
EOF
echo "[+] Exec: auth test + output"
sleep 3

# showboat image
cat >> "$FILE" << 'EOF'

```bash
agent-browser screenshot login-page.png && echo login-page.png
```

![Login Page](login-page.png)
EOF
echo "[+] Image: screenshot reference"
sleep 3

# showboat note
cat >> "$FILE" << 'EOF'

---

All authentication tests passed. The login flow works correctly with proper token generation.
EOF
echo "[+] Final note with HR"

echo ""
echo "Demo simulation complete!"
