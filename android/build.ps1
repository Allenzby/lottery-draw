# 构建安卓 APK（不需要 Android Studio / Gradle）
# 依赖：JDK 17+（javac/keytool）、Android build-tools、Android platform(android.jar)
#
# 用法：  powershell -ExecutionPolicy Bypass -File android\build.ps1
#        powershell -ExecutionPolicy Bypass -File android\build.ps1 -Version 1.2 -VersionCode 3
#
# 注意：aapt2 不支持含中文的路径，所以先复制到 %TEMP%\lottery-android 里构建，
#       最后再把 APK 拷回项目目录。

param(
    [string]$Version = "1.1",
    [int]$VersionCode = 2,
    [string]$Sdk = "C:\Users\Administrator\AppData\Local\android-sdk",
    [string]$KeystorePass = "lotterydraw"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$BT = Join-Path $Sdk "android-14"            # build-tools 34
$AndroidJar = Join-Path $Sdk "android-35\android.jar"
$Stage = Join-Path $env:TEMP "lottery-android"
$OutApk = Join-Path (Split-Path $Root -Parent) ("摇号软件-v" + $Version + ".apk")
$Ks = Join-Path $Root "lottery-release.jks"
$KsAlias = "lottery"

foreach ($p in @("$BT\aapt2.exe", "$BT\d8.bat", "$BT\apksigner.bat",
                 "$BT\zipalign.exe", $AndroidJar)) {
    if (-not (Test-Path $p)) { throw "缺少构建工具：$p" }
}

if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
New-Item -ItemType Directory $Stage | Out-Null

Copy-Item (Join-Path $Root "AndroidManifest.xml") $Stage
Copy-Item (Join-Path $Root "res") $Stage -Recurse
Copy-Item (Join-Path $Root "assets") $Stage -Recurse
Copy-Item (Join-Path $Root "java") $Stage -Recurse

Write-Host "[1/7] 编译资源 ..."
& "$BT\aapt2.exe" compile --dir (Join-Path $Stage "res") -o (Join-Path $Stage "res.zip")
if ($LASTEXITCODE -ne 0) { throw "aapt2 compile 失败" }

Write-Host "[2/7] 链接资源 + 清单 + assets ..."
& "$BT\aapt2.exe" link -o (Join-Path $Stage "base.apk") `
    -I $AndroidJar `
    --manifest (Join-Path $Stage "AndroidManifest.xml") `
    -R (Join-Path $Stage "res.zip") `
    -A (Join-Path $Stage "assets") `
    --min-sdk-version 21 --target-sdk-version 34 `
    --version-code $VersionCode --version-name $Version `
    --auto-add-overlay
if ($LASTEXITCODE -ne 0) { throw "aapt2 link 失败" }

Write-Host "[3/7] 编译 Java ..."
$classes = Join-Path $Stage "classes"
New-Item -ItemType Directory $classes | Out-Null
$javaFiles = @(Get-ChildItem (Join-Path $Stage "java") -Recurse -Filter *.java |
    ForEach-Object { $_.FullName })
& javac -encoding UTF-8 -source 8 -target 8 -nowarn `
    -bootclasspath $AndroidJar -d $classes @javaFiles
if ($LASTEXITCODE -ne 0) { throw "javac 失败" }

Write-Host "[4/7] 转换为 dex ..."
$dexDir = Join-Path $Stage "dex"
New-Item -ItemType Directory $dexDir | Out-Null
$classFiles = @(Get-ChildItem $classes -Recurse -Filter *.class |
    ForEach-Object { $_.FullName })
& "$BT\d8.bat" --release --lib $AndroidJar --min-api 21 --output $dexDir @classFiles
if ($LASTEXITCODE -ne 0) { throw "d8 失败" }

Write-Host "[5/7] 打包 classes.dex ..."
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$apk = Join-Path $Stage "base.apk"
$zip = [System.IO.Compression.ZipFile]::Open($apk, [System.IO.Compression.ZipArchiveMode]::Update)
try {
    $entry = $zip.CreateEntry("classes.dex", [System.IO.Compression.CompressionLevel]::Optimal)
    $src = [System.IO.File]::OpenRead((Join-Path $dexDir "classes.dex"))
    try {
        $dst = $entry.Open()
        $src.CopyTo($dst)
        $dst.Dispose()
    } finally { $src.Dispose() }
} finally { $zip.Dispose() }

Write-Host "[6/7] 对齐 ..."
$aligned = Join-Path $Stage "aligned.apk"
& "$BT\zipalign.exe" -f 4 $apk $aligned
if ($LASTEXITCODE -ne 0) { throw "zipalign 失败" }

Write-Host "[7/7] 签名 ..."
if (-not (Test-Path $Ks)) {
    Write-Host "首次构建，生成签名密钥：$Ks（请备份，后续升级要用同一个）"
    & keytool -genkeypair -keystore $Ks -alias $KsAlias -keyalg RSA -keysize 2048 `
        -validity 10000 -storepass $KeystorePass -keypass $KeystorePass `
        -dname "CN=Lottery Draw, OU=Mobile, O=Allenzby, L=Beijing, ST=Beijing, C=CN"
    if ($LASTEXITCODE -ne 0) { throw "keytool 失败" }
}

$signed = Join-Path $Stage "signed.apk"
& "$BT\apksigner.bat" sign --ks $Ks --ks-key-alias $KsAlias `
    --ks-pass "pass:$KeystorePass" --key-pass "pass:$KeystorePass" `
    --out $signed $aligned
if ($LASTEXITCODE -ne 0) { throw "apksigner 签名失败" }

& "$BT\apksigner.bat" verify --print-certs $signed | Select-Object -First 3

Copy-Item $signed $OutApk -Force
Write-Host ""
Write-Host "完成：$OutApk"
$mb = [math]::Round((Get-Item $OutApk).Length / 1MB, 1)
Write-Host ("大小：" + $mb + " MB")
