#!/bin/bash

PORT=11434

# Vérifier si le port est utilisé
PID=$(lsof -ti tcp:$PORT)

if [ -n "$PID" ]; then
  echo "⚠️ Le port $PORT est déjà utilisé par le processus $PID. Arrêt en cours..."
  kill -9 $PID
  echo "✅ Processus $PID arrêté."
else
  echo "ℹ️ Le port $PORT est libre."
fi

# Relancer Ollama
echo "🚀 Démarrage de Ollama sur le port $PORT..."
OLLAMA_HOST=127.0.0.1:$PORT ollama serve
