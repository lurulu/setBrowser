import sys, time, os, glob
from PyQt5 import QtGui, QtCore, QtWidgets, QtMultimedia, QtMultimediaWidgets
import pymysql.cursors
import urllib
from random import shuffle
import sqlite3
import vlc
from PIL.ImageQt import ImageQt, Image

# ImageQt.LOAD_TRUNCATED_IMAGES = True
# QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
# print QtGui.QImageReader.supportedImageFormats()

application_path = '.\\'#'\\\\192.168.0.5\\iSCSI\\db\\'

usenetsites = ['wowporn','ftvgirls','esnap','ultrafilms','metartx','joymii','femjoy','mpl','yonitale','swallowsalon','random']

class slideShowClass(QtWidgets.QMainWindow):

    def __init__(self, path, globString, slideDelay=2.0, randomOrder=False):
        super(slideShowClass, self).__init__()
        self.setStyleSheet("QMainWindow {background: 'black';}");
        self.showFullScreen()
        # self.setMinimumSize(300, 300)
        self.globString = globString
        self.randomOrder = randomOrder
        self.slideDelay = slideDelay
        self.path = path
        self.image_paths = self.get_image_paths(self.path)
        self.label = QtWidgets.QLabel()
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter);
        self.setCentralWidget(self.label)
        self.label.setMinimumWidth(self.width())
        self.label.setMinimumHeight(self.height())
        self.show()
        self.imagenumber = -1
        self.reader = QtGui.QImageReader()
        self.reader.setAutoTransform(True)
        self.updateImage()
        self.paused = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateImage)
        self.timer.start(self.slideDelay*1000)

    def updateImage(self):
        self.imagenumber = self.imagenumber + 1
        self.loadImage(self.image_paths[self.imagenumber])

    def get_image_paths(self, input_dir='.'):
        paths = sorted(glob.glob(input_dir+self.globString))
        if self.randomOrder:
            paths = shuffle(paths)
        return paths

    def loadImage(self, image):
        self.image = Image.open(image)
        self.resizePixmap()

    def resizePixmap(self):
        if hasattr(self,'image'):
            w = self.label.width()
            h = self.label.height()
            try:
                self.image.thumbnail((w,h), Image.ANTIALIAS)
            except:
                print self.image_paths[self.imagenumber]
            self.qimage = ImageQt(self.image)
            self.pixmap = QtGui.QPixmap.fromImage(self.qimage)
            self.label.setPixmap(self.pixmap)

    def resizeEvent(self,event):
        self.resizePixmap()
        # return super(noMouseWheel,self).eventFilter(receiver, event)

    def keyPressEvent(self, e):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            incr = 2
        elif modifiers == QtCore.Qt.ControlModifier:
            incr = 5
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            incr = 10
        else:
            incr = 1
        if e.key() == QtCore.Qt.Key_Space:
            if not self.paused:
                self.paused = True
                self.timeLeft = self.timer.remainingTime()
                self.timer.stop()
            else:
                self.paused = False
                time.sleep(self.timeLeft/1000.0)
                self.timer.start()
        if e.key() == QtCore.Qt.Key_Right:
            self.changeImage(incr)
        if e.key() == QtCore.Qt.Key_Left:
            self.changeImage(-1*incr)
        if e.key() == QtCore.Qt.Key_Up:
            self.decreaseSlideDelay()
        if e.key() == QtCore.Qt.Key_Down:
            self.increaseSlideDelay()
        if e.key() == QtCore.Qt.Key_Escape:
            self.exit()

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if  angle< 0:
            self.changeImage(1)
        elif angle > 0:
            self.changeImage(-1)

    def changeImage(self, incr):
        self.timeLeft = 0
        self.timer.stop()
        self.imagenumber = self.imagenumber + incr - 1
        if self.imagenumber < -1:
            self.imagenumber = -1
        self.updateImage()
        if not self.paused:
            self.timer.start()

    def decreaseSlideDelay(self):
        self.slideDelay = self.slideDelay - 0.5
        if self.slideDelay < 0.5:
            self.slideDelay = 0.5
        self.timer.setInterval(self.slideDelay*1000.0)

    def increaseSlideDelay(self):
        self.slideDelay = self.slideDelay + 0.5
        self.timer.setInterval(self.slideDelay*1000.0)

    def exit(self):
        self.close()

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
        if e.key() == QtCore.Qt.Key_M:
            self.player.setMuted(not self.player.isMuted())
        if e.key() == QtCore.Qt.Key_Up:
            vol = self.player.volume()+10
            vol = vol if vol <= 100 else 100
            self.player.setVolume(vol)
        if e.key() == QtCore.Qt.Key_Down:
            vol = self.player.volume()-10
            vol = vol if vol >= 0 else 0
            self.player.setVolume(vol)

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
        self.setMinimumWidth(250)
        self.setMinimumHeight(200)
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        entry = result
        if self.site in usenetsites or self.site == "errotica":
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
        if type(self.pathReplace) is list:
            for i in range(len(self.pathReplace)):
                self.thumb = self.thumb.replace(self.pathReplace[i],self.pathReplaceWith[i])
        else:
            self.thumb = self.thumb.replace(self.pathReplace,self.pathReplaceWith)
        if self.video == 1:
            if type(self.pathReplace) is list:
                for i in range(len(self.pathReplace)):
                    self.directory = self.directory.replace(self.pathReplace[i],self.pathReplaceWith[i])
            else:
                self.directory = self.directory.replace(self.pathReplace,self.pathReplaceWith)
            self.path = self.mainPath+self.directory.replace('/','\\')
            # print 'self.path = ', self.path
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
            self.pixmap.loadFromData(ba)
            t = (self.thumb, buffer(ba))
            thumbshelf.execute("""insert into thumbs values (?,?)""", t)
            conn.commit()
        self.label.setPixmap(self.pixmap)
        self.label.setMinimumSize(self.pixmap.width(), self.pixmap.height())
        self.label.mousePressEvent = self.imageClicked
        try:
            self.models = ' '.join(self.model.split('.')).split(' and ')
        except:
            self.models = ''
        if self.site == "abby":
            dateText = QtWidgets.QLabel("")
        else:
            date = time.strptime(str(self.date),'%Y%m%d')
            dateText = QtWidgets.QLabel(time.strftime("%d/%m/%Y",date))
        self.ratingsBox = QtWidgets.QComboBox()
        for rating in range(6):
            self.ratingsBox.addItem(str(rating))
        self.ratingsBox.setCurrentIndex(int(self.rating))
        self.ratingsBox.currentIndexChanged.connect(self.updateRating)
        self.ratingsBox.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.myFilter	 = noMouseWheel()
        self.ratingsBox.installEventFilter(self.myFilter)
        layout.addWidget(self.label)
        # if hasattr(self,'setname'):
        #     setnameLabel = dateText = QtWidgets.QLabel(self.setname)
        #     layout.addWidget(setnameLabel)
        modelRateLayout = QtWidgets.QHBoxLayout()
        modelNameWidget = QtWidgets.QComboBox()
        modelNameWidget.installEventFilter(self.myFilter)
        modelNameWidget.addItem('')
        modelNameWidget.currentIndexChanged.connect(self.modelClicked)
        modelNameLayout = QtWidgets.QVBoxLayout()
        for m in self.models:
            modelNameWidget.addItem(m)
        modelNameWidget.setLayout(modelNameLayout)
        modelRateLayout.addWidget(modelNameWidget)
        modelRateLayout.addWidget(dateText)
        modelRateLayout.addWidget(self.ratingsBox)
        modelRateWidget = QtWidgets.QWidget()
        # modelRateWidget.setMaximumHeight(100)
        modelRateWidget.setLayout(modelRateLayout)
        layout.addWidget(modelRateWidget)
        self.setLayout(layout)
        self.parent.siteChangedSignal.connect(self.siteChanged)

    def startMovie(self, event):
        if self.video == 1:
            if os.path.isfile(self.path+'.gif'):
                if not hasattr(self,'movie'):
                    self.movie = QtGui.QMovie(self.path+'.gif')
                self.label.enterEvent = self.startMovie
                self.label.leaveEvent = self.stopMovie
                self.label.setMovie(self.movie)
                self.movie.setPaused(False)
            else:
                print self.path+'.gif'

    def stopMovie(self, event):
        if self.video == 1 and hasattr(self,'movie'):
            self.frameNumber = self.movie.currentFrameNumber()
            self.movie.setPaused(True)
            if not self.site in usenetsites or self.movie.currentFrameNumber() < 5:
                self.label.setPixmap(self.pixmap)
            # del self.movie

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
                self.videowidget = videoWidget(self.path)
            else:
                self.runSlideShow()

    def runSlideShow(self):
        self.parent.runSlideShow(self.path, self.globString)

    def modelClicked(self):
        model = self.sender().currentText()
        if not model == '':
            if self.site in usenetsites:
                model = '.'.join(model.split(' '))
            self.modelClickedSignal.emit(model)
        self.sender().setCurrentIndex(0)

    def siteChanged(self, site):
        self.site = site
        if self.site == "errotica":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\errotica\\'
            self.pathReplace = 'errofiles2/'
            self.pathReplaceWith = ''
            if 'files/' in self.directory:
                self.globString = '\\*_l.jpg'
            else:
                self.globString = '\\*.jpg'
        elif self.site == "yonitale":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\yonitale\\'
            self.pathReplace = 'yonitale/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "swallowsalon":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\swallowsalon\\'
            self.pathReplace = 'swallowsalon/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "metartx":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\metartx\\'
            self.pathReplace = 'metartx/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "ultrafilms":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\ultrafilms\\'
            self.pathReplace = 'ultrafilms/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "joymii":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\joymii\\'
            self.pathReplace = 'joymii/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "ftvgirls":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\FTV\\'
            self.pathReplace = 'ftvgirls/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "wowporn":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\wowporn\\'
            self.pathReplace = 'wowporn/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "random":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\random\\'
            self.pathReplace = 'random/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "esnap":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\esnap\\'
            self.pathReplace = 'esnap/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "abby":
            self.mainPath = '\\\\192.168.0.5\\met-art\\nl-g2.abbywinters.com\\'
            self.pathReplace = 'abby/'
            self.pathReplaceWith = ''
            self.globString = '\\*.jpg'
        elif self.site == "femjoy":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\femjoy\\'
            self.pathReplace = 'femjoy/'
            self.pathReplaceWith = ''
            self.globString = '\\femjoy*.jpg'
        elif self.site == "mpl":
            self.mainPath = '\\\\192.168.0.5\\iSCSI\\MPL\\'
            self.pathReplace = 'mpl/'
            self.pathReplaceWith = ''
            self.globString = '\\[0-9][0-9][0-9][0-9][0-9]*.jpg'
        elif self.site == "met":
            self.mainPath = '\\\\192.168.0.5\\met-art\\members.met-art.com\\members\\'
            self.pathReplace = ['met/','\\t_']
            self.pathReplaceWith = ['','\\']
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
    dataReady = QtCore.pyqtSignal('QWidget', int, int)

    def __init__(self, parent = None):
        super(SetBrowser, self).__init__(parent)
        self.setWindowTitle("SetBrowser")
        self.showFullScreen()
        self.show()

        self.tab = QtWidgets.QFrame()
        self.layout = QtWidgets.QGridLayout()

        self.sites = ['errotica', 'met', 'abby'] + usenetsites#, 'wowporn','esnap','metartx','yonitale','swallowsalon','random']
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
        self.modelWidgetActive = False
        self.centralLayout.addWidget(self.widgetMain)
        self.centralLayout.addWidget(self.widgetModel)
        self.widgetMain.scrollContent.loadRowSignal.connect(self.addNewRow)
        self.setCentralWidget(self.centralWidget)
        self.loadThumbnailsSignal.connect(self.loadThumbnails)
        self.dataReady.connect(self.addThumbnail)

    def addNewRow(self, row):
        self.row = self.widget.scrollContent.rowAt(self.widget.scrollContent.height())
        self.loadTable(self.row+self.rows)

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
        # self.slideshow.exit()

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
        else:
            for r in range(row):
                if not r in self.widget.scrollContent.rowList and r*self.columns < len(self.result):
                    self.widget.scrollContent.rowList.append(r)
                    self.widget.scrollContent.insertRow(r)
                    self.loadThumbnailsSignal.emit(r)

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
        elif self.chosenSite in usenetsites:
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
        if not self.modelWidgetActive:
            self.modelWidgetActive = True
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
        self.widget.clear()
        self.modelWidgetActive = False
        try:
            self.widgetMain.scrollContent.loadRowSignal.connect(self.addNewRow)
            self.widgetModel.scrollContent.loadRowSignal.disconnect(self.addNewRow)
        except:
            pass
        self.widget.hide()
        self.widget = self.widgetMain
        self.widget.show()
        self.backButton.hide()
        self.tableSelectionBox.currentIndexChanged.disconnect(self.changeTable)
        self.tableSelectionBox.setCurrentIndex(self.index)
        self.tableSelectionBox.currentIndexChanged.connect(self.changeTable)
        self.getData()

    def keyPressEvent(self, event):
         key = event.key()

         if key == QtCore.Qt.Key_Escape:
            global conn
            conn.commit()
            self.close()

    def changeRating(self, id, rating):
        pass
        cursor = self.connection.cursor()
        # if self.chosenSite in usenetsites:
        sql = "UPDATE `sets` SET  `rating` =  \'"+str(rating)+"\' WHERE  `sets`.`thumb` = \'"+str(id)+"\';"
        # else:
        #     sql = "UPDATE `sets` SET  `rating` =  \'"+str(rating)+"\' WHERE  `sets`.`id` ="+str(id)+";"
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
                try:
                    self.dataReady.emit(self.thumb,row,col)
                except:
                    pass
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
