# scripts/release-finish.ps1
# 用法：
#   .\scripts\release-finish.ps1                 # 在 release/<ver> 分支上时自动解析 ver
#   .\scripts\release-finish.ps1 -v 2.0.0-beta.10
#   .\scripts\release-finish.ps1 -v 2.0.0-beta.10 -r origin -m tauri -d dev

[CmdletBinding()]
param(
  [Alias('v')]
  [string]$Version,

  [Alias('r')]
  [string]$Remote = "origin",

  [Alias('m')]
  [string]$MainBranch = "tauri",

  [Alias('d')]
  [string]$DevBranch  = "dev"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail([string]$msg, [int]$code = 1) {
  Write-Host "❌ $msg" -ForegroundColor Red
  exit $code
}

# 0) 确认在 git 仓库
& git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { Fail "当前目录不是 git 仓库（git rev-parse 失败）" 2 }

# 1) 工作区必须干净（含 untracked）
$status = & git status --porcelain
if ($LASTEXITCODE -ne 0) { Fail "无法读取 git status" 3 }
if ($status) {
  Write-Host "当前工作区不干净（git status --porcelain 有输出），请先 commit/stash/clean 后再运行：" -ForegroundColor Yellow
  $status | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
  Fail "中断：工作区不干净" 20
}

# 2) 当前分支必须是 release/*
$branch = (& git rev-parse --abbrev-ref HEAD).Trim()
if (-not $branch) { Fail "无法获取当前分支名" 4 }

if ($branch -notlike "release/*") {
  Fail "当前分支不是 release/*（现在是 '$branch'）。请切到 release/<版本> 分支再运行。" 10
}

$curVer = $branch.Substring("release/".Length)
if ([string]::IsNullOrWhiteSpace($curVer)) {
  Fail "分支名 '$branch' 无法解析出版本号（预期形如 release/2.0.0-beta.10）" 11
}

# 3) Version 可选：没传则用分支名；传了必须与分支一致
if ([string]::IsNullOrWhiteSpace($Version)) {
  $Version = $curVer
} else {
  if ($Version -ne $curVer) {
    Fail "你传入的 -v/-Version 是 '$Version'，但当前分支是 '$branch'（版本 '$curVer'）。两者不一致，已中断。" 12
  }
}

# 预检查：本地/远程 tag 是否已存在（存在则中断）
# 约定：git-flow release finish <Version> 会创建 tag "v<Version>"
$expectedTag = if ($Version -match '^[vV]') { $Version } else { "v$Version" }
$expectedRef = "refs/tags/$expectedTag"

# 本地 tag 检查
& git show-ref --tags --verify --quiet $expectedRef
if ($LASTEXITCODE -eq 0) {
  Fail "本地已存在 tag：$expectedTag（$expectedRef）。请更换版本号或先删除该 tag 后再试。" 30
}

# 远程 tag 检查（同时查轻量/附注 tag 的对象解引用）
$remoteHit = & git ls-remote --tags $Remote $expectedRef "$expectedRef^{}"
if ($LASTEXITCODE -ne 0) {
  Fail "无法查询远程 tag：git ls-remote --tags $Remote ...（请检查远程名/网络/权限）" 31
}
if ($remoteHit) {
  Fail "远程 '$Remote' 已存在 tag：$expectedTag。请更换版本号，或在远程删除该 tag 后再试。" 32
}

Write-Host "▶ 当前分支: $branch"
Write-Host "▶ 将执行: git-flow release finish $Version"
Write-Host "▶ 完成后推送: $Remote $MainBranch $DevBranch + (HEAD tag if exists)"

# 4) 执行 finish
& git-flow release finish $Version
if ($LASTEXITCODE -ne 0) { Fail "git-flow release finish 失败（exit=$LASTEXITCODE）" $LASTEXITCODE }

# 5) 推送主分支/开发分支
& git push $Remote $MainBranch $DevBranch
if ($LASTEXITCODE -ne 0) { Fail "推送分支失败：git push $Remote $MainBranch $DevBranch" $LASTEXITCODE }

# 6) 只推 HEAD 上的 tag
$tag = (& git describe --tags --exact-match 2>$null).Trim()
if ($tag) {
  & git push $Remote "refs/tags/$tag"
  if ($LASTEXITCODE -ne 0) { Fail "推送 tag 失败：git push $Remote refs/tags/$tag" $LASTEXITCODE }
  Write-Host "✅ 已推送 tag: $tag"
} else {
  Write-Host "ℹ️ HEAD 上没有 tag，跳过 tag push"
}

Write-Host "✅ 完成"
