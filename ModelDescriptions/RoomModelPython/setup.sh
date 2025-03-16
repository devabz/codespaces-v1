# INSTALL REQUIREMENTS
pip install --user -r requirements.txt

# INSTALL GNUPLOT
apt update 
apt install gnuplot -y

# REMOVE EXCESS PYTHON INTERPRETERS 
rm -rf $(find /usr/bin -type f -name python*)

# INSTALL NECESSARY VSCODE EXTENSIONS
#code --install-extension ms-python.python
#code --install-extension ms-toolsai.jupyter