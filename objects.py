class Rover(object):
  def __init__():
    #Position data
    self.x = 0
    self.y = 0
    self.trek = []

    #Power data
    self.batteryCharge = 0
    self.solarDeployed = True
    self.solarOutput = 0
    
    #Comms
    self.lander = None
    self.landerConnected = True

    #Neutron Spectrometer System
    self.nsystem = None

    #Thermal data
    self.temp = 0

class NSS(object):
  def __init__():
    self.active = True

class Lander(object):
  def __init__():
    #Position data
    self.x = 0
    self.y = 0

    #Comms
    self.earthConnected = True
