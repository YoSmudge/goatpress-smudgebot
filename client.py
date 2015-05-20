import socket
import player
import logging

class GoatpressClient(object):
  def __init__(self,server):
    self.server = server
  
  def connect(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect(self.server)

  def send(self, message):
    sent = self.sock.send(message + "\n")
    
    logging.info(">"+message)
    
    if sent == 0:
      raise RuntimeError("socket connection broken")

  def readLine(self):
    message = b''
    end_of_message = b'\n'
    while len(message) == 0 or message[-1] != end_of_message:
      char = self.sock.recv(2)
      message = message + char
    
    return str(message)
  
  def waitForCommand(self):
    line = c.readLine()
    
    try:
      infoMsg = line.split(';')[0].lstrip()
      command = line.split(';')[1].lstrip().rstrip()
    except IndexError:
      print "ERROR LINE", line
      exit()
    
    logging.info("INFO "+ infoMsg)
    logging.info("COMMAND "+ command)
    
    if command == 'name ?':
      self.send("SmudgeBot")
    elif command == 'ping ?':
      self.send("pong")
    elif infoMsg.startswith('new game vs'):
      logging.info("Creating game against {0}".format(line.split(";")[0].split(" ")[-1]))
      self.currentGame = player.Game()
    elif command.startswith('move'):
      self.currentGame.updateBoard(
        " ".join(command.split(' ')[1:6]),
        " ".join(command.split(' ')[6:11])
      )
      
      nextMove = self.currentGame.nextMove()
      
      logging.info("Playing {0}".format(nextMove[0]))
      
      positions = []
      for l in nextMove[2]:
        positions.append([l.letter,l.position,l.realPosition])
      
      sendString = "move:{0} ({1})".format(
        ",".join(
          ["".join(
            [str(p) for p in pos[1]]
          ) for pos in positions
          ]
        ),
        nextMove[0]
      )
      
      self.send(sendString)

if __name__ == '__main__':
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)d %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S"
  )
  
  c = GoatpressClient(
    ('52.16.6.95',4123)
  )
  c.connect()
  
  while True:
    c.waitForCommand()