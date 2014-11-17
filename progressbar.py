import fcntl
import termios
import struct
import sys
import time

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
SECONDS_IN_A_DAY = 86400
SECONDS_IN_A_HOUR = 3600
SECONDS_IN_A_MINUTE = 60


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
        self.firstTick = True
        self.createTime = int(time.time())
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
        now = time.time()
        if not self.firstTick:
            delay = now - self.lastTime
            self.meanDelay = (delay + (self.progress-1)*self.meanDelay) / float(self.progress)
            ticksToFinish = self.taskLength - self.progress
            timeToFinish = int(self.meanDelay * ticksToFinish)
            days = timeToFinish / SECONDS_IN_A_DAY
            surplus = timeToFinish - days * SECONDS_IN_A_DAY
            hours = (surplus) / SECONDS_IN_A_HOUR
            surplus = surplus - hours * SECONDS_IN_A_HOUR
            minutes = (surplus) / SECONDS_IN_A_MINUTE
            seconds = surplus - minutes * SECONDS_IN_A_MINUTE
            daysLabel = "" if days <= 0 else "%dd" % days
            hoursLabel = "00" if hours <= 0 else "%02d" % hours
            minutesLabel = "00" if minutes <= 0 else "%02d" % minutes
            secondsLabel = "00" if seconds <= 0 else "%02d" % seconds
            timeDisplay = "%s %s:%s:%s" % (daysLabel,
                                           hoursLabel,
                                           minutesLabel,
                                           secondsLabel)

        else:
            # self.meanDelay = now - self.createTime
            self.meanDelay = 0
            timeDisplay = ""
        # counter = "%.1f%%" % (nProgress*100)
        counter = "%d of %d (%.1f%%) %s" % (self.progress,
                                            self.taskLength,
                                            nProgress*100,
                                            timeDisplay)
        screenLength = terminal_size()[0]
        leftBarLength = int((screenLength-len(counter))/2.0)
        rightBarLength = screenLength - leftBarLength - len(counter)
        leftBar = self.getLeftBar(self.getScreenProgress(), leftBarLength)
        rightBar = self.getRightBar(self.getScreenProgress(),
                                    rightBarLength,
                                    screenLength)
        print CURSOR_UP_ONE + ERASE_LINE
        self.lastTime = now
        return leftBar + counter + rightBar + "\r"

    def tick(self):
        print self,
        if self.firstTick:
            self.firstTick = False
# p = ProgressBar(100000)
# for i in range(100000):
#     time.sleep(.001)
#     p.tick()
