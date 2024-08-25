python -m venv mqttbuzz
source mqttbuzz/bin/activate
cd mqttbuzz
pip install --upgrade pip
pip install paho.mqtt
pip install py2app
pip install rumps 
pip install setuptools==70.3.0
cp -r ~/Documents/GitHub/osx-code/mqttbuzz/* .
python setup.py py2app
