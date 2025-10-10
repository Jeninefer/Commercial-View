# Commercial-View Branch Conflict Resolution Script

Write-Host "🏦 Commercial-View Branch Conflict Resolution" -ForegroundColor Cyan
Write-Host "Current branch: fix-conflicts-and-secrets" -ForegroundColor Green
Write-Host "=" * 50

# Step 1: List all conflicted files
Write-Host "`n📋 Conflicted files:" -ForegroundColor Yellow
$conflictedFiles = git diff --name-only --diff-filter=U
foreach ($file in $conflictedFiles) {
    Write-Host "  - $file" -ForegroundColor Red
}

# Step 2: Resolve conflicts by choosing strategy
Write-Host "`n🔧 Conflict Resolution Strategy:" -ForegroundColor Green
Write-Host "1. Keep all remote changes (recommended for clean merge)"
Write-Host "2. Keep all local changes"
Write-Host "3. Remove deleted files completely"
Write-Host "4. Interactive resolution"

$choice = Read-Host "`nSelect option (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🔄 Accepting all remote changes..." -ForegroundColor Green

        # Accept remote version for content conflicts
        git checkout --theirs .gitignore
        git checkout --theirs execute_complete_resolution.py
        git checkout --theirs src/data_loader.py
        git checkout --theirs src/utils/retry.py
        git checkout --theirs src/utils/schema_parser.py

        # Accept remote version for modify/delete conflicts (keep the files)
        git add src/data_ingestion.py
        git add src/integrations.py
        git add src/kpi.py
        git add src/modeling.py
        git add src/utils/__init__.py
        git add src/utils/config_loader.py
        git add src/visualization.py

        # Add resolved files
        git add .gitignore execute_complete_resolution.py src/data_loader.py src/utils/retry.py src/utils/schema_parser.py

        Write-Host "✅ All conflicts resolved with remote changes" -ForegroundColor Green
    }
    "2" {
        Write-Host "`n🔄 Keeping all local changes..." -ForegroundColor Green

        # Keep local version for content conflicts
        git checkout --ours .gitignore
        git checkout --ours execute_complete_resolution.py
        git checkout --ours src/data_loader.py
        git checkout --ours src/utils/retry.py
        git checkout --ours src/utils/schema_parser.py

        # Remove files that were deleted locally
        git rm src/data_ingestion.py
        git rm src/integrations.py
        git rm src/kpi.py
        git rm src/modeling.py
        git rm src/utils/__init__.py
        git rm src/utils/config_loader.py
        git rm src/visualization.py

        # Add resolved files
        git add .gitignore execute_complete_resolution.py src/data_loader.py src/utils/retry.py src/utils/schema_parser.py

        Write-Host "✅ All conflicts resolved with local changes" -ForegroundColor Green
    }
    "3" {
        Write-Host "`n🗑️  Removing all conflicted files..." -ForegroundColor Yellow

        # Remove all conflicted files
        foreach ($file in $conflictedFiles) {
            git rm $file
            Write-Host "Removed: $file" -ForegroundColor Red
        }

        Write-Host "✅ All conflicted files removed" -ForegroundColor Green
    }
    "4" {
        Write-Host "`n🛠️  Starting interactive resolution..." -ForegroundColor Yellow
        Write-Host "You'll need to manually edit each file to resolve conflicts." -ForegroundColor Cyan
        Write-Host "Look for <<<<<<< HEAD, =======, and >>>>>>> markers." -ForegroundColor Cyan

        # Open each conflicted file in default editor
        foreach ($file in $conflictedFiles) {
            Write-Host "Opening: $file" -ForegroundColor Yellow
            Start-Process "code" -ArgumentList $file -Wait
        }

        Write-Host "After editing, add each resolved file with: git add <filename>" -ForegroundColor Cyan
        return
    }
    default {
        Write-Host "❌ Invalid option selected." -ForegroundColor Red
        return
    }
}

# Step 3: Complete the merge
Write-Host "`n📝 Committing resolution..." -ForegroundColor Green
git commit -m "Resolve merge conflicts: clean up Commercial-View project structure"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Conflicts resolved and committed!" -ForegroundColor Green

    # Step 4: Push the branch
    Write-Host "`n📤 Pushing branch..." -ForegroundColor Green
    git push origin fix-conflicts-and-secrets

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Branch pushed successfully!" -ForegroundColor Green
        Write-Host "`n🎯 Next steps:" -ForegroundColor Cyan
        Write-Host "1. Visit: https://github.com/Jeninefer/Commercial-View/pull/new/fix-conflicts-and-secrets"
        Write-Host "2. Create a Pull Request"
        Write-Host "3. Review and merge the PR"
        Write-Host "4. Delete this branch: git branch -d fix-conflicts-and-secrets"
    } else {
        Write-Host "❌ Push failed. Check the output above." -ForegroundColor Red
    }
} else {
    Write-Host "❌ Commit failed. Check for remaining conflicts." -ForegroundColor Red
}

Write-Host "`n📊 Current status:" -ForegroundColor Blue
git status --short
