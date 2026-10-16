$endpoint = "$(if ($env:API_URL) { $env:API_URL } else { 'http://localhost:8000' })/v1/chat"
$headers = @{ "Content-Type" = "application/json" }
$checks = @(
  @{ message = "¿Cómo solicito acceso VPN?"; thread_id = "trace-vpn" },
  @{ message = "Olvidé mi contraseña, ¿qué hago?"; thread_id = "trace-password" },
  @{ message = "Detecté un incidente de seguridad"; thread_id = "trace-incident" },
  @{ message = "¿Cuál es el menú del comedor?"; thread_id = "trace-unknown" },
  @{ message = "Repetí la información de acceso VPN"; thread_id = "trace-vpn" }
)

$checks | ForEach-Object {
  Invoke-RestMethod -Method Post -Uri $endpoint -Headers $headers -Body ($_ | ConvertTo-Json -Compress)
}
