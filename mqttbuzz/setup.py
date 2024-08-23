from setuptools import setup

APP = ['src/mqttbuzz.py']
DATA_FILES = ['config.json','help.txt']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'src/MQTTBuzz.icns'
    'packages': ['rumps', 'paho.mqtt.client'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
