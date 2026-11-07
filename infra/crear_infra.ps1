<#
  Crea la infraestructura Fabric de un proyecto (plan B de la demo "Paso 1. Crear la infraestructura").
    - Workspace de control:  <Proyecto>Control, con el lakehouse control (log y telemetría de las cargas)
    - Workspace de datos:    <Proyecto>, con los lakehouses bronze, silver y gold (con esquemas)
  Idempotente: si algo ya existe lo reutiliza, no lo borra ni lo recrea.

  Requisitos: az login --allow-no-subscriptions   (tenant sin suscripciones de Azure)
  Uso:        .\crear_infra.ps1 -Proyecto GreatAdventures [-Capacidad "<nombre o id>"]
#>
param(
    [Parameter(Mandatory)] [string] $Proyecto,
    [string] $Capacidad = "Trial-"   # prefijo del nombre o id de la capacidad
)
$ErrorActionPreference = 'Stop'
$api = 'https://api.fabric.microsoft.com/v1'

function Fabric([string]$Method, [string]$Path, $Body) {
    $a = @('rest', '--method', $Method, '--resource', 'https://api.fabric.microsoft.com', '--url', "$api$Path")
    if ($Body) {
        $f = New-TemporaryFile
        $Body | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding utf8 $f
        $a += @('--body', "@$f", '--headers', 'Content-Type=application/json')
    }
    $out = az @a 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Fallo en $Method $Path" }
    if ($out) { $out | ConvertFrom-Json }
}

$cap = (Fabric GET '/capacities').value |
    Where-Object { $_.state -eq 'Active' -and ($_.id -eq $Capacidad -or $_.displayName -like "$Capacidad*") } |
    Select-Object -First 1
if (-not $cap) { throw "No encuentro una capacidad activa que coincida con '$Capacidad'" }

function Get-Workspace([string]$Nombre) {
    $ws = (Fabric GET '/workspaces').value | Where-Object displayName -eq $Nombre
    if ($ws) { return @{ ws = $ws; estado = 'ya existía' } }
    $ws = Fabric POST '/workspaces' @{ displayName = $Nombre; capacityId = $cap.id }
    @{ ws = $ws; estado = 'creado' }
}

function Get-Lakehouse([string]$WsId, [string]$Nombre) {
    $lh = (Fabric GET "/workspaces/$WsId/lakehouses").value | Where-Object displayName -eq $Nombre
    $estado = 'ya existía'
    if (-not $lh) {
        Fabric POST "/workspaces/$WsId/lakehouses" @{ displayName = $Nombre; creationPayload = @{ enableSchemas = $true } } | Out-Null
        $estado = 'creado'
        for ($i = 0; $i -lt 20 -and -not $lh; $i++) {   # la creación es asíncrona
            Start-Sleep -Seconds 3
            $lh = (Fabric GET "/workspaces/$WsId/lakehouses").value | Where-Object displayName -eq $Nombre
        }
    }
    @{ lh = $lh; estado = $estado }
}

$res = @()
$ctl = Get-Workspace "${Proyecto}Control"
$res += [pscustomobject]@{ Tipo = 'Workspace'; Nombre = $ctl.ws.displayName; Estado = $ctl.estado; Id = $ctl.ws.id; OneLake = '' }
$r = Get-Lakehouse $ctl.ws.id 'control'
$res += [pscustomobject]@{
    Tipo = 'Lakehouse'; Nombre = "${Proyecto}Control/control"; Estado = $r.estado; Id = $r.lh.id
    OneLake = "abfss://$($ctl.ws.id)@onelake.dfs.fabric.microsoft.com/$($r.lh.id)"
}

$dat = Get-Workspace $Proyecto
$res += [pscustomobject]@{ Tipo = 'Workspace'; Nombre = $dat.ws.displayName; Estado = $dat.estado; Id = $dat.ws.id; OneLake = '' }

foreach ($capa in 'bronze', 'silver', 'gold') {
    $r = Get-Lakehouse $dat.ws.id $capa
    $res += [pscustomobject]@{
        Tipo = 'Lakehouse'; Nombre = "$Proyecto/$capa"; Estado = $r.estado; Id = $r.lh.id
        OneLake = "abfss://$($dat.ws.id)@onelake.dfs.fabric.microsoft.com/$($r.lh.id)"
    }
}

"Capacidad: $($cap.displayName) ($($cap.sku), $($cap.region))"
$res | Format-Table -AutoSize -Wrap
