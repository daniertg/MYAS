# Theoryma MySQL Auto User

Web-based & CLI MySQL User & Database Management Tool untuk VPS.

**By Febrian Dani Ritonga - Theoryma Team**

---

## 📋 Features

### Web Interface (NEW!)
- ✅ Create MySQL User & Database via Web
- ✅ List & Manage Users
- ✅ List & Manage Databases  
- ✅ Grant/Revoke Privileges
- ✅ Change User Password
- ✅ Delete Users & Databases
- ✅ Password Policy Validation
- ✅ Responsive Web Interface

### CLI Tool
- Input interaktif
- Validasi password sesuai policy MySQL
- User hanya memiliki akses ke database terkait
- Mendukung localhost, semua host, atau host spesifik

---

## Persyaratan

- Linux VPS
- MySQL / MariaDB
- Akses sudo
- Python 3 (untuk Web Interface)

---

## 🚀 Quick Install Web Interface

```bash
# Clone atau upload files ke VPS
cd /path/to/mysql-auto-user

# Jalankan installer
sudo chmod +x install.sh
sudo ./install.sh
```

Akses melalui browser: `http://YOUR_SERVER_IP:5000`

---

## Instalasi CLI Only

Clone repository ke VPS:

```bash
git clone https://github.com/USERNAME/mysql-auto-user.git
cd mysql-auto-user
chmod +x mysql-auto-user.sh
