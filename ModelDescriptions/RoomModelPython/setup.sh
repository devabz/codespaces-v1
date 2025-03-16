# INSTALL REQUIREMENTS
pip install --user -r requirements.txt

# INSTALL GNUPLOT
apt update 
apt install gnuplot -y

# REMOVE EXCESS PYTHON INTERPRETERS 
rm -rf $(find /usr/bin -type f -name python*)
