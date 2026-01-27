---
description: Install Python package with auto-freeze to requirements.txt
---

# Install Package Workflow

This workflow ensures that every package installation automatically updates `requirements.txt`.

## Steps

1. **Navigate to project root**
   ```powershell
   cd e:\JOB\ini-sebuah-event
   ```

2. **Use the install script instead of pip directly**
   
   For PowerShell:
   ```powershell
   .\scripts\install.ps1 package-name
   ```
   
   For Command Prompt:
   ```cmd
   scripts\install.bat package-name
   ```

3. **Verify requirements.txt was updated**
   ```powershell
   git diff requirements.txt
   ```

## Examples

Install single package:
```powershell
.\scripts\install.ps1 requests
```

Install multiple packages:
```powershell
.\scripts\install.ps1 requests pandas numpy
```

## Important Notes

- ⚠️ Always use the install script, not `pip install` directly
- ✅ The script will automatically run `pip freeze > requirements.txt`
- ✅ Only updates if installation succeeds
- 📝 Share this workflow with your team
