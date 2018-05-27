import sys, time
from subprocess import call
import pymysql.cursors
import urllib
import glob
from random import shuffle
import sqlite3
# conn.text_factory = str
from PyQt5 import QtGui, QtCore, QtWidgets, QtMultimedia, QtMultimediaWidgets
import argparse
import random
import os
import vlc

import sys, os

application_path = '.\\'#'\\\\192.168.0.5\\iSCSI\\db\\'

import pyglet

class slideShowClass(pyglet.window.Window):

    # display = pyglet.window.Display()
    # screen = display.get_screens()[1]

    def __init__(self, path, globString, slideDelay=4.0, randomOrder=False):
        super(slideShowClass, self).__init__(fullscreen=True,screen=pyglet.window.Display().get_screens()[1])
        self.globString = globString
        self.randomOrder = randomOrder
        self.set_fullscreen(True)
        self.doingShow = False
        self.on_key_press = self.on_key_press
        # self.on_text_motion = self.on_text_motion
        # self.on_text = self.on_text
        self.path = path
        self.image_paths = self.get_image_paths(self.path)
        if len(self.image_paths) < 2:
            print 'empty = ', self.path
            print 'glob = ', self.globString
        self.imagenumber = -1
        self.event_loop = pyglet.app.EventLoop()
        self.slideDelay = slideDelay
        self.updateDelay = True
        self.paused = False
        pyglet.clock.schedule_once(self.update_image, 0.0)
        pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        pyglet.app.run()
        # self.update_image(0.001)

    def update_image(self, dt):
        if not self.doingShow:
            self.doingShow = True
            self.imagenumber = self.imagenumber + 1
            if self.imagenumber >= len(self.image_paths):
                pyglet.clock.unschedule(self.update_image)
                pyglet.app.exit()
                self.close()
            else:
                self.img = pyglet.image.load(self.image_paths[self.imagenumber])
                self.sprite = pyglet.sprite.Sprite(self.img,subpixel=True)
                self.sprite.image = self.img
                self.sprite.scale = self.get_scale(self, self.img)
                self.sprite.x, self.sprite.y = self.get_pos(self, self.img, self.sprite.scale)
                self.clear()
                self.sprite.draw()
            self.doingShow = False

    def get_image_paths(self, input_dir='.'):
        paths = sorted(glob.glob(input_dir+self.globString))
        if self.randomOrder:
            paths = shuffle(paths)
        return paths

    def get_scale(self, window, image):
        if image.width > image.height:
            scale = float(window.width) / image.width
        else:
            scale = float(window.height) / image.height
        return scale

    def get_pos(self, window, image, scale):
        xpos = (float(window.width) - (scale*image.width)) / 2.0
        ypos = (float(window.height) - (scale*image.height)) / 2.0
        return [xpos, ypos]

    def exit(self):
        pyglet.clock.unschedule(self.update_image)
        pyglet.app.exit()

    def on_text(self, text):
        pass

    def on_text_motion(self, motion):
        return True

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            pyglet.clock.unschedule(self.update_image)
            pyglet.clock.schedule_once(self.update_image, 0.0)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        if button == pyglet.window.mouse.RIGHT:
            self.imagenumber = self.imagenumber - 2
            pyglet.clock.unschedule(self.update_image)
            pyglet.clock.schedule_once(self.update_image, 0.0)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        if button == pyglet.window.mouse.MIDDLE:
            pyglet.clock.unschedule(self.update_image)
            pyglet.app.exit()
            self.close()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y < 0:
            pyglet.clock.unschedule(self.update_image)
            pyglet.clock.schedule_once(self.update_image, 0.0)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        elif scroll_y > 0:
            self.imagenumber = self.imagenumber - 2
            pyglet.clock.unschedule(self.update_image)
            pyglet.clock.schedule_once(self.update_image, 0.0)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)

    def on_text_motion(self, motion):
        if motion == pyglet.window.key.MOTION_UP or motion == pyglet.window.key.MOTION_RIGHT or motion == pyglet.window.key.MOTION_DOWN or motion == pyglet.window.key.MOTION_LEFT:
            pass

    # def on_text(self,text):
    #     if symbol == pyglet.window.key.RIGHT or symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.UP or symbol == pyglet.window.key.DOWN:
    #         pass

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.RIGHT or symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.UP or symbol == pyglet.window.key.DOWN:
            pass

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.RIGHT:
            pyglet.clock.unschedule(self.update_image)
            pyglet.clock.schedule_once(self.update_image, 0.0)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        elif symbol == pyglet.window.key.LEFT:
            self.imagenumber = self.imagenumber - 2
            pyglet.clock.unschedule(self.update_image)
            pyglet.clock.schedule_once(self.update_image, 0.0)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        elif symbol == pyglet.window.key.UP:
            self.clear()
            self.sprite.draw()
            if self.slideDelay == 0.5:
                self.slideDelay = 1.0
            else:
                self.slideDelay = self.slideDelay + 0.5
            self.updateDelay = True
            pyglet.clock.unschedule(self.update_image)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        elif symbol == pyglet.window.key.DOWN:
            self.clear()
            self.sprite.draw()
            self.slideDelay = self.slideDelay - 0.5
            if self.slideDelay < 0.5:
                self.slideDelay = 0.5
            self.updateDelay = True
            pyglet.clock.unschedule(self.update_image)
            if not self.paused:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
        elif symbol == pyglet.window.key.SPACE:
            self.clear()
            self.sprite.draw()
            if not self.paused:
                pyglet.clock.unschedule(self.update_image)
                self.paused = True
            else:
                pyglet.clock.schedule_interval(self.update_image, self.slideDelay)
                self.paused = False
        elif symbol == 65307:
            pyglet.clock.unschedule(self.update_image)
            pyglet.app.exit()
            self.close()
        else:
            self.clear()
            self.sprite.draw()

class videoWidget(QtWidgets.QMainWindow):

    def __init__(self, path, parent=None):
        super(videoWidget, self).__init__()
        self.setStyleSheet("QMainWindow {background: 'black';}");
        self.showFullScreen()
        self.setMinimumSize(300, 300)
        self.path = path
        self.widget = QtWidgets.QWidget()
        self.media = QtCore.QUrl.fromLocalFile(self.path)
        self.content= QtMultimedia.QMediaContent(self.media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(self.content)
        self.videoWidget = QtMultimediaWidgets.QVideoWidget()
        # self.layout.addWidget(self.videoWidget)
        self.setCentralWidget(self.videoWidget)
        self.player.setVideoOutput(self.videoWidget)
        self.player.play()
        self.show()
        self.directory = ''
        self.player.mediaStatusChanged.connect(self.closeWhenFinished)

    def closeWhenFinished(self, status):
        if status == 7:
            self.close()

    def keyPressEvent(self, e):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            incr = 30
        elif modifiers == QtCore.Qt.ControlModifier:
            incr = 60
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            incr = 5*60
        else:
            incr = 10
        if e.key() == QtCore.Qt.Key_Space:
            if self.player.state() == 1:
                self.player.pause()
            elif self.player.state() == 2:
                self.player.play()
        if e.key() == 16777236:
            if (self.player.position() + (incr*1000)) > self.player.duration():
                self.player.setPosition(self.player.duration())
            else:
                self.player.setPosition(self.player.position() + (incr*1000))
        if e.key() == 16777234:
            self.player.setPosition(self.player.position() - (incr*1000))
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        try:
            self.player.stop()
            del self.player
        except:
            pass

class noMouseWheel(QtCore.QObject):
    def eventFilter(self, receiver, event):
        # print event.type()
        if(event.type() == 31):
            return True
        else:
            return super(noMouseWheel,self).eventFilter(receiver, event)

class imageLink(QtWidgets.QWidget):

    modelClickedSignal = QtCore.pyqtSignal('QString')
    modelRatingChanged = QtCore.pyqtSignal('QString','QString')

    def __init__(self, result=[], parent=None):
        super(imageLink, self).__init__()
        global thumbshelf
        self.parent = parent
        self.site = self.parent.chosenSite
        if self.site == "wowporn" or self.site == "esnap":
            self.setMinimumWidth(250)
            self.setMaximumWidth(250)
            self.setMinimumHeight(200)
            self.setMaximumHeight(200)
        else:
            self.setMinimumWidth(250)
            self.setMaximumWidth(250)
            self.setMinimumHeight(400)
            self.setMaximumHeight(400)
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        entry = result
        if self.site == "wowporn" or self.site == "esnap":
            try:
                self.model, self.thumb, self.directory, self.date, self.photographer, self.rating, self.video, self.setname = entry
                self.id = self.thumb
            except:
                pass
        elif self.site == "met":
            self.id, self.model, self.thumb, self.directory, self.date, self.photographer, self.rating = entry
            self.video = 0
        elif self.site == "abby":
            self.id, self.model, self.thumb, self.directory, self.date, self.rating = entry
            self.video = 0
        else:
            self.id, self.model, self.thumb, self.directory, self.date, self.rating, self.video = entry
        self.siteChanged(self.site)
        # self.url = 'http://192.168.0.8:8888/'+self.thumb
        # self.data = urllib.urlopen(self.url).read()
        # self.pixmap = QtGui.QPixmap()
        # self.pixmap.loadFromData(self.data)
        if type(self.pathReplace) is list:
            for i in range(len(self.pathReplace)):
                self.thumb = self.thumb.replace(self.pathReplace[i],self.pathReplaceWith[i])
        else:
            self.thumb = self.thumb.replace(self.pathReplace,self.pathReplaceWith)
        if self.site == "wowporn" or self.site == "esnap":
            if type(self.pathReplace) is list:
                for i in range(len(self.pathReplace)):
                    self.directory = self.directory.replace(self.pathReplace[i],self.pathReplaceWith[i])
            else:
                self.directory = self.directory.replace(self.pathReplace,self.pathReplaceWith)
            self.path = self.mainPath+self.directory.replace('/','\\')
            #print self.path
            # print self.path+'gif'
            self.label.enterEvent = self.startMovie
            self.label.leaveEvent = self.stopMovie
        ''' ***************************************************************************************************** '''
        thumbshelf.execute('select * from thumbs where filename=?', (self.thumb,))
        result = thumbshelf.fetchone()
        if not result == None and self.thumb in result:
            save = False
            thumbdata = str(result[1])
        else:
            save = True
            print 'Not in db!'
            with open(self.mainPath+self.thumb.replace('/','\\'), 'rb') as f:
                thumbdata = f.read()
        ''' ***************************************************************************************************** '''
        self.pixmap = QtGui.QPixmap()
        self.pixmap.loadFromData(thumbdata)
        # print 'width = ',self.pixmap.width(),'\theight = ',self.pixmap.height()
        if save:
            if float(self.pixmap.width()) / 250.0 > float(self.pixmap.height()) / 300.0:
                self.pixmap = self.pixmap.scaledToWidth(250,QtCore.Qt.SmoothTransformation)
            else:
                self.pixmap = self.pixmap.scaledToHeight(300,QtCore.Qt.SmoothTransformation)
            pixmapImage = self.pixmap.toImage()
            ba = QtCore.QByteArray()
            abuffer = QtCore.QBuffer(ba)
            abuffer.open(QtCore.QIODevice.WriteOnly)
            pixmapImage.save(abuffer, "JPG")
            abuffer.close()
            self.pixmap = QtGui.QPixmap()
            # bastring = QtCore.QString(ba)
            # bastring = bastring.toUtf8()
            # print '2'
            self.pixmap.loadFromData(ba)
            # print bastring
            # print '3'
            t = (self.thumb, buffer(ba))
            thumbshelf.execute("""insert into thumbs values (?,?)""", t)
            conn.commit()
        self.label.setPixmap(self.pixmap)
        self.label.mousePressEvent = self.imageClicked
        modelText = QtWidgets.QPushButton(self.model)
        modelText.clicked.connect(self.modelClicked)
        if self.site == "abby":
            dateText = QtWidgets.QLabel("")
        else:
            date = time.strptime(str(self.date),'%Y%m%d')
            dateText = QtWidgets.QLabel(time.strftime("%d/%m/%Y",date))
        # self.dateText.setStyleSheet("QLabel { color : white; }");
        self.ratingsBox = QtWidgets.QComboBox()
        for rating in range(6):
            self.ratingsBox.addItem(str(rating))
        self.ratingsBox.setCurrentIndex(int(self.rating))
        self.ratingsBox.currentIndexChanged.connect(self.updateRating)
        self.ratingsBox.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.myFilter	 = noMouseWheel()
        self.ratingsBox.installEventFilter(self.myFilter)
        layout.addWidget(self.label)
        modelRateLayout = QtWidgets.QHBoxLayout()
        # self.modelRateLayout.setAlignment(QtCore.Qt.AlignCenter)
        modelRateLayout.addWidget(modelText)
        modelRateLayout.addWidget(dateText)
        modelRateLayout.addWidget(self.ratingsBox)
        modelRateWidget = QtWidgets.QWidget()
        modelRateWidget.setMaximumHeight(100)
        modelRateWidget.setLayout(modelRateLayout)
        layout.addWidget(modelRateWidget)
        self.setLayout(layout)
        self.parent.siteChangedSignal.connect(self.siteChanged)

    def startMovie(self, event):
        if self.site == "wowporn" or self.site == "esnap":
            if os.path.isfile(self.path+'.gif'):
                self.movie = QtGui.QMovie(self.path+'.gif')
                self.label.enterEvent = self.startMovie
                self.label.leaveEvent = self.stopMovie
                self.label.setMovie(self.movie)
                self.movie.start()

    def stopMovie(self, event):
        if self.site == "wowporn"  or self.site == "esnap" and hasattr(self,'movie'):
            self.movie.stop()
            self.label.setPixmap(self.pixmap)
            del self.movie

    def ratingsBoxFilter(self, reciever, event):
        if(event.type() == QEvent.Wheel):
            pass

    def updateRating(self, i):
        self.ratingsBox.setCurrentIndex(i)
        self.modelRatingChanged.emit(str(self.id),str(i))

    def getPixmap(self):
        return self

    def imageClicked(self, event):
        if event.button() == 1:
            if type(self.pathReplace) is list:
                for i in range(len(self.pathReplace)):
                    self.directory = self.directory.replace(self.pathReplace[i],self.pathReplaceWith[i])
            else:
                self.directory = self.directory.replace(self.pathReplace,self.pathReplaceWith)
            self.path = self.mainPath+self.directory.replace('/','\\')
            if self.video == 1:
                # call("\"C:\Program Files (x86)\K-Lite Codec Pack\MPC-HC64\mpc-hc64.exe\" /play /close /fullscreen \""+self.path, shell=True)
                self.videowidget = videoWidget(self.path)
            else:
                self.runSlideShow()
                # call("\"C:\Program Files (x86)\IrfanView\i_view32.exe\" /fs /one /resample /closeslideshow /slideshow=\""+self.path+"\\*.jpg\"", shell=True)

    def runSlideShow(self):
        self.parent.runSlideShow(self.path, self.globString)

    def modelClicked(self):
        self.modelClickedSignal.emit(self.model)

    def siteChanged(self, site):
        self.site = site
        if self.site == "errotica":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\members.errotica-archives.com\\'
            self.pathReplace = 'errofiles2/'
            self.pathReplaceWith = ''
            if 'files/' in self.directory:
                self.globString = '\\*_l.jpg'
            else:
                self.globString = '\\*high*.jpg'
        elif self.site == "wowporn":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\wowporn\\'
            self.pathReplace = 'wowfiles/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "esnap":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\esnap\\'
            self.pathReplace = 'esnap/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "abby":
            self.mainPath = '\\\\192.168.0.14\\met-art\\nl-g2.abbywinters.com\\'
            self.pathReplace = 'abby/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "met":
            self.mainPath = '\\\\192.168.0.14\\met-art\\members.met-art.com\\members\\'
            self.pathReplace = ['met/','t_']
            self.pathReplaceWith = ['','']
            if 'hires' in self.directory:
                self.globString = '\\*.jpg'
            else:
                self.globString = '\\h_*.jpg'

class myQtableWidget(QtWidgets.QTableWidget):

    loadRowSignal = QtCore.pyqtSignal(int)
    updateMainGuiSignal = QtCore.pyqtSignal()

    def __init__(self, rows, columns,  parent = None):
        super(myQtableWidget, self).__init__(rows, columns, parent)
        self.setShowGrid(False)
        self.parent = parent
        self.vbar = self.verticalScrollBar()
        self.vbar.valueChanged.connect(self.vbarMoved)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def wheelEvent(self,event):
        delta = event.angleDelta().y()
        self.vbar.setValue(self.vbar.value()-(delta))

    def mousePressEvent(self, event):
        pass

    def vbarMoved(self, change):
        self.loadRowSignal.emit(self.vbar.value())

    def vbarMoveToPos(self,pos):
        print 'goal pos = ', pos
        while self.vbar.value() < (pos-500):
            self.vbar.setValue(pos)

class scrollableWidget(QtWidgets.QWidget):

    def __init__(self, rows, columns, parent = None):
        super(scrollableWidget, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        self.scrollContent = myQtableWidget(1, columns, self)
        self.layout.addWidget(self.scrollContent)

    def clear(self):
        self.scrollContent.clear()
        self.scrollContent.setRowCount(0)

class SetBrowser(QtWidgets.QMainWindow):

    siteChangedSignal = QtCore.pyqtSignal('QString')
    loadThumbnailsSignal = QtCore.pyqtSignal(int)
    dataReady = QtCore.pyqtSignal('QObject', int, int)

    def __init__(self, parent = None):
        super(SetBrowser, self).__init__(parent)
        self.setWindowTitle("SetBrowser")
        self.showFullScreen()
        self.show()

        self.tab = QtWidgets.QFrame()
        self.layout = QtWidgets.QGridLayout()

        self.sites = ['errotica', 'met', 'abby', 'wowporn','esnap']
        self.siteSelectionBox = QtWidgets.QComboBox()
        for site in self.sites:
            self.siteSelectionBox.addItem(site)
        self.siteSelectionBox.setCurrentIndex(0)
        self.chosenSite = self.sites[0]
        self.siteSelectionBox.currentIndexChanged.connect(self.changeSite)

        self.videosCheckBox = QtWidgets.QCheckBox('Only Videos')
        self.videosCheckBox.clicked.connect(lambda: self.loadTable(row=None))

        self.randomOrder = False
        self.randomCheckBox = QtWidgets.QPushButton('Random')
        self.randomCheckBox.setMaximumWidth(100)
        self.randomCheckBox.clicked.connect(lambda: self.loadTable(random=True))
        self.randomCheckBox.setChecked(False)

        self.tables = ['sets','best']
        self.tableSelectionBox = QtWidgets.QComboBox()
        for table in self.tables:
            self.tableSelectionBox.addItem(table)
        self.tableSelectionBox.setCurrentIndex(0)
        self.chosenTable = self.tables[0]
        self.tableSelectionBox.currentIndexChanged.connect(self.changeTable)

        self.years = ['All']
        [self.years.append(str(x)) for x in reversed(range(2000,2018))]
        self.yearsSelectionBox = QtWidgets.QComboBox()
        for year in self.years:
            self.yearsSelectionBox.addItem(year)
        self.yearsSelectionBox.setCurrentIndex(0)
        self.chosenYear = 'All'
        self.yearsSelectionBox.currentIndexChanged.connect(self.changeYear)

        self.backButton = QtWidgets.QPushButton("Back")
        self.backButton.clicked.connect(self.backButtonClicked)
        self.backButton.hide()

        self.model = ""

        self.slideDelay = 3.0

        self.emptyPic = QtWidgets.QWidget()
        self.emptyPic.setMinimumWidth(250)
        self.emptyPic.setMaximumWidth(250)
        self.emptyPic.setMinimumHeight(400)
        self.emptyPic.setMaximumHeight(400)

        self.centralWidget = QtWidgets.QWidget()
        self.centralLayout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(self.centralLayout)
        self.bar = QtWidgets.QWidget()
        self.layoutBar = QtWidgets.QHBoxLayout()
        self.bar.setLayout(self.layoutBar)
        self.centralLayout.addWidget(self.bar)
        self.rows = 1
        self.columns = 6
        self.widgetMain = scrollableWidget(self.rows,self.columns)
        self.widget = self.widgetMain
        self.widgetModel = scrollableWidget(self.rows,self.columns)
        self.widgetModel.hide()
        self.centralLayout.addWidget(self.widgetMain)
        self.centralLayout.addWidget(self.widgetModel)
        self.widgetMain.scrollContent.loadRowSignal.connect(self.addNewRow)
        self.setCentralWidget(self.centralWidget)
        self.loadThumbnailsSignal.connect(self.loadThumbnails)
        self.dataReady.connect(self.addThumbnail)

    def addNewRow(self, row):
        self.row = int(row/self.rowHeight)
        if len(self.widget.scrollContent.rowList) > 0 and self.row > max(self.widget.scrollContent.rowList) - self.rows:
            # for i in range(row+self.rows+2):
                self.loadTable(self.row+self.rows)
        # print 'number of imageLinks = ', len(self.findChildren(QtCore.QObject))

    def setBarLayout(self):
        self.layoutBar.addWidget(self.backButton)
        self.layoutBar.addWidget(self.siteSelectionBox)
        self.layoutBar.addWidget(self.tableSelectionBox)
        self.layoutBar.addWidget(self.yearsSelectionBox)
        self.layoutBar.addWidget(self.videosCheckBox)
        self.layoutBar.addWidget(self.randomCheckBox)

    def changeYear(self,i):
        self.chosenYear = self.yearsSelectionBox.currentText()
        self.offset = 0
        self.loadTable()

    def runSlideShow(self, path, globString):
        self.slideshow = slideShowClass(path, globString, self.slideDelay)
        self.slideDelay = self.slideshow.slideDelay
        self.slideshow.exit()

    def addThumbnail(self, thumb, row, col):
        widgetItem = QtWidgets.QWidget()
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.setAlignment(QtCore.Qt.AlignCenter)
        widgetLayout.addWidget(thumb)
        widgetItem.setLayout(widgetLayout)
        # print 'row/col = ',row,'/',col
        self.widget.scrollContent.setCellWidget(row,col,widgetItem)
        if self.widget.scrollContent.rowHeight(row) > 0:
            self.rowHeight = self.widget.scrollContent.rowHeight(row)
        self.widget.scrollContent.resizeColumnsToContents()
        self.widget.scrollContent.resizeRowsToContents()

    def loadTable(self, row=None, random=False):
        if row == None:
            self.getData(random)
            self.widget.clear()
            self.widget.scrollContent.rowList = list()
            self.widget.scrollContent.vbar.setValue(0)
            for i in range(self.rows):
                self.loadTable(i, self.widget.scrollContent)
        elif not row in self.widget.scrollContent.rowList and row*self.columns < len(self.result):
            self.widget.scrollContent.rowList.append(row)
            self.widget.scrollContent.insertRow(row)
            self.loadThumbnailsSignal.emit(row)

    def leftClick(self):
        if self.offset - self.numberthumbnails < 0:
            self.offset = 0
        else:
            self.offset = self.offset - self.numberthumbnails
        self.loadTable()

    def rightClick(self):
        self.offset = self.offset + self.numberthumbnails
        self.loadTable()

    def changeTable(self, i):
        self.chosenTable = self.tableSelectionBox.currentText()
        self.offset = 0
        self.loadTable()

    def changeSite(self, i):
        self.chosenSite = str(self.siteSelectionBox.currentText())
        self.siteChangedSignal.emit(self.chosenSite)
        if self.chosenSite == "errotica":
            self.columns = 7
            self.rows = 5
        if self.chosenSite == "abby":
            self.columns = 7
            self.rows = 5
        elif self.chosenSite == "wowporn" or self.chosenSite == "esnap":
            self.columns = 6
            self.rows = 6
        elif self.chosenSite == "met":
            self.columns = 7
            self.rows = 5

        self.numberthumbnails = self.columns * self.rows
        if hasattr(self,'connection'):
            self.connection.close()
        # self.connection = pymysql.connect(host='192.168.0.8',
        #                              port=3360,
        #                              user='root',
        #                              password='testpass',
        #                              db=self.chosenSite)
        global application_path
        self.connection = sqlite3.connect(application_path+self.chosenSite+'.db')
        sets = self.connection.cursor()
        global conn, thumbshelf
        conn = sqlite3.connect(application_path+'thumbs_'+self.chosenSite+'.db')
        thumbshelf = conn.cursor()
        try:
            # thumbshelf.execute('''drop table IF EXISTS '''+self.chosenSite)
            thumbshelf.execute('''create table thumbs (filename, image BLOB)''')
        except:
            pass
        # self.widget.scrollContentMain.updateMainGuiSignal.connect(self.repaint)
        self.setBarLayout()
        # self.setCentralWidget(self.widget)
        self.model = ""
        self.widget.scrollContent.vbarMoveToPos(0)
        self.backButton.hide()
        # self.widget.scrollContentModel.hide()
        # self.widget.scrollContentMain.show()
        self.loadTable()

    def updateModel(self,model):
        self.originalvbarpos = self.widget.scrollContent.vbar.value()
        self.index = self.tableSelectionBox.currentIndex()
        try:
            self.widgetMain.scrollContent.loadRowSignal.disconnect(self.addNewRow)
            self.widgetModel.scrollContent.loadRowSignal.connect(self.addNewRow)
        except:
            pass
        self.widget.hide()
        self.widget = self.widgetModel
        self.widget.show()
        self.widget.clear()
        self.model = model
        self.offset = 0
        self.backButton.show()
        self.loadTable()

    def backButtonClicked(self):
        self.model = ""
        # self.widget.clear()
        try:
            self.widgetMain.scrollContent.loadRowSignal.connect(self.addNewRow)
            self.widgetModel.scrollContent.loadRowSignal.disconnect(self.addNewRow)
        except:
            pass
        self.widget.hide()
        self.widget = self.widgetMain
        self.widget.show()
        self.widget.clear()
        self.backButton.hide()
        self.tableSelectionBox.currentIndexChanged.disconnect(self.changeTable)
        self.tableSelectionBox.setCurrentIndex(self.index)
        self.tableSelectionBox.currentIndexChanged.connect(self.changeTable)
        self.loadTable()

    def keyPressEvent(self, event):
         key = event.key()

         if key == QtCore.Qt.Key_Escape:
            global conn
            conn.commit()
            self.close()

    def changeRating(self, id, rating):
        pass
        cursor = self.connection.cursor()
        if self.chosenSite == 'wowporn' or self.chosenSite == "esnap":
            sql = "UPDATE `sets` SET  `rating` =  \'"+str(rating)+"\' WHERE  `sets`.`thumb` = \'"+str(id)+"\';"
        else:
            sql = "UPDATE `sets` SET  `rating` =  \'"+str(rating)+"\' WHERE  `sets`.`id` ="+str(id)+";"
        cursor.execute(sql)
        self.connection.commit()

    def getData(self, random=False):
        # Read a single record
        sql = "SELECT * FROM `sets` where `date` > 0 "
        if not self.model == "":
            if len(list(self.model.split("-&-"))) > 1:
                models = list(self.model.split("-&-"))
                for model in models:
                    if model == models[0]:
                        sql = sql + "AND `model` LIKE \"%"+str(model)+"%\" "
                    else:
                        sql = sql + "OR `model` LIKE \"%"+str(model)+"%\" "
            else:
                sql = sql + "AND `model` LIKE \"%"+str(self.model)+"%\" "
        if not self.chosenYear == 'All':
            sql = sql + "AND `date` LIKE \""+str(self.chosenYear)+"%\" "
        if self.videosCheckBox.isChecked():
            sql = sql + "AND `video` = 1 "
        if self.chosenTable == 'best':
            sql = sql + "AND `rating` > 0 "
            if not random:
                sql = sql + "ORDER BY -rating "
            else:
                sql = sql + "ORDER BY RAND() "
        else:
            if not random:
                if self.chosenSite == "abby":
                    sql = sql + "ORDER BY model "
                else:
                    sql = sql + "ORDER BY -date "
            else:
                sql = sql + "ORDER BY RANDOM() "
        sql = sql + ";"
        print sql
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.result = cursor.fetchall()
        print len(self.result)

    def loadThumbnail(self,i):
        if i >= len(self.result):
            pic = self.emptyPic
        else:
            result = self.result[i]
            pic = imageLink(result,self)
            pic.modelClickedSignal.connect(self.updateModel)
            pic.modelRatingChanged.connect(self.changeRating)
        return pic

    def loadThumbnails(self, row):
        if len(self.result) > 0:
            col = 0
            for pos in range(row*self.columns,(row+1)*self.columns):
                self.thumb = self.loadThumbnail(pos)
                self.dataReady.emit(self.thumb,row,col)
                col = col + 1

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = SetBrowser()
    ex.changeSite(0)
    ex.show()
    # ex.backButtonClicked()
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()
