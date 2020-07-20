import math
from objects import *
def initiateMockMission():
  #create a lander, rover, NSS
  moonRanger = Rover()
  nss = NSS()
  x1 = Lander()
  testMap = Map()
  testMap.sunAngle = 135
  moonRanger.nSystem = nss
  moonRanger.lander = x1
  moonRanger.map = testMap
  #just combines the path driven view with the obstacle view
  moonRanger.map.addObstaclesToRecord() 

  #operator command testing
  moonRanger.push_waypoint(10,20,2,"far east")
  moonRanger.push_waypoint(18,2,2,"southern region")
  moonRanger.push_waypoint(7,3,2,"back toward comm")
  moonRanger.push_waypoint(5,0,4,"in comm")
  moonRanger.drive_trek()
  moonRanger.map.printMap(moonRanger.map.driveRecord)
  moonRanger.get_telemetry_log()
  #moonRanger.get_nss_data()
  print(moonRanger.checkSolarEff())
  moonRanger.get_solar_status()
  moonRanger.get_battery_status()
  moonRanger.get_comm_status()



initiateMockMission()
