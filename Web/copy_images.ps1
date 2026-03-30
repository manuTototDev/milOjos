
$src      = "c:\Users\manu\Documents\Jovenes creadores\Dev\produccion\fcaesDes"
$dstFotos = "c:\Users\manu\Documents\Jovenes creadores\Web\backend\static\fotos_recortadas"
$dstBols  = "c:\Users\manu\Documents\Jovenes creadores\Web\backend\static\boletines"
$years    = @("2020","2021","2022","2023","2024","2025","2026")

foreach ($year in $years) {
    # --- Fotos recortadas ---
    $srcFotos = Join-Path $src "$year\fotos_recortadas"
    if (Test-Path $srcFotos) {
        $files = Get-ChildItem $srcFotos -Filter "*.jpg"
        $copied = 0
        foreach ($f in $files) {
            $destName = $year + "_" + $f.Name
            $destPath = Join-Path $dstFotos $destName
            if (-not (Test-Path $destPath)) {
                Copy-Item $f.FullName $destPath
                $copied++
            }
        }
        Write-Host "Fotos $year`: $copied nuevas (total $($files.Count))"
    }

    # --- Boletines completos ---
    $srcBols = Join-Path $src "$year\boletines_completos"
    if (Test-Path $srcBols) {
        $files = Get-ChildItem $srcBols -Filter "*.jpg"
        $copied = 0
        foreach ($f in $files) {
            $destName = $year + "_" + $f.Name
            $destPath = Join-Path $dstBols $destName
            if (-not (Test-Path $destPath)) {
                Copy-Item $f.FullName $destPath
                $copied++
            }
        }
        Write-Host "Boletines $year`: $copied nuevas (total $($files.Count))"
    }
}

Write-Host ""
Write-Host "=== RESUMEN FINAL ==="
$totalFotos = (Get-ChildItem $dstFotos -Filter "*.jpg" | Measure-Object).Count
$totalBols  = (Get-ChildItem $dstBols  -Filter "*.jpg" | Measure-Object).Count
Write-Host "Fotos recortadas: $totalFotos"
Write-Host "Boletines:        $totalBols"
Write-Host "LISTO."
