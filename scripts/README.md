# Auto-Freeze Installation Scripts

## 🇮🇩 Bahasa Indonesia

### Cara Penggunaan

Script ini akan otomatis mengupdate `requirements.txt` setiap kali Anda menginstall package baru.

#### PowerShell (Recommended)
```powershell
# Install single package
.\scripts\install.ps1 requests

# Install multiple packages
.\scripts\install.ps1 requests pandas numpy
```

#### Command Prompt (CMD)
```cmd
# Install single package
scripts\install.bat requests

# Install multiple packages
scripts\install.bat requests pandas numpy
```

### Keuntungan
✅ Otomatis update `requirements.txt` setelah install  
✅ Tidak perlu manual `pip freeze`  
✅ Mencegah lupa menambahkan dependency  
✅ Konsisten untuk semua developer  

### Tips
- Gunakan script ini untuk semua instalasi package
- Jangan gunakan `pip install` langsung
- `requirements.txt` akan selalu ter-update otomatis

---

## 🇬🇧 English

### Usage

These scripts automatically update `requirements.txt` every time you install a new package.

#### PowerShell (Recommended)
```powershell
# Install single package
.\scripts\install.ps1 requests

# Install multiple packages
.\scripts\install.ps1 requests pandas numpy
```

#### Command Prompt (CMD)
```cmd
# Install single package
scripts\install.bat requests

# Install multiple packages
scripts\install.bat requests pandas numpy
```

### Benefits
✅ Automatically updates `requirements.txt` after installation  
✅ No need for manual `pip freeze`  
✅ Prevents forgetting to add dependencies  
✅ Consistent across all developers  

### Tips
- Use these scripts for all package installations
- Don't use `pip install` directly
- `requirements.txt` will always be automatically updated

---

## Alternative: Git Hook (Advanced)

Untuk setup yang lebih advanced, Anda bisa menggunakan pre-commit hook yang akan otomatis freeze setiap kali ada perubahan di environment.

### Setup Git Hook
```bash
# Create pre-commit hook
echo "pip freeze > requirements.txt" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Namun, cara ini kurang reliable karena hanya trigger saat commit, bukan saat install.
