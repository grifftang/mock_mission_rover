from objects import *

def runMockMission():
  #create a lander, rover, NSS
  moonRanger = Rover()
  nss = NSS()
  x1 = Lander()
  moonRanger.nsystem = nss
  moonRanger.lander = x1

  #loop
    #get user input command

    #check valid command

    #execute command

    #send back the resulting data









if __name__ == 'main':
  print("yo")
  runMockMission()