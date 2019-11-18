import configparser

config = configparser.ConfigParser()
config.read('/home/pi/ubuntuPyNightLock/config.ini')

manager = config['Manager']
nightscout = config['Nightscout']
plot = config['Plot']
display = config['Display']
