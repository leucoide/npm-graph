import fcntl
import termios
import struct
import sys
import time

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


def terminal_size():
    h, w, hp, wp = struct.unpack('HHHH',
                                 fcntl.ioctl(0,
                                             termios.TIOCGWINSZ,
                                             struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h


class ProgressBar(object):
    """docstring for ProgressBar"""
    def __init__(self, taskLength, autoUpdate=True):
        self.taskLength = taskLength
        self.autoUpdate = autoUpdate
        self.progress = 0

    def update(self):
        self.progress += 1

    def getNormalizedProgress(self):
        return round((self.progress/float(self.taskLength)), 5)

    def getScreenProgress(self):
        nProgress = self.getNormalizedProgress()
        screenLength = terminal_size()[0]

        return int(nProgress*screenLength)

    def getLeftBar(self, progress, length):
        if progress <= length:
            return "="*progress + " "*(length-progress)
            # print "a"*(length-progress)
        else:
            return "="*length

    def getRightBar(self, progress, length, screen):
        rightProgress = progress - (screen - length)
        if rightProgress > 0:
            return "="*rightProgress + " "*(length-rightProgress)
        else:
            return " "*length

    def __repr__(self):
        if self.autoUpdate:
            self.update()
        nProgress = self.getNormalizedProgress()

        # counter = "%.1f%%" % (nProgress*100)
        counter = "%d of %d (%.1f%%)" % (self.progress,
                                         self.taskLength,
                                         nProgress*100)
        screenLength = terminal_size()[0]
        leftBarLength = int((screenLength-len(counter))/2.0)
        rightBarLength = screenLength - leftBarLength - len(counter)
        leftBar = self.getLeftBar(self.getScreenProgress(), leftBarLength)
        rightBar = self.getRightBar(self.getScreenProgress(),
                                    rightBarLength,
                                    screenLength)
        print CURSOR_UP_ONE + ERASE_LINE
        return leftBar + counter + rightBar + "\r"

    def tick(self):
        print self,
# p = ProgressBar(100000)
# for i in range(100000):
#     time.sleep(.001)
#     p.tick()
