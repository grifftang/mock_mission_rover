import math, random
from tkinter import *

class Rover(object):
  def __init__(self):
    self.time = 0
    #configurable data
    self.maxIncline = 0.3
    self.startingPower = 200 
    self.maxChargeRate = 10
    self.drivePowerCost = 10
    self.maxCharge= 200
    self.minPowerBeforeCharge = 20

    #Position data
    self.map = None
    self.x = 0
    self.y = 0
    self.trek = []
    self.telemetryLog = []
    self.lastDriveAngle = 0

    #Power data
    self.batteryCharge = self.startingPower
    self.solarDeployed = True
    self.solarOutput = 0
    
    #Comms
    self.lander = None
    self.landerConnectionStrength = 100

    #Neutron Spectrometer System
    self.nSystem = None

    #Thermal data
    self.temp = 0

  # Returns the communication strength status
  def get_comm_status(self):
    if self.lander.earthConnected:
      return "Communication Status:\n" + "Earth <--✓--> Lander (Obviously)\n" + "Lander <--" + str(self.landerConnectionStrength) + "%--> Rover"
    else:
      return "Lander uplink connection failed"

  # Returns NSS data
  def get_nss_data(self):
    if self.landerConnectionStrength > 0:
      return self.nSystem.dataLog
    else:
      return "Communication to rover failed..."

  # Returns telemetry log of rover
  def get_telemetry_log(self):
    if self.landerConnectionStrength > 0:
      result = "Time: Position: Battery: Solar: Comms: NSS:\n"
      for t in self.telemetryLog:
        result += " " + str(round(t.time, 1)) + "hr" + "   " + str(t.pos) + "     " + str(int(t.battery/2))+"%" + "     " + str(int(t.solar))+"%" + "    " + str(t.connectionStrength) + "    " + str(t.nss) + "\n"
        print(result)
      return result
    else:
      return "Communication to rover failed...\n"

  # Returns the status of the solar panel (deployed & strength)
  def get_solar_status(self):
    if self.landerConnectionStrength > 0:
      if self.solarDeployed:
        return "Panel deployed, collecting at " + str(self.checkSolarEff()) + "%\n"
      else:
        return "Solar panel not deployed\n"
    else:
        return "Communication to rover failed...\n"

  # Returns the battery status of the rover
  def get_battery_status(self):
    if self.landerConnectionStrength > 0:
      return "System powered at "+str(round(self.batteryCharge/self.maxCharge*100,2))+"%\n"
    else:
      return "Communication to rover failed...\n"

  # Returns the rover's status as a string
  def get_systems_status(self):
    response = self.get_solar_status() + self.get_battery_status()
    response += "NSS status is nominal.\n"
    response += "Thermal status is nominal.\n"
    response += "Software status is nominal.\n"
    response += "Mechanical status is nominal.\n"
    return response

  # Adds a waypoint to the rover's trek list
  def push_waypoint(self, x,y,r,name):
    if self.landerConnectionStrength > 0:
      waypoint = Waypoint(x,y,r,name)
      self.trek.append(waypoint)
      return "Added waypoint '" + name + "' at x=" + str(x) + ", y=" + str(y)
    else:
      return "Communication to rover failed..."

  # Clears all waypoints from the rover's trek list
  def clear_trek(self):
    if self.landerConnectionStrength > 0:
      self.trek = []
      return "Trek cleared"
    else:
      return "Communication to rover failed..."

  def delete_trek_data(self):
    if self.landerConnectionStrength > 0:
      return "Data deleted"
    else:
      return "Communication to rover failed..."

  # Stop the rover and charge the battery until it's full
  def charge_to_full(self):
    if self.landerConnectionStrength > 0:
      while self.batteryCharge < 190:
        self.charge()
        self.tickTime()
      return "Charged!"
    else:
      return "Communication to rover failed..."
  
  #Operable by rover so no fail catch
  def charge_to_percent(self,percent):
    while self.batteryCharge/self.maxCharge*100 < percent:
      self.charge()
      self.tickTime()
    return "Charged!"

  def drive_trek(self):
    if self.landerConnectionStrength > 0:
      print("Initiating trek of "+str(len(self.trek))+" waypoints")
      for waypoint in self.trek:
        self.drive(waypoint)
      return "Trek complete"

      #self.clear_trek()

    else:
      return "Communication to rover failed..."

  def drive(self, waypoint):
    #while we are not near enough to our target
    #nss collect data
    self.nSystem.log(self.time,self.x,self.y,self.map)
    #collect telemetry data
    self.telemetryLog.append(Telemetry(self.time,self.x,self.y,self.batteryCharge,self.checkSolarEff(),self.landerConnectionStrength,self.nSystem.active))
    while(self.distFrom(waypoint) > waypoint.radius):
      #for each possible next pixel
      bestDist = self.map.width*10 #unreachably far min
      bestX = self.x
      bestY = self.y
      #check faults:
      if self.faultCheckPass():
        for row in range(self.y - 1, self.y + 2):
          for col in range(self.x - 1, self.x + 2):
            #check in bounds of array
            if 0 <= col < self.map.width and 0 <= row < self.map.height:
              #check slope & obstacles
              if self.map.obstacleMap[col][row] != "^": #and self.map.slopeMap[col][row] > self.maxIncline:
                #check bestDist
                if self.dist(col,row,waypoint.x,waypoint.y) < bestDist:
                  bestDist = self.dist(col,row,waypoint.x,waypoint.y)
                  bestX = col
                  bestY = row
        if (self.x,self.y) == (bestX,bestY):
          return "Rover crashed in obstacle"
        #Move and take power cost
        self.lastDriveAngle = self.angleToWaypoint(Waypoint(bestX,bestY,0,"Best"))
        self.x = bestX
        self.y= bestY
        self.batteryCharge -= self.drivePowerCost
      else:
        self.charge_to_percent(50)

      #charge check
      self.charge()
      #comms check
      if self.distFrom(self.lander) <= self.lander.commRange:
        self.landerConnectionStrength = 100
      else:
        self.landerConnectionStrength = 0
      #record progress and tick
      self.tickTime()
      #nss collect data
      self.nSystem.log(self.time,self.x,self.y,self.map)
      #collect telemetry data
      self.telemetryLog.append(Telemetry(self.time,self.x,self.y,self.batteryCharge,self.checkSolarEff(),self.landerConnectionStrength,self.nSystem.active))
      self.map.driveRecord[bestX][bestY] = "*"

  def tickTime(self):
    self.time += 0.1

  def charge(self):
    self.batteryCharge += self.maxChargeRate * self.checkSolarEff()
    print(self.batteryCharge)

  def faultCheckPass(self):
    #battery has enough power
    return self.batteryCharge >= self.minPowerBeforeCharge
    #add more later

  def distFrom(self,waypoint):
    return ( (waypoint.x -self.x)**2 + (waypoint.y - self.y)**2 )**0.5

  def dist(self,x1,y1,x2,y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

  def checkSolarEff(self):
    panelAngle = 360 % (self.lastDriveAngle + 90)
    return math.sin(math.radians(abs(panelAngle - 180)))

  def angleToWaypoint(self,waypoint):
    rads = math.atan2(waypoint.y-self.y, waypoint.x-self.x)
    return math.degrees(rads)
class NSS(object):
  def __init__(self):
    self.active = True
    self.dataLog = []
  def log(self,time,x,y,map):
    self.dataLog.append([time,map.iceMap[x][y]])

class Lander(object):
  def __init__(self):
    #Position data
    self.x = 0
    self.y = 0
    #Comms
    self.earthConnected = True
    self.commRange = 100

class Map(object):
  def __init__(self):
    self.obstacleOdds = 4 #1/4
    self.sunAngle = 0
    self.width = 20
    self.height = 20
    self.driveRecord = self.newMap()
    self.obstacleMap = self.randomObstacleMap()
    self.iceMap = self.randomIceMap()

  def addObstaclesToRecord(self):
    for row in range(self.height):
      for col in range(self.width):
        if self.obstacleMap[row][col] == "^":
          self.driveRecord[row][col] = "^"

  def newMap(self):
    blank = []
    for row in range(self.height):
      line = []
      for col in range(self.width):
        line.append("-")
      blank.append(line)
    return blank
  
  def randomIceMap(self):
    resultMap = self.newMap()
    for row in range(self.height):
      for col in range(self.width):
        #25% odds of having ice at all
        if random.randint(1,4) == 4:
          resultMap[row][col] = round(random.random(),2)
    return resultMap

  def randomObstacleMap(self):
    resultMap = self.newMap()
    for row in range(self.height):
      for col in range(self.width):
        #1/3rd odds of being an obstacle
        if random.randint(1,self.obstacleOdds) == self.obstacleOdds:
          resultMap[row][col] = "^"
    return resultMap
  
  def printMap(self,map):
    print("+  ",end="")
    for i in range(len(map[0])):
      if i < 10:
        print(" "+str(i),end=" ")
      else:
        print(i,end=" ")
    print()
    for row in range(len(map)):
      if row == 0:
        print(row,end="  ")
      elif 0 < row < 10:
        print(row,end="  ")
      else:
        print(row,end=" ")

      for col in range(len(map[0])):
        print(" "+ str(map[row][col]), end = " ")
      print()

  def printTkMap(self):
    master = Tk()

    windowHeight = 500
    c = Canvas(master, width=1200, height=windowHeight)
    c.pack()

    obsColor = "dark grey"
    noObsColor = "black"
    iceColor = "blue"
    someIceColor = "light blue"
    noIceColor = "white"
    size = windowHeight / self.height

    for y in range(self.height):
      for x in range(self.width):
        outlineColor = noObsColor
        if self.iceMap[x][y] == '-':
          fillColor = noIceColor
        elif self.iceMap[x][y] <= .49:
          fillColor = iceColor
        elif self.iceMap[x][y] > .5:
          fillColor = someIceColor
        if self.obstacleMap[x][y] == "^":
          fillColor = obsColor
        c.create_rectangle(x * size, y * size, (x + 1) * size, (y + 1) * size, fill=fillColor, outline= outlineColor)
    
    mainloop()

class Waypoint(object):
  def __init__(self,x,y,r,name):
    self.x = x
    self.y = y
    self.radius = r
    self.name = name

  def __str__(self):
    return "(" + str(self.x) + ", " + str(self.y) + ")" + " Radius: " + str(self.radius) + " Name: " + self.name

  def __repr__(self):
    return self.__str__()

class Telemetry(object):
  def __init__(self,time,x,y,battery,solar,connectionStrength,nss):
    self.time = time
    self.pos = (x,y)
    self.battery = battery
    self.solar = solar
    self.connectionStrength = connectionStrength

    self.nss = 'On'
    if not nss: 
      self.nss = 'Off'
