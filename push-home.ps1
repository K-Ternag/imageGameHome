$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Run from a normal PowerShell terminal with GitHub write credentials available.
# No force push, credential changes, or global Git configuration changes.
$expectedRemote = 'https://github.com/K-Ternag/imageGameHome.git'

function Invoke-ProjectGit {
    param([string[]]$GitArguments)
    & git -C $PSScriptRoot @GitArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git failed: $($GitArguments -join ' ')"
    }
}

Push-Location -LiteralPath $PSScriptRoot
try {
    python build_site.py
    if ($LASTEXITCODE -ne 0) { throw 'Site generation failed.' }
    python scripts/verify_site.py
    if ($LASTEXITCODE -ne 0) { throw 'Site verification failed.' }
    python scripts/verify_config.py
    if ($LASTEXITCODE -ne 0) { throw 'Configuration verification failed.' }

    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot '.git'))) {
        Invoke-ProjectGit -GitArguments @('init', '-b', 'main')
    }
    $existingRemote = & git config --get remote.origin.url
    if ($LASTEXITCODE -ne 0) {
        Invoke-ProjectGit -GitArguments @('remote', 'add', 'origin', $expectedRemote)
    } elseif ($existingRemote.TrimEnd('/') -ne $expectedRemote) {
        throw "Origin points to a different repository: $existingRemote"
    }

    $authorName = & git config user.name
    if (-not $authorName) {
        Invoke-ProjectGit -GitArguments @('config', 'user.name', 'K-Ternag')
    }
    $authorEmail = & git config user.email
    if (-not $authorEmail) {
        Invoke-ProjectGit -GitArguments @('config', 'user.email', '10904273+K-Ternag@users.noreply.github.com')
    }

    $remoteHeads = & git ls-remote --heads origin
    if ($LASTEXITCODE -ne 0) { throw 'Cannot connect to the remote repository.' }
    $localHead = & git rev-parse --verify --quiet HEAD
    $hasLocalHead = $LASTEXITCODE -eq 0
    if ($remoteHeads -and -not $hasLocalHead) {
        throw 'The remote now has history. Fetch and review it before importing this website.'
    }
    $branch = & git symbolic-ref --short HEAD
    if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') {
        throw 'Expected the main branch. Select the intended branch before publishing.'
    }
    if ($remoteHeads) {
        Invoke-ProjectGit -GitArguments @('fetch', 'origin', 'main')
        & git merge-base --is-ancestor origin/main HEAD
        if ($LASTEXITCODE -ne 0) { throw 'Remote history has changed. Review and integrate it before pushing.' }
    }

    Invoke-ProjectGit -GitArguments @('add', '--', '.gitignore', '.nojekyll', '.github', 'assets', 'scripts', '*.html', '*.css', '*.js', '*.json', '*.md', '*.py', '*.txt', '*.xml', 'push-home.ps1')
    Invoke-ProjectGit -GitArguments @('diff', '--cached', '--check')
    & git diff --cached --quiet
    $changes = $LASTEXITCODE
    if ($changes -gt 1) { throw 'Could not inspect staged changes.' }
    if ($changes -eq 1) {
        Invoke-ProjectGit -GitArguments @('commit', '-m', 'Build bilingual Photo Games website with policies and Pages deployment')
    }
    Invoke-ProjectGit -GitArguments @('push', '-u', 'origin', 'main')
    Invoke-ProjectGit -GitArguments @('status', '--short')
    Write-Output 'Published source: https://github.com/K-Ternag/imageGameHome'
} finally {
    Pop-Location
}
