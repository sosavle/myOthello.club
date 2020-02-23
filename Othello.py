###############################################
## Vignesh Selvaraj                          ##
## Luis Sosa                                 ##
## Nicholas Wagner                           ##
###############################################
## Artificial Inteligence Project 1: Othello ##
###############################################


'''
NOTES:
    * Any given space can be black 'B', white, 'W', empty ' ', periphery '@' or wall 'X'
    * In order to make move choosing efficient, the board keeps track of all peripheries -- areas around other chips
    * The board has a dictionary linking all peripheries coordinates with the direction of nearby chips
    * Thus, to search for possible moves, one should check the periphery list and evaluate the linked directions
'''


import pygame, sys, copy
from abc import ABC, abstractmethod
from pygame.locals import *

# Initialize pygame library
pygame.init()


# Global variables for screen drawing
DISPLAY = pygame.display.set_mode((400, 500), 0, 32)
FONT = pygame.font.Font(None, 30)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (123, 196, 255)


class Board:
    '''Represents the game board in member variable "configuration" and possesses
    methods determineCaptures() and modifyLayout* to seek viable moves and
    excecute them, respectively'''
    # Codenames for direction values in the form of [rowShift, columnShift]
    N = [-1, 0]
    NE = [-1, 1]
    E = [0, 1]
    SE = [1, 1]
    S = [1, 0]
    SW = [1, -1]
    W = [0, -1]
    NW = [-1, -1]
    directions = [N, NE, E, SE, S, SW, W, NW]

    def __init__(self):
        '''Creates an Othello board in the initial state'''
        self.configuration = [['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
                              ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X'],
                              ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X'],
                              ['X', ' ', ' ', '@', '@', '@', '@', ' ', ' ', 'X'],
                              ['X', ' ', ' ', '@', 'B', 'W', '@', ' ', ' ', 'X'],
                              ['X', ' ', ' ', '@', 'W', 'B', '@', ' ', ' ', 'X'],
                              ['X', ' ', ' ', '@', '@', '@', '@', ' ', ' ', 'X'],
                              ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X'],
                              ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X'],
                              ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']]
        self.score = [2, 2]
        self.mustPass = False
        self.endState = False


        self.peripheries = {(5, 3): [Board.NE, Board.E],
                            (6, 3): [Board.NE],
                            (6, 4): [Board.NE, Board.N],
                            (6, 5): [Board.N, Board.NW],
                            (6, 6): [Board.NW],
                            (5, 6): [Board.W, Board.NW],
                            (4, 6): [Board.SW, Board.W],
                            (3, 6): [Board.SW],
                            (3, 5): [Board.SW, Board.S],
                            (3, 4): [Board.S, Board.SE],
                            (3, 3): [Board.SE],
                            (4, 3): [Board.E, Board.SE]}

    def print(self):
        print(" ---------- ")
        num = 0
        print("  0 1 2 3 4 5 6 7 8 9")
        for row in self.configuration:
            print(num, end=' ')
            num += 1
            for element in row:
                if element == 'B':
                    print('□', end=' ')
                elif element == 'W':
                    print('■', end=' ')
                else:
                    print(element, end=' ')
            print("\n", end='')
        print(" ---------- ")

    @staticmethod
    def getOppositeColor(color):
        '''Returns black if color is white, white if color is black, and N/A otherwise'''
        if color == 'B':
            return 'W'
        elif color == 'W':
            return 'B'
        else:
            return "N/A"

    @staticmethod
    def getOppositeDirection(direction):
        '''Returns direction opposite to input'''
        return [-1*direction[0], -1*direction[1]]

    def searchLine(self, color, row, column, direction):
        '''Searches a list of directions and attempts to find
        a piece of the same color (making a legal move).
        Returns the position of all capturable pieces
        resulting from playing on position [row,column]'''

        oppositeColor = Board.getOppositeColor(color)
        capturablePieces = []

        # Look ahead to next location
        row += direction[0]
        column += direction[1]

        # If immediately adjacent chip is not of opposite color, the move is illegal
        if self.configuration[row][column] != oppositeColor:
            return []

        # Update looping variables
        capturablePieces = [[row, column]]
        row += direction[0]
        column += direction[1]

        # Another chip along the line must be of the same color
        while True:
            currentColor = self.configuration[row][column]

            # If an opposite colored chip is found, it may be capturable if the move is legal
            if currentColor == oppositeColor:
                capturablePieces += [[row, column]]

            # If a same colored chip was found, the result found is valid
            elif currentColor == color:
                return capturablePieces

            # If an empty tile  or wall is found, move is illegal after all
            else:
                return []

            # Move onto the next tile
            row += direction[0]
            column += direction[1]

        # If loop conditions were not met, the move is illegal after all
        return []

    def determineCaptures(self, color, row, column):
        '''Returns a list with the position of all pieces that would be captured by a given move'''

        # Only peripheral positions can possibly have any captures
        if self.configuration[row][column] != '@':
            return []

        capturablePieces = []

        # Determine directions to search
        pos = (row, column)
        searchDirections = self.peripheries[pos]

        # Search those directions
        for d in searchDirections:
            capturablePieces += self.searchLine(color, row, column, d)
        return capturablePieces


    def modifyLayout(self, color, row, column, captures=None, redraw=True):
        '''Modifies the board by making positions listed in captures of a given color.
        If no capture list is provided, it is calculated on the spot.
        If the move is illegal, Illegal is returned'''

        # If not provided, determine which chips will be captured with this move
        if captures == None:
            captures = self.determineCaptures(color, row, column)
        # If no chips will be captured, return error
        if captures == []:
            return "Illegal"

        # Branch function behavior depending on move color
        if color == 'B':
            myScore = 0
            opponentScore = 1
            penColor = BLACK;

        else:
            myScore = 1
            opponentScore = 0
            penColor = WHITE;

        # Capture and redraw chips
        self.configuration[row][column] = color

        if redraw:
            pygame.draw.circle(DISPLAY, penColor, [column * 50 - 25, row * 50 - 25], 20)

        for position in captures:
            self.configuration[position[0]][position[1]] = color
            if redraw:
                pygame.draw.circle(DISPLAY, penColor, [position[1] * 50 - 25, position[0] * 50 - 25], 20)

        # Update score
        numCaptures = len(captures)
        self.score[myScore] += numCaptures + 1
        self.score[opponentScore] -= numCaptures

        # Update periphery values
        self.updatePeripheries(row, column)

        # Determine if new state is a pass/end state
        self.determinePassEnd(color)


    def updatePeripheries(self, row, column):
        '''Turns empty (' ') squares around position row,column into peripheries ('@')
        Updates nearby preexisting peripheries with new borderDirection entry'''

        # Remove move square from peripheries
        pos = (row, column)
        del self.peripheries[pos]

        for d in self.directions:
            pos = (row + d[0], column + d[1])

            # If empty square, add to periphery list
            if self.configuration[pos[0]][pos[1]] == ' ':
                self.configuration[pos[0]][pos[1]] = '@'
                self.peripheries[pos] = [Board.getOppositeDirection(d)]

            # If already a periphery, add a new direction to check
            elif self.configuration[pos[0]][pos[1]] == '@':
                self.peripheries[pos] += [Board.getOppositeDirection(d)]

    def determinePassEnd(self, color):
        '''Determines a player must pass or if current configuration is a final state
        Returns True if either we must pass or if it is an end state'''

        # Search all peripheries
        for peri in self.peripheries:

            # Translate location string to ints
            row, column = peri

            # If at least single piece is capturable, then no need to pass
            if self.determineCaptures(color, row, column) != []:
                self.mustPass = False
                return False

        # If no move was legal, we must run the function a second time
        # for the opposite color to determine whether state is pass or end
        if not self.mustPass:
            self.mustPass = True
            self.endState = self.determinePassEnd(Board.getOppositeColor(color))

        # If we get to this point, then our current state is an end state
        return True







class StateNode:
    def __init__(self, id, board):
        self.children = {}
        self.value = None
        self.id = id
        self.board = board

    def populateChildren(self, color):

        # Verify which captures are legal moves
        for peri in self.board.peripheries:
            captures = self.board.determineCaptures(color, peri[0], peri[1])
            if captures == []:
                continue
            else:
                nextBoard = copy.deepcopy(self.board)
                nextBoard.modifyLayout(color, peri[0], peri[1], captures, redraw=False)
                self.children[peri] = StateNode(peri, nextBoard)

                #print(color, "move @", peri, "captures", captures)
                #self.board.print()
                #print("↓")
                #nextBoard.print()

    def heuristicEvaluation1(self):
        '''Evaluate state non-recursively with heuristic from the perspective of Black'''
        return self.board.score[0]

    def evaluateState(self, color, maxDepth, currentDepth=1):
        '''Evaluates state desirability recursively from the perspective of Black'''
        #print(currentDepth)

        # Exit recursion at a certain depth
        if currentDepth > maxDepth:
            self.value = self.heuristicEvaluation1()
            return self.value

        # If end state, no need to keep searching
        elif self.board.endState:

            if self.board.score[0] > board.score[1]:
                self.value = float("inf")
                return float("inf")

            elif self.board.score[0] < board.score[1]:
                self.value = float("inf")
                return float("-inf")

            else:
                self.value = 0
                return 0

        elif self.board.mustPass:
            self.value = self.evaluateState(Board.getOppositeColor(color), maxDepth, currentDepth + 1)
            print("passcase")
            return self.value

        # Explore each child, keeping max/min values encountered
        minimum = float('inf')
        maximum = float('-inf')

        #print(color)
        #self.board.print()
        self.populateChildren(Board.getOppositeColor(color))

        for child in self.children.values():
            childVal = child.evaluateState(Board.getOppositeColor(color), maxDepth, currentDepth + 1)
            if color == "W" and childVal < minimum:
                minimum = childVal

            elif color =="B" and childVal > maximum:
                maximum = childVal

        # Value of node is max/min of child values
        if color == "W":
            self.value = minimum
        else:
            self.value = maximum

        return self.value


class Player(ABC):
    @abstractmethod
    def makeMove(self):
        pass

class HumanPlayer(Player):
    @staticmethod
    def makeMove():
        pass

class AIPlayer(Player):
    def __init__(self, board, lookAhead=2):
        self.stateTree = StateNode((0, 0), Board())
        self.board = board
        self.lookAhead = lookAhead
        self.AIColor = "W"

        self.stateTree.populateChildren(Board.getOppositeColor(self.AIColor))

    def makeMove(self):
        # Selecting the minimum element in the child eval list
        minimum = float('inf')
        move = None

        # Before starting a recursive search, check if path has already been explored
        print("children", self.stateTree.children)
        if self.stateTree.children != {}:
            minChild = min(self.stateTree.children.values(), key=lambda child: child.value)
            move = minChild.id
            print("Skipped Eval")

        else:
            # Populate children list with potential moves
            if self.stateTree.children == {}:
                self.stateTree.populateChildren(self.AIColor)
            # Evaluate the value of each legal move and keep track of the minimum
            for child in self.stateTree.children.values():
                evaluation = child.evaluateState(self.AIColor, self.lookAhead)
                #print("min",minimum)
                #print("eval",evaluation)
                if evaluation < minimum:
                     minimum = evaluation
                     move = child.id

        # Make the best move (worst for black)
        self.board.modifyLayout(self.AIColor, move[0], move[1]) #ADD: If child empty, PASS
        self.moveToNextLevel(self.AIColor, move)
        #print("AI made a move at", move[0], ",", move[1], "Beep")

    def moveToNextLevel(self, color, moveID):
        # Populate children list with potential moves
        if self.stateTree.children == {}:
            self.stateTree.populateChildren(color)
        newRoot = self.stateTree.children[moveID]
        print("root")
        newRoot.board.print()
        self.stateTree = newRoot










def othelloInit():
    '''Initializes graphic and sound components of the game'''
    # Initialize display window
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Othello')
    DISPLAY.fill(GREEN)
    for n in range(0, 401, 50):
        pygame.draw.rect(DISPLAY, LIGHT_BLUE, [0, 400, 500, 100])
        pygame.draw.line(DISPLAY, BLACK, [n, 0], [n, 400], 3)
        pygame.draw.line(DISPLAY, BLACK, [0, n], [400, n], 3)
    pygame.draw.circle(DISPLAY, BLACK, [4 * 50 - 25, 4 * 50 - 25], 20)
    pygame.draw.circle(DISPLAY, BLACK, [5 * 50 - 25, 5 * 50 - 25], 20)
    pygame.draw.circle(DISPLAY, WHITE, [5 * 50 - 25, 4 * 50 - 25], 20)
    pygame.draw.circle(DISPLAY, WHITE, [4 * 50 - 25, 5 * 50 - 25], 20)

    # Initialize menu icons
    DISPLAY.blit(FONT.render('Turn: 1', True, BLACK, LIGHT_BLUE), (25, 425))
    pygame.draw.circle(DISPLAY, BLACK, [58, 470], 20)
    DISPLAY.blit(FONT.render('Black: 2', True, BLACK, LIGHT_BLUE), (140, 425))
    DISPLAY.blit(FONT.render('White: 2', True, BLACK, LIGHT_BLUE), (268, 425))
    pygame.draw.rect(DISPLAY, BLACK, [337, 472, 60, 20])
    DISPLAY.blit(FONT.render('Reset', True, BLACK, GREEN), (340, 475))



    # Initialize Sound
    pygame.mixer.music.load('background.mp3')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    # Initialize board and AI
    board = Board()
    return board, 'B', 1, AIPlayer(board) # AIPlayer(board)






if __name__ == "__main__":
    board, color, turnNo, ai = othelloInit()
    moveSFX = pygame.mixer.Sound('movesfx.wav')
    turnPlayer = 'B'

    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and turnNo % 2:
                x = event.pos[0]
                y = event.pos[1]
                pygame.event.pump
                row = y // 50 + 1
                column = x // 50 + 1
                print("Clicked at", row, column)
                if row <= 8 and column <= 8:
                    captures = board.determineCaptures(color, row, column)
                    if captures != []:
                        moveSFX.play()
                        board.modifyLayout(color, row, column, captures)
                        ai.moveToNextLevel(turnPlayer,(row,column))
                        color = board.getOppositeColor(color)
                        board.print()
                        turnNo += 1
                        DISPLAY.blit(FONT.render('Turn: %d ' % turnNo, True, BLACK, LIGHT_BLUE), (25, 425))
                        DISPLAY.blit(FONT.render('Black: %d  ' % board.score[0], True, BLACK, LIGHT_BLUE), (140, 425))
                        DISPLAY.blit(FONT.render('White: %d  ' % board.score[1], True, BLACK, LIGHT_BLUE), (268, 425))
                        if (turnNo % 2):
                            pygame.draw.circle(DISPLAY, BLACK, (58, 470), 20)
                        else:
                            pygame.draw.circle(DISPLAY, WHITE, (58, 470), 20)
                elif 340 <= x <= 395 and 475 <= y <= 495:
                    print("Clicked reset!")
                    pygame.draw.rect(DISPLAY, WHITE, (337, 472, 60, 20))
                    DISPLAY.blit(FONT.render('Reset', True, BLACK, YELLOW),(340,475))
                    pygame.display.update()
                    board, color, turnNo, ai = othelloInit()


            elif event.type == KEYDOWN and not turnNo % 2:
                pygame.event.pump
                if not (turnNo % 2):
                    ai.makeMove()
                    moveSFX.play()
                    color = board.getOppositeColor(color)
                    board.print()
                    turnNo += 1
                    DISPLAY.blit(FONT.render('Turn: %d ' % turnNo, True, BLACK, LIGHT_BLUE), (25, 425))
                    DISPLAY.blit(FONT.render('Black: %d  ' % board.score[0], True, BLACK, LIGHT_BLUE), (140, 425))
                    DISPLAY.blit(FONT.render('White: %d  ' % board.score[1], True, BLACK, LIGHT_BLUE), (268, 425))
                    if (turnNo % 2):
                        pygame.draw.circle(DISPLAY, BLACK, (58, 470), 20)
                    else:
                        pygame.draw.circle(DISPLAY, WHITE, (58, 470), 20)



            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

"""
    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:

                if not (turnNo % 2):
                    ai.makeMove()
                    moveSFX.play()
                    color = board.getOppositeColor(color)
                    board.print()
                    turnNo += 1
                    DISPLAY.blit(FONT.render('Turn: %d ' % turnNo, True, BLACK, LIGHT_BLUE), (25, 425))
                    DISPLAY.blit(FONT.render('Black: %d  ' % board.score[0], True, BLACK, LIGHT_BLUE), (140, 425))
                    DISPLAY.blit(FONT.render('White: %d  ' % board.score[1], True, BLACK, LIGHT_BLUE), (268, 425))
                    if (turnNo % 2):
                        pygame.draw.circle(DISPLAY, BLACK, (58, 470), 20)
                    else:
                        pygame.draw.circle(DISPLAY, WHITE, (58, 470), 20)





                x = event.pos[0]
                y = event.pos[1]
                row = y // 50 + 1
                column = x // 50 + 1
                print("Clicked at", row, column)
                if row <= 8 and column <= 8:
                    captures = board.determineCaptures(color, row, column)
                    if captures != []:
                        moveSFX.play()
                        board.modifyLayout(color, row, column, captures)
                        ai.moveToNextLevel((row,column))
                        color = board.getOppositeColor(color)
                        board.print()
                        turnNo += 1
                        DISPLAY.blit(FONT.render('Turn: %d ' % turnNo, True, BLACK, LIGHT_BLUE), (25, 425))
                        DISPLAY.blit(FONT.render('Black: %d  ' % board.score[0], True, BLACK, LIGHT_BLUE), (140, 425))
                        DISPLAY.blit(FONT.render('White: %d  ' % board.score[1], True, BLACK, LIGHT_BLUE), (268, 425))
                        if (turnNo % 2):
                            pygame.draw.circle(DISPLAY, BLACK, (58, 470), 20)
                        else:
                            pygame.draw.circle(DISPLAY, WHITE, (58, 470), 20)
                elif 340 <= x <= 395 and 475 <= y <= 495:
                    print("Clicked reset!")
                    pygame.draw.rect(DISPLAY, WHITE, (337, 472, 60, 20))
                    DISPLAY.blit(FONT.render('Reset', True, BLACK, YELLOW),(340,475))
                    pygame.display.update()
                    board, color, turnNo, ai = othelloInit()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
"""



