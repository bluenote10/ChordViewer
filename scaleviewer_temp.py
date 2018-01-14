# encoding=utf-8
'''
This Rocks
'''

# Import Statements {{{
import wx
import time
import os
import sys
import ConfigParser
import glob
import re
# }}}

# Helper: Path Change {{{ 
relpath = os.path.dirname(sys.argv[0])
g_scriptpath = os.path.abspath(relpath)

def setpathscript():
    """
    Change path to script directory
    """
    os.chdir(g_scriptpath)
    return g_scriptpath

def setpathhome():
    """
    Change path to home directory
    """
    os.chdir(os.path.expanduser("~"))

# }}}

def LoadChords():#{{{
    setpathscript()
    f = open('chords.txt', 'r')

    chords = []
    descr = []
    for line in f.readlines():
        fields = line.split(",")
        fields = [i.strip() for i in fields]
        if len(fields) == 7:
            chords.append(fields[:6])
            descr.append(fields[6])

    return (chords, descr)
#}}}

def CalcNote(fret, i):#{{{
    absfret = fret
    if i == 1:      absfret += 5
    elif i == 2:    absfret += 10
    elif i == 3:    absfret += 15
    elif i == 4:    absfret += 19
    elif i == 5:    absfret += 24

    absfret = absfret % 12
    return absfret#}}}

def ShiftChordHoriz(chord, s):#{{{
    for i in range(6):
        if chord[i] != "x":
            chord[i] = str(int(chord[i]) + s)
    return chord
#}}}

def ShiftCordVertically(chord, strings):#{{{
    if strings == 0:
        return chord
    elif strings > 0:
        new = ['x']*6
        shift = [-5, -5, -5, -4, -5]
        for i in range(5):
            if chord[i] != "x":
                new[i+1] = str(int(chord[i]) + shift[i])
        return ShiftCordVertically(new, strings-1)
    elif strings < 0:
        new = ['x']*6
        shift = [5, 5, 5, 4, 5]
        for i in range(5):
            if chord[i+1] != "x":
                new[i] = str(int(chord[i+1]) + shift[i])
        return ShiftCordVertically(new, strings+1)
#}}}

def ChordDistance(chord, center):#{{{
    pos = AvgPos(chord)
    dist = [abs(pos-center), abs(pos-center+12), abs(pos-center-12)]
    return min(dist)
#}}}

def AvgPos(chord):#{{{
    chord = NormalizeChord(chord)
    n = 0
    sum = 0
    for i in range(6):
        if chord[i] != 'x':
            n += 1
            sum += int(chord[i])
    return float(sum) / n
#}}}

def NormalizeChord(chord):#{{{
    maxfret = -9999
    minfret = +9999
    for i in range(6):
        if chord[i] != 'x':
            f = int(chord[i])
            if f > maxfret:
                maxfret = f
            if f < minfret:
                minfret = f

    if maxfret / 12 != minfret / 12:
        num = maxfret / 12
        maxfret = maxfret % 12
        minfret = abs(12 - minfret % 12)
        print "maxfret", maxfret
        print "minfret", minfret
        print "num", num
        if maxfret > minfret:
            chord = ShiftChordHoriz(chord, -12 * num)
    else:
        for i in range(6):
            if chord[i] != 'x':
                chord[i] = str(int(chord[i]) % 12)

    """
    if minfret < 0:
        print abs(minfret) / 12
        chord = ShiftChordHoriz(chord, ((abs(minfret) / 12) + 1) * 12)

    print "minfret", minfret
    print "maxfret", maxfret
    minfret -= 12
    maxfret -= 12
    if abs(maxfret) >= abs(minfret):
        for i in range(6):
            if chord[i] != 'x':
                chord[i] = str(int(chord[i]) - 12)
    """
    return chord
#}}}

def HighlightCurChord(names, sel):#{{{
    text = ""

    for i in range(len(names)):
        if i != sel:
            text += "      " + names[i] + "\n"
        else:
            text += " ---> " + names[i] + "\n"
    return text#}}}

def ScoreChord(chord):#{{{
    s = set()
    score = 0
    for i in range(6):
        if chord[i] != 'x':
            s.add(CalcNote(int(chord[i]), i))

    if 0 in s: score += 10
    if 3 in s: score += 12
    if 4 in s: score += 12
    if 7 in s: score += 8
    if 10 in s: score += 8
    if 11 in s: score += 7
    return score#}}}

def NameChord(chord):#{{{
    s = set()
    name = ""
    for i in range(6):
        if chord[i] != 'x':
            s.add(CalcNote(int(chord[i]), i))

    if 3 in s: name = "Moll "
    if 4 in s: name = "Dur "

    if 10 in s: name += "7 "
    if 11 in s: name += "j7 "

    name += "("

    if 6 in s: name += "5-,"

    if 1 in s: name += "b9,"
    if 2 in s: name += "9,"
    if 5 in s: name += "11,"
    if 8 in s: name += "5+,"
    if 9 in s: name += "13,"

    if not 0 in s: name += "no root,"
    if not 7 in s: name += "no fifth,"

    if name[-1] == ',':
        name = name[:-1]

    name += ")"
    return name#}}}

def AnalyzeChords(chord): #{{{
    chords = []
    for i in range(12):
        new = ['x', 'x', 'x', 'x', 'x', 'x']
        for j in range(6):
            if chord[j] != 'x':
                new[j] = int(chord[j]) + i
        chords.append((ScoreChord(new), new, NameChord(new)))

    sum = 0
    sum = reduce(lambda x, y: x + y, [a for (a,b,c) in chords])
    chords = [(100.0 * float(a) / sum, b, c) for (a,b,c) in chords]

    chords = list(reversed(sorted(chords)))
    return ([b for (a,b,c) in chords], [c for (a,b,c) in chords])
#}}}

def ShiftChords(chord): #{{{

    down = 0
    up = 0
    while chord[down] == "x":
        down += 1
    while chord[5-up] == "x":
        up += 1

    print "down", down
    print "up", up

    chords = []

    for i in list(reversed(range(up))):
        new = NormalizeChord(ShiftCordVertically(chord, i+1))
        print i, new
        chords.append(new)

    chords.append(chord)

    for i in range(down):
        new = NormalizeChord(ShiftCordVertically(chord, -i-1))
        print i, new
        chords.append(new)

    print chords
    return (chords, up)
#}}}

def CalcNextInScale(scale, note, inc):
    print "before", note
    note = (note + inc) % 12
    while scale[note] == "":
        note = (note + inc) % 12
    print "after", note
    return note

class MainFrame(wx.Frame):
    def __init__(self): # {{{
        wx.Frame.__init__(self, None, -1, "Launcher")
        self.CreateStatusBar()

        # load chords
        self.scale = ["I","","D","","P","L","","M","","A","","-"]
        self.root = 8
        self.dispint = False
        self.modal = 0

        # create the UI elements ...
        self.output = wx.TextCtrl(self, 1, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)   # wx.WANTS_CHARS | wx.TE_RICH2
        self.output.WriteText("")
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Monospace')
        #font = wx.Font(self.fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New')
        self.output.SetFont(font)
        #self.input = wx.TextCtrl(self, 1, style = wx.TE_PROCESS_ENTER)
        #self.input.Bind(wx.EVT_KEY_DOWN, self.KeyPressed, self.input)
        #self.output.Bind(wx.EVT_LEFT_DOWN, self.MouseClick, self.output)
        #self.input.Bind(wx.EVT_TEXT, self.CmdLineChanged, self.input)
        #self.drawPanel = wx.Panel(self)
        self.drawPanel = wx.ScrolledWindow(self, -1, style=wx.SUNKEN_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.drawPanel.SetBackgroundColour(wx.WHITE)

        # ... do the layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.output, 1, wx.EXPAND)
        self.vbox.Add(self.drawPanel, 1, wx.EXPAND)
        self.SetSizer(self.vbox)
        self.SetAutoLayout(1)

        # bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.output.Bind(wx.EVT_KEY_DOWN, self.OnKey, self.output)
        #wx.EVT_CLOSE(self, self.OnClose)

        # ... and adjust the window size
        self.SetSize((1200, 800))
        self.Centre()
        self.Show(True)

        # give Focus
        self.output.SetFocus()
        self.Raise()


# }}}
    def OnPaint(self, evt): # {{{

        #fretfactor = 1.059463094
        fretfactor = 1.04

        maxx, maxy = self.drawPanel.GetSize()
        basey = maxy / 2
        stringspace = maxy / 12
        sy = [basey + stringspace * i for i in [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]]

        #print "basey", basey
        #print "stringspace", stringspace

        #self.drawPanel.SetBackgroundColour(wx.Color(0,0,0,255))
        #self.drawPanel.ClearBackground()

        dc = wx.PaintDC(self.drawPanel)
        try:
            gc = wx.GraphicsContext.Create(dc)
        except NotImplementedError:
            dc.DrawText("This build of wxPython does not support the wx.GraphicsContext family of classes.", 25, 25)
            return

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)

        gc.SetPen(wx.Pen("white", 1))
        gc.SetBrush(wx.Brush("white"))
        gc.DrawRectangle(0, 0, maxx, maxy)

        gc.SetPen(wx.Pen("navy", 1))
        gc.SetBrush(wx.Brush("black"))
        #gc.DrawRectangle(10,10, maxx - 20, maxy - 20)

        # draw strings
        for i in range(6):
            gc.DrawLines([(10, sy[i]), (maxx - 10, sy[i])])

        # calc baselength x
        startx = 10
        endx = maxx-10
        numfrets = 17 + 1
        sum = 0.0
        for i in range(numfrets-1):
            sum += fretfactor**(-i)
        x = (endx - startx) / sum

        # calc all frets
        frets = []
        frets.append(startx)
        lastx = startx
        for i in range(numfrets-1):
            frets.append(lastx + x * fretfactor**(-i))
            lastx = lastx + x * fretfactor**(-i)

        # draw frets
        for i in range(len(frets)):
            gc.DrawLines([(frets[i], sy[0]), (frets[i], sy[5])])

        # calc boxes
        box = []
        for i in range(len(frets) - 1):
            box.append((frets[i] + frets[i+1]) / 2)

        for i in range(len(box)):
            w, h = gc.GetTextExtent(str(i+1))
            if (i+1) in set([5,7,12,17,19]):
                gc.DrawText(str(i+1), box[i] - w/2, sy[5] + 40)
            if (i+1) in set([3,5,7,9,15,17,19,21]):
                r = 4
                gc.DrawEllipse(box[i] - r/2, sy[5] + 20, r, r)
            if i == 11:
                r = 4
                gc.DrawEllipse(box[i] - 5 - r/2, sy[5] + 20, r, r)
                gc.DrawEllipse(box[i] + 5 - r/2, sy[5] + 20, r, r)


        # draw scale
        """
        gc.SetPen(wx.Pen("navy", 1))
        gc.SetBrush(wx.Brush("lightblue"))

        for i in range(len(box)):
            for s in range(6):
                absfret = CalcNote(i - self.root + 1, s)
                modalfunc = CalcNote(i - self.root + 1 - self.modal, s)
                if self.scale[absfret] != '':
                    x = box[i]
                    size = stringspace / 3.5
                    if self.dispint == False:
                        gc.SetBrush(wx.Brush("lightblue"))
                    else:
                        if modalfunc == 0:
                            label = "1"
                            gc.SetFont(font, wx.Colour(255, 255, 255))
                            gc.SetBrush(wx.Brush(wx.Colour(0,0,0)))
                        elif modalfunc == 1:
                            label = "b9"
                            gc.SetFont(font, wx.Colour(0, 0, 0))
                            gc.SetBrush(wx.Brush("#ff003f"))
                        elif modalfunc == 2:
                            label = "9"
                            gc.SetFont(font, wx.Colour(255, 255, 255))
                            gc.SetBrush(wx.Brush("#699aa5"))
                        elif modalfunc == 3:
                            label = "b3"
                            gc.SetFont(font, wx.Colour(0, 0, 0))
                            gc.SetBrush(wx.Brush("#aec9e4"))
                            #gc.SetBrush(wx.Brush("#729fcf")) darker
                        elif modalfunc == 4:
                            label = "3"
                            gc.SetFont(font, wx.Colour(0, 0, 0))
                            #gc.SetBrush(wx.Brush("#ffc180")) bright
                            gc.SetBrush(wx.Brush("#ff8200"))
                        elif modalfunc == 5:
                            label = "11"
                            gc.SetFont(font, wx.Colour(255, 255, 255))
                            gc.SetBrush(wx.Brush("#fd8b8b"))
                        elif modalfunc == 6:
                            label = "5-"
                            gc.SetFont(font, wx.Colour(255, 255, 255))
                            gc.SetBrush(wx.Brush("#ff00c9"))
                        elif modalfunc == 7:
                            label = "5"
                            gc.SetFont(font, wx.Colour(0, 0, 0))
                            gc.SetBrush(wx.Brush("#FFFFFF"))
                            #gc.SetBrush(wx.Brush("#4c80c7")) blue
                        elif modalfunc == 8:
                            label = "#5"
                            gc.SetFont(font, wx.Colour(0, 0, 0))
                            gc.SetBrush(wx.Brush("#fffe00"))
                            #gc.SetBrush(wx.Brush("#1cff00")) green
                        elif modalfunc == 9:
                            label = "13"
                            gc.SetFont(font, wx.Colour(255, 255, 255))
                            gc.SetBrush(wx.Brush("#ad7fa8"))
                        elif modalfunc == 10:
                            label = "7"
                            gc.SetFont(font, wx.Colour(0, 0, 0))
                            gc.SetBrush(wx.Brush("#d18a19"))
                        elif modalfunc == 11:
                            label = "j7"
                            gc.SetFont(font, wx.Colour(255, 255, 255))
                            gc.SetBrush(wx.Brush("#8ae234"))


                    gc.DrawEllipse(x - size, sy[5-s] - size, size*2, size*2)
                    label = self.scale[absfret]
                    w, h = gc.GetTextExtent(label)
                    gc.DrawText(label, int(x - float(w) / 2.0), int(sy[5-s] - float(h) / 2.0))
        """

# }}}
    def UpdateText(self): # {{{
        self.output.Clear()
        #self.output.WriteText(NameChord(self.chords[self.curchord]))
    # }}}
    def OnKey(self, evt): # {{{
        keycode = evt.GetKeyCode()
        print keycode

        if keycode == wx.WXK_NUMPAD_ADD:
            self.root += 1
            self.OnPaint(evt)
        elif keycode == wx.WXK_NUMPAD_SUBTRACT:
            self.root -= 1
            self.OnPaint(evt)
        elif keycode == 73: # i
            self.dispint = [True, False][self.dispint]
            self.OnPaint(evt)
        elif keycode == 74: # j
            self.modal = CalcNextInScale(self.scale, self.modal, -1)
            self.OnPaint(evt)
        elif keycode == 75: # k
            self.modal = CalcNextInScale(self.scale, self.modal, +1)
            self.OnPaint(evt)
        elif keycode == 72: # h
            self.modal = CalcNextInScale(self.scale, self.modal, -1)
            self.modal = CalcNextInScale(self.scale, self.modal, -1)
            self.modal = CalcNextInScale(self.scale, self.modal, -1)
            self.modal = CalcNextInScale(self.scale, self.modal, -1)
            self.OnPaint(evt)
        elif keycode == 76: # l
            self.modal = CalcNextInScale(self.scale, self.modal, +1)
            self.modal = CalcNextInScale(self.scale, self.modal, +1)
            self.modal = CalcNextInScale(self.scale, self.modal, +1)
            self.modal = CalcNextInScale(self.scale, self.modal, +1)
            self.OnPaint(evt)
    # }}}
    def OnKeyBrowse(self, evt, keycode): # {{{
        if keycode == wx.WXK_LEFT:
            self.curchord -= 1
            if self.curchord < 0:
                self.curchord += len(self.chords)
            self.UpdateText()
            self.SetStatusText("Chord " + str(self.curchord+1) + "/" + str(len(self.chords)))
            self.OnPaint(evt)
        elif keycode == wx.WXK_RIGHT:
            self.curchord += 1
            if self.curchord >= len(self.chords):
                self.curchord -= len(self.chords)
            self.UpdateText()
            self.SetStatusText("Chord " + str(self.curchord+1) + "/" + str(len(self.chords)))
            self.OnPaint(evt)
        elif keycode >= 340 and keycode <= 351:
            center = keycode - 339
            self.chords = [b for (a,b) in sorted([(ChordDistance(i, center), i) for i in self.chords])]
            self.curchord = 0
            self.UpdateText()
            self.SetStatusText("Chord " + str(self.curchord+1) + "/" + str(len(self.chords)))
            self.OnPaint(evt)
        elif keycode == wx.WXK_TAB:
            self.chords = [b for (a,b) in sorted([(AvgPos(i),i) for i in self.chords])]
            self.curchord = 0
            self.UpdateText()
            self.SetStatusText("Chord " + str(self.curchord+1) + "/" + str(len(self.chords)))
            self.OnPaint(evt)
        elif keycode == 65: # A
            self.mode = 'analyze'
            self.backup = (self.chords, self.curchord)
            self.chords, self.analyzednames = AnalyzeChords(self.chords[self.curchord])
            self.curchord = 0
            self.output.Clear()
            self.output.WriteText(HighlightCurChord(self.analyzednames, self.curchord))
            self.OnPaint(evt)
        elif keycode == 83: # S
            self.mode = 'shift'
            self.backup = (self.chords, self.curchord)
            self.chords, self.curchord = ShiftChords(self.chords[self.curchord])
            self.output.Clear()
            #self.output.WriteText(HighlightCurChord(self.analyzednames, self.curchord))
            self.OnPaint(evt)
    # }}}
    def OnKeyAnalyze(self, evt, keycode): # {{{
        if keycode == wx.WXK_UP:
            self.curchord -= 1
            if self.curchord < 0:
                self.curchord += len(self.chords)
            self.output.Clear()
            self.output.WriteText(HighlightCurChord(self.analyzednames, self.curchord))
            self.OnPaint(evt)
        elif keycode == wx.WXK_DOWN:
            self.curchord += 1
            if self.curchord >= len(self.chords):
                self.curchord -= len(self.chords)
            self.output.Clear()
            self.output.WriteText(HighlightCurChord(self.analyzednames, self.curchord))
            self.OnPaint(evt)
        elif keycode == wx.WXK_ESCAPE:
            self.mode = 'std'
            self.chords, self.curchord = self.backup
            self.UpdateText()
            self.OnPaint(evt)
    # }}}
    def OnKeyShift(self, evt, keycode): # {{{
        if keycode == wx.WXK_UP:
            self.curchord -= 1
            if self.curchord < 0:
                self.curchord += len(self.chords)
            self.output.Clear()
            #self.output.WriteText(HighlightCurChord(self.analyzednames, self.curchord))
            self.OnPaint(evt)
        elif keycode == wx.WXK_DOWN:
            self.curchord += 1
            if self.curchord >= len(self.chords):
                self.curchord -= len(self.chords)
            self.output.Clear()
            #self.output.WriteText(HighlightCurChord(self.analyzednames, self.curchord))
            self.OnPaint(evt)
        elif keycode == wx.WXK_ESCAPE:
            self.mode = 'std'
            self.chords, self.curchord = self.backup
            self.UpdateText()
            self.OnPaint(evt)
    # }}}


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainFrame()
    app.MainLoop()



# {{{

"""
transpose = [[  0,  5,  10,  15,  19,  24],
             [ -5,  0,   5,  10,  14,  19],
             [-10, -5,   0,   5,   9,  15],
             [-15, -10, -5,   0,   4,   9],
             [-19, -15,-10,  -5,   0,   5],
             [-24, -19,-15, -10,  -5,   9]]
"""



"""
# make a path that contains a circle and some lines, centered at 0,0
path = gc.CreatePath()
path.AddCircle(100, 100, BASE2)
path.MoveToPoint(0, -BASE2)
path.AddLineToPoint(0, BASE2)
path.MoveToPoint(-BASE2, 0)
path.AddLineToPoint(BASE2, 0)
path.CloseSubpath()
path.AddRectangle(-BASE4, -BASE4/2, BASE2, BASE4)

# Now use that path to demonstrate various capbilites of the grpahics context
gc.PushState()             # save current translation/scale/other state 
gc.Translate(60, 75)       # reposition the context origin

gc.SetPen(wx.Pen("navy", 1))
gc.SetBrush(wx.Brush("pink"))

# show the difference between stroking, filling and drawing
for label, PathFunc in [("StrokePath", gc.StrokePath),
                        ("FillPath",   gc.FillPath),
                        ("DrawPath",   gc.DrawPath)]:
    w, h = gc.GetTextExtent(label)
    
    gc.DrawText(label, -w/2, -BASE2-h-4)
    PathFunc(path)
    gc.Translate(2*BASE, 0)

    
gc.PopState()              # restore saved state
gc.PushState()             # save it again
gc.Translate(60, 200)      # offset to the lower part of the window

gc.DrawText("Scale", 0, -BASE2)
gc.Translate(0, 20)


gc.DrawPath(path)
"""
        
# }}}
