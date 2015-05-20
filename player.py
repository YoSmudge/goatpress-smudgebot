from texttable import Texttable, get_color_string, bcolors
import logging
import random

class Board(object):
  """
  Complete board, with tile score
  """
  
  _state = []
  
  def __init__(self,board,state,size=(5,5)):
    self.size = size
    self.board = board
    self.state = state
    self._state = []
    
    for i,letter in enumerate(board):
      if letter is not " ":
        self._state.append(
          Cell(letter,state[i],len(self._state),self)
        )
  
  def cellAtLocation(self,x,y):
    """
    Return the cell at a specified location
    """
    
    index = y*self.size[0] + x
    return self._state[index]
  
  def cellsByRank(self):
    """
    Return cells sorted by rank
    """
    
    return list(reversed(sorted(
      self._state,
      key=lambda c:c.score()
    )))
  
  def __repr__(self):
    t = Texttable()
    
    for rowId in range(0,self.size[0]):
      rowDetails = []
      for cellId in range(0,self.size[1]):
        cell = self.cellAtLocation(cellId,rowId)
        
        color = {
          "free":   bcolors.WHITE,
          "mine":   bcolors.PURPLE,
          "theirs": bcolors.RED
        }[cell.getState()]
        
        rowDetails.append(
          get_color_string(color, cell)
        )
      
      t.add_row(rowDetails)
    
    return "\n".join([
      t.draw(),
      self.board,
      self.state
    ])


class Cell(object):
  """
  Single cell
  """
  _score = None
  
  def __init__(self,letter,state,position,board):
    if position > 24:
      raise Exception("Tried to create letter with position {0}".format(position))
    self.letter = letter
    self.state = int(state)
    self.position = (
      position/5,
      position%5
    )
    self.realPosition = position
    self.board = board
  
  def getState(self):
    return ['free','mine','theirs'][self.state]
  
  def surroundingCells(self):
    """
    Return list of cells around this cell
    """
    
    cells = []
    positionList = [
      (self.position[0],    self.position[1]-1),
      (self.position[0],    self.position[1]+1),
      (self.position[0]-1,  self.position[1]),
      (self.position[0]+1,  self.position[1])
    ]
    
    for cell in positionList:
      if  cell[0] in range(0,self.board.size[0])\
        and cell[1] in range(0,self.board.size[1]):
          cells.append(self.board.cellAtLocation(*cell))
    
    return cells
  
  def score(self):
    if not self._score:
      self._score = 0.0
      
      # Corners are valuable
      if self.position in [
        (0,0),
        (0,self.board.size[1]-1),
        (self.board.size[0]-1,0),
        (self.board.size[0]-1,self.board.size[1]-1)
      ]:
        self._score += 10
      
      # As are cells they own
      if self.getState() == 'theirs':
        self._score += 7.5
        
        # Unless they're surrounded by other cells
        if all([True for c in self.surroundingCells() if c.getState() == 'theirs']):
          self._score -= 10
      
      # Free cells
      if self.getState() == 'free':
        self._score += 2
    
    return self._score
  
  def __repr__(self):
    return "letter {0}\n[{1}]\n{2}\n({3})".format(
      self.letter,
      self.score(),
      self.getState(),
      ",".join([str(p) for p in self.position])
    )


class Game(object):
  """
  Base game class
  """
  
  boardSize = (5,5)
  boardState = []
  wordsFile = "./words.txt"
  words = []
  playedWords = []
  gameMoves = 0
  
  def __init__(self):
    with open(self.wordsFile) as f:
      self.words = f.readlines()
    
    logging.info("Loaded {0} words".format(len(self.words)))
  
  def updateBoard(self,board,state):
    """
    Calculate a consistent board state and store it locally
    """
    
    self.currentBoard = Board(board,state)
    
    print self.currentBoard
  
  def nextMove(self,minLength=6):
    """
    Figure out the next best move
    
    Assign each word in the list it's best score
    """
    
    playableWords = []
    logging.info("Calculating selection")
    wordSelection = random.sample(self.words, 5000)
    
    logging.info("Finding words")
    for word in wordSelection:
      word = word.strip()
      usedCells = []
      
      if len(word) >= minLength and not word in self.playedWords:
        for letter in word:
          letterFound = False
          for cell in self.currentBoard.cellsByRank():
            if not letter.isupper() and letter.lower() == cell.letter and not cell in usedCells:
              usedCells.append(cell)
              letterFound = True
              break
          
          if not letterFound:
            break
      
        if letterFound:
          playableWords.append([word,sum([c.score() for c in usedCells]),usedCells])
    
    topWord = sorted(playableWords,key=lambda pw: pw[1])[-1]
    self.playedWords.append(topWord[0])
    
    return topWord

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  p = Game()
  p.updateBoard(
    "nclxu tcrie nmcoo tueda rctio",
    "22120 20121 12020 21222 10122"
  )