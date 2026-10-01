$ErrorActionPreference = 'Stop'
$base = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $base 'data/reference/osrm'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$points = @(
    @{code='CNX';name='เชียงใหม่';lon=98.9853;lat=18.7883;region='North';share=0.35},
    @{code='BKK';name='กรุงเทพมหานคร';lon=100.5018;lat=13.7563;region='Central';share=0.15},
    @{code='KKC';name='ขอนแก่น';lon=102.8350;lat=16.4322;region='Northeast';share=0.10},
    @{code='KSN';name='กาฬสินธุ์';lon=103.5061;lat=16.4328;region='Northeast';share=0.08},
    @{code='SSK';name='ศรีสะเกษ';lon=104.3220;lat=15.1186;region='Northeast';share=0.07},
    @{code='NMA';name='นครราชสีมา';lon=102.0978;lat=14.9799;region='Northeast';share=0.06},
    @{code='UTH';name='อุดรธานี';lon=102.7930;lat=17.4138;region='Northeast';share=0.06},
    @{code='RET';name='ร้อยเอ็ด';lon=103.6520;lat=16.0538;region='Northeast';share=0.05},
    @{code='LPT';name='ลำปาง';lon=99.4937;lat=18.2888;region='North';share=0.04},
    @{code='RYG';name='ระยอง';lon=101.2816;lat=12.6814;region='East';share=0.04}
)
$rows = @()
foreach ($p in $points) {
    # Approximate city-centre endpoints, not the coordinates of a real warehouse.
    $coords = '104.8575,15.2448;{0},{1};104.8575,15.2448' -f $p.lon,$p.lat
    $url = 'https://router.project-osrm.org/route/v1/driving/' + $coords + '?overview=false&steps=false'
    $res = Invoke-RestMethod -Uri $url -TimeoutSec 40
    if ($res.code -ne 'Ok' -or $res.routes[0].legs.Count -ne 2) { throw 'Unexpected routing response' }
    $res | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath (Join-Path $outDir ($p.code+'.json')) -Encoding utf8
    $rows += [pscustomobject]@{
        code=$p.code;province=$p.name;region=$p.region;destination_share=$p.share;
        latitude=$p.lat;longitude=$p.lon;origin_latitude=15.2448;origin_longitude=104.8575;
        outbound_km=[math]::Round($res.routes[0].legs[0].distance/1000,3);
        return_km=[math]::Round($res.routes[0].legs[1].distance/1000,3);
        car_duration_hours=[math]::Round($res.routes[0].legs[0].duration/3600,4);
        reference_url=$url;reference_date='2026-10-02';
        distance_basis='OSRM car route estimate on OpenStreetMap, not observed truck mileage'
    }
    Write-Output ($p.code+': '+$rows[-1].outbound_km+' km')
    Start-Sleep -Milliseconds 1100
}
$rows | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $base 'data/reference/route_benchmarks.json') -Encoding utf8
