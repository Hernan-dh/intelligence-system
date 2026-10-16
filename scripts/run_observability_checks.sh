#!/usr/bin/env sh
set -eu

endpoint="${API_URL:-http://localhost:8000}/v1/chat"
send() {
  curl --fail --silent --show-error -X POST "$endpoint" \
    -H 'Content-Type: application/json' \
    -d "$1"
  printf '\n'
}

send '{"message":"¿Cómo solicito acceso VPN?","thread_id":"trace-vpn"}'
send '{"message":"Olvidé mi contraseña, ¿qué hago?","thread_id":"trace-password"}'
send '{"message":"Detecté un incidente de seguridad","thread_id":"trace-incident"}'
send '{"message":"¿Cuál es el menú del comedor?","thread_id":"trace-unknown"}'
send '{"message":"Repetí la información de acceso VPN","thread_id":"trace-vpn"}'
