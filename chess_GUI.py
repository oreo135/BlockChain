import tkinter as tkin
from PIL import ImageTk, Image
import random
import os.path

root = tkin.Tk()
root.title('Chess')
root.geometry("1300x1000")

# define absolute OS path
script_dir = os.path.dirname(os.path.abspath(__file__))

# title
header = tkin.Label(root, text="2D Chess")
header.config(font=("courier", 20))
header.grid(column=0, row=0)

def roundLabel(moveNo):
    roundText = tkin.Label(root, text="MOVE")
    roundNo = tkin.Label(root, text=moveNo)
    roundText.grid(column=0, row=9, sticky="w")
    roundNo = roundNo.grid(column=0, row=9)

def playerLabel(playerGo):
    pass

def labelTop():
    # putting letter labels at top of board
    topLabels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    count = 1
    for letter in topLabels:
        letter = tkin.Label(root, text=letter)
        letter.grid(column=count, row=0, sticky="S")
        count += 1

def labelSide():
    # putting numbers in labels at side of board
    sideLabels = [i for i in range(8, 0, -1)]
    count = 1
    for num in sideLabels:
        num = tkin.Label(root, text=num)
        num.grid(column=0, row=count, sticky="E")
        count += 1

def padding():
    lLabel = tkin.Label(root)
    lLabel.grid(column=0, ipadx=50)

def MakeBoardCanvases():
    '''Gets and stores the square images needed to make the board'''
    global blackSquares
    global whiteSquares

    blackSquares = []
    blackSquares += range(0, 32)

    whiteSquares = []
    whiteSquares += range(0, 32)

    for var in blackSquares:
        ind = blackSquares.index(var)
        blackSquares[ind] = tkin.Canvas(root, width=100, height=100, border=0, bg="black", cursor="hand2")

    for var in whiteSquares:
        ind = whiteSquares.index(var)
        whiteSquares[ind] = tkin.Canvas(root, width=100, height=100, border=0, bg="white", cursor="hand2")

    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                # Для черных клеток
                canvas = blackSquares.pop()  # Извлекаем холст из списка черных клеток
            else:
                # Для белых клеток
                canvas = whiteSquares.pop()  # Извлекаем холст из списка белых клеток
            canvas.grid(row=row + 1, column=col + 1)

    return blackSquares, whiteSquares

def boardSpaces(blackSquares, whiteSquares):

    board = []
    for num in range(0, 4):
        board.append(whiteSquares[num])
        board.append(blackSquares[num])
    for num in range(4, 8):
        board.append(blackSquares[num])
        board.append(whiteSquares[num])
    for num in range(8, 12):
        board.append(whiteSquares[num])
        board.append(blackSquares[num])
    for num in range(12, 16):
        board.append(blackSquares[num])
        board.append(whiteSquares[num])
    for num in range(16, 20):
        board.append(whiteSquares[num])
        board.append(blackSquares[num])
    for num in range(20, 24):
        board.append(blackSquares[num])
        board.append(whiteSquares[num])
    for num in range(24, 28):
        board.append(whiteSquares[num])
        board.append(blackSquares[num])
    for num in range(28, 32):
        board.append(blackSquares[num])
        board.append(whiteSquares[num])
    return board

boardObjectSpaces = []
for num in range(0,64):
        boardObjectSpaces.append("")

wSet = []
bSet = []


class Piece(object):
    def __init__(self, color, mySet):

        self.color = color
        self.mySet = mySet.append(self)

    # properties
    alive = True
    squareInd = 0

    global row1
    global row2
    global row3
    global row4
    global row5
    global row6
    global row7
    global row8

    global col1
    global col2
    global col3
    global col4
    global col5
    global col6
    global col7
    global col8

    row1 = range(0, 8)
    row2 = range(8, 16)
    row3 = range(16, 24)
    row4 = range(24, 32)
    row5 = range(32, 40)
    row6 = range(40, 48)
    row7 = range(48, 56)
    row8 = range(56, 64)

    col1 = range(0, 57, +8)
    col2 = range(1, 58, +8)
    col3 = range(2, 59, +8)
    col4 = range(3, 60, +8)
    col5 = range(4, 61, +8)
    col6 = range(5, 62, +8)
    col7 = range(6, 63, +8)
    col8 = range(7, 64, +8)

    def unbindAll(self):
        pass

class Pawn(Piece):
    # properties
    bOpen = Image.open(os.path.join(script_dir, "mats/bPawn.png"))
    bImage = ImageTk.PhotoImage(bOpen)
    wOpen = Image.open(os.path.join(script_dir, "mats/wPawn.png"))
    wImage = ImageTk.PhotoImage(wOpen)

    kind = "pawn"

    def moves(self, squareIndex):
        print("PAWN MOVE")
        # index of current square in boardSquares
        print(squareIndex, "\n")

        piece = boardObjectSpaces[squareIndex]

        # plug base movements into list
        # left = squareIndex - 1
        # right = squareIndex + 1
        up = squareIndex - 8
        up2 = up - 8
        nw = squareIndex - 9
        ne = squareIndex - 7

        # sw = squareIndex + 7
        # se = squareIndex + 9
        # down = squareIndex + 8
        # possibleSpaces = [left,right,up,down]

        # both are upside down to eachother
        if self.color == "w":
            up = squareIndex - 8
            nw = squareIndex - 9
            ne = squareIndex - 7
            up2 = up - 8

        elif self.color == "b":
            up = squareIndex + 8
            nw = squareIndex + 7
            ne = squareIndex + 9
            up2 = up + 8

        possibleSpaces = [up, nw, ne]

        # lets pawns do a double move on their first move
        if self.color == "w":
            for space in row7:
                print(space)
                if boardObjectSpaces.index(self) == space:
                    possibleSpaces.append(up2)
        if self.color == "b":
            for space in row2:
                if boardObjectSpaces.index(self) == space:
                    possibleSpaces.append(up2)

        # make sure the piece isn't on row ends
        # if it is then remove appropriate move from list of moves
        # if squareIndex in range(0,56,+8):
        # can't go left
        # possibleSpaces.remove(left)
        # if squareIndex in range(7,63,+8):
        # can't go right
        # possibleSpaces.remove(right)

        ########
        # if squareIndex in range(0,8):
        # can't go up
        # possibleSpaces.remove(up)

        # if squareIndex in range(56,63):
        # can't go down
        # possibleSpaces.remove(down)

        origSquare = board[squareIndex]
        # print(origSquare)

        copyPossibleSpaces = possibleSpaces

        print(copyPossibleSpaces)

        ##########
        playColor = boardObjectSpaces[squareIndex].color

        # used to store spaces we will delete
        deleteSpaces = []

        # print(boardObjectSpaces)

        # determining the bunch of spaces that must be removed if counter is blocking the line of sight
        # need to use deletespaces otherwise I would mess up the for loop by editing it (copypossiblespaces) while looping it
        for var in copyPossibleSpaces:
            if var == up:
                if boardObjectSpaces[var] != "":
                    deleteSpaces.append(up)
                    deleteSpaces.append(up2)
                else:
                    pass
            if var == up2:
                if boardObjectSpaces[var] != "":
                    deleteSpaces.append(up2)
                else:
                    pass
            if var == nw:
                if squareIndex in col1:
                    deleteSpaces.append(nw)
                else:
                    if boardObjectSpaces[var] != "":
                        if boardObjectSpaces[var].color == playColor:
                            deleteSpaces.append(nw)
                        if boardObjectSpaces[var].color != playColor:
                            pass
                    else:
                        # if empty then can't move there
                        deleteSpaces.append(nw)
            if var == ne:
                if squareIndex in col8:
                    deleteSpaces.append(ne)
                else:
                    if boardObjectSpaces[var] != "":
                        if boardObjectSpaces[var].color == playColor:
                            deleteSpaces.append(ne)
                        if boardObjectSpaces[var].color != playColor:
                            pass
                    else:
                        deleteSpaces.append(ne)

        # removing spaces that are blocked
        for varia in deleteSpaces:
            if varia in copyPossibleSpaces:
                copyPossibleSpaces.remove(varia)
            else:
                pass

        # print(playColor)
        # print("copyPossibleSpaces", copyPossibleSpaces)

        # highlighting possible spaces in light purple
        for var in copyPossibleSpaces:
            posSpace = board[var]
            posSpace.config(bg="mediumpurple4")
            # EVENT
            # move on click
            posSpace.bind("<Button-1>",
                          lambda event: doMove(event, origSquare=origSquare, possibleMoves=copyPossibleSpaces))

        # EVENT
        # deselect on right click
        # lambda is necessary so arguments can be accepted inside the function inside bind()
        origSquare.bind("<Button-3>", lambda event: deselect(event, possibleSpaces=possibleSpaces))


labelTop()
labelSide()
MakeBoardCanvases()
root.mainloop()