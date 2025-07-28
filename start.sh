#!/usr/bin/env bash

# 1. Aktywacja środowiska
echo "▶️ Aktywuję środowisko virtualne..."
source venv/bin/activate

# 2. Uruchomienie serwera FastAPI
echo "🚀 Startuję backend (Uvicorn) na porcie 8000..."
nohup uvicorn main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &

# 3. Czekamy chwilę aż serwer ruszy
sleep 3

# 4. Uruchomienie Ngrok i pokazanie publicznego URL-a
echo "🌍 Startuję ngrok..."
nohup ngrok http 8000 > ngrok.log 2>&1 &

sleep 2

# 5. Wyciągamy publiczny URL ngroka
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o 'https://[a-z0-9\-]*\.ngrok-free\.app')

if [ -n "$NGROK_URL" ]; then
  echo "✅ Twój publiczny URL ngrok to: $NGROK_URL"
  echo "👉 Wklej go jako endpoint do agenta GPT."
else
  echo "❌ Nie udało się uzyskać URL z ngroka. Sprawdź log: ngrok.log"
fi
