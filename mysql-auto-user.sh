#!/bin/bash

clear

# ===== Banner Utama =====
cat << "EOF"
*  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  * *                                                                                          
*                                                                                           *
*  MMP""MM""YMM `7MM                                                                        *
*  P'   MM   `7   MM                                                                        * 
*       MM        MMpMMMb.  .gP"Ya   ,pW"Wq`7Mb,od8 `7M'   `MF'`7MMpMMMb.pMMMb.   ,6"Yb.    *
*       MM        MM    MM ,M'   Yb 6W'   `Wb MM' "'   VA   ,V    MM    MM    MM  8)   MM   * 
*       MM        MM    MM 8M====== 8M     M8 MM        VA ,V     MM    MM    MM   ,pm9MM   *
*       MM        MM    MM YM.    , YA.   ,A9 MM         VVV      MM    MM    MM  8M   MM   *
*     .JMML.    .JMML  JMML`Mbmmd'  `Ybmd9'.JMML.       ,V     .JMML  JMML  JMML.`Moo9^Yo.  *
*                                                      ,V                                   *
*                                                    OOb"                                   *
* Theoryma MYSQL Auto User v1.0                                                             *
* Coded by Febrian Dani Ritonga                                                             *
*  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  * * 
EOF

# ===== Password validation =====
validate_password() {
  [[ ${#1} -ge 8 ]] &&
  [[ "$1" =~ [A-Z] ]] &&
  [[ "$1" =~ [a-z] ]] &&
  [[ "$1" =~ [0-9] ]] &&
  [[ "$1" =~ [^a-zA-Z0-9] ]]
}

echo ""
echo "=== MySQL Auto User & Database Tool ==="
echo ""

# ===== Input dasar =====
read -p "Nama database : " DB_NAME
read -p "Username      : " DB_USER

# ===== Input host (penjelasan singkat) =====
echo "Host = asal koneksi ke MySQL (bukan nama database / server)"
read -p "[Enter=localhost | 0=all | IP/host]: " DB_HOST_INPUT

if [[ -z "$DB_HOST_INPUT" ]]; then
  DB_HOST="localhost"
elif [[ "$DB_HOST_INPUT" == "0" ]]; then
  DB_HOST="%"
else
  DB_HOST="$DB_HOST_INPUT"
fi

# ===== Input password =====
while true; do
  read -s -p "Password      : " DB_PASS
  echo
  read -s -p "Ulangi password: " DB_PASS_CONFIRM
  echo

  [[ "$DB_PASS" != "$DB_PASS_CONFIRM" ]] && echo "Password tidak sama" && continue
  ! validate_password "$DB_PASS" && echo "Password tidak memenuhi policy MySQL" && continue
  break
done

echo ""
read -p "Lanjutkan proses? (y/n): " CONFIRM
[[ "$CONFIRM" != "y" ]] && echo "Dibatalkan" && exit 1

# ===== Eksekusi MySQL =====
if sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`;
CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'${DB_HOST}';
FLUSH PRIVILEGES;
EOF
then
  echo ""
  echo "============================"
  echo "| MYSQL Auto User Tool     |"
  echo "| By Theoryma Team         |"
  echo "============================"
  echo "================ SUCCESS ======================"
  echo "Your MySQL user and database have been created:"
  echo "Database : $DB_NAME"
  echo "Username : $DB_USER"
  echo "Host     : $DB_HOST"
  echo ""
else
  echo ""
  echo "FAILED TO CREATE USER OR DATABASE"
fi
