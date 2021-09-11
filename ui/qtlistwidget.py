from collections import deque
from math import cos, pi

from PySide2.QtCore import Qt, QSize, QTimer, QPoint, QDateTime
from PySide2.QtGui import QPixmap, QColor, QFont, QCursor, QWheelEvent
from PySide2.QtWidgets import QListWidget, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem, QAbstractSlider, \
    QScroller, QMenu, QApplication, QAbstractItemView

from conf import config
from qss.qss import QssDataMgr
from resources.resources import DataMgr
from src.book.book import BookMgr
from src.qt.com.qt_scroll import SmoothMode
from src.qt.com.qtcomment import QtComment
from src.qt.com.qtimg import QtImgMgr
from src.qt.com.qtmsg import QtMsgLabel
from src.qt.qt_main import QtOwner
from src.qt.util.qttask import QtTaskBase
from src.util.status import Status


class ItemWidget(QWidget):
    def __init__(self, _id, title, leftStr1, leftStr2, leftStr3, leftStr4):
        super(ItemWidget, self).__init__()
        self.id = _id
        self.url = ""
        self.path = ""
        self.IsClicked = False
        # self.setMaximumSize(220, 400)
        # self.setMaximumSize(220, 550)
        layout = QVBoxLayout(self)
        # layout.setContentsMargins(10, 10, 10, 0)
        # 图片label
        self.pictureData = None
        self.picIcon = QLabel(self)
        # self.picIcon.setCursor(Qt.PointingHandCursor)
        # self.picIcon.setScaledContents(True)
        self.picIcon.setMinimumSize(220, 308)
        self.picIcon.setMaximumSize(220, 308)

        self.picIcon.setToolTip(title)
        pic = QPixmap()
        self.picIcon.setPixmap(pic)
        layout.addWidget(self.picIcon)
        if leftStr1:
            self.leftLabel1 = QLabel(leftStr1, self)
            self.leftLabel1.setMinimumHeight(20)
            self.leftLabel1.setMaximumHeight(50)
            self.leftLabel1.setWordWrap(True)
            self.leftLabel1.adjustSize()
            self.leftLabel1.setAlignment(Qt.AlignLeft)
            layout.addWidget(self.leftLabel1)

        if leftStr2:
            layout2 = QHBoxLayout()
            p = QPixmap()
            p.loadFromData(DataMgr.GetData("icon_bookmark_on"))
            self.starPic = QLabel()

            self.starPic.setMinimumSize(20, 20)
            self.starPic.setMaximumSize(20, 20)
            self.starPic.setPixmap(p)
            self.starPic.setCursor(Qt.PointingHandCursor)
            self.starPic.setScaledContents(True)

            self.leftLabel2 = QLabel(leftStr2, self)
            self.leftLabel2.setMinimumHeight(20)
            self.leftLabel2.setMaximumHeight(20)
            self.leftLabel2.setAlignment(Qt.AlignLeft)
            self.leftLabel2.adjustSize()

            layout2.addWidget(self.starPic)
            layout2.addWidget(self.leftLabel2)
            if leftStr3:
                self.leftLabel3 = QLabel(leftStr3, self)
                self.leftLabel3.setMinimumHeight(20)
                self.leftLabel3.setMaximumHeight(20)
                self.leftLabel3.setAlignment(Qt.AlignRight)
                self.leftLabel3.adjustSize()
                layout2.addWidget(self.leftLabel3)

            layout.addLayout(layout2)

        if leftStr4:
            self.leftLabel4 = QLabel(leftStr4, self)
            self.leftLabel4.setMinimumHeight(20)
            self.leftLabel4.setMaximumHeight(20)
            self.leftLabel4.adjustSize()
            self.leftLabel4.setAlignment(Qt.AlignLeft)
            layout.addWidget(self.leftLabel4)
        # self.infoLabel = QLabel(info, self, styleSheet="color: #999999;")
        # self.infoLabel.setMinimumSize(160, 20)
        # self.infoLabel.setMaximumSize(160, 40)
        # self.infoLabel.setAlignment(Qt.AlignRight)
        # layout2.addWidget(self.infoLabel)

        self.label = QLabel(title, self)
        self.label.setMinimumSize(210, 20)
        self.label.setMaximumSize(210, 150)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.adjustSize()
        self.label.setWordWrap(True)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        # self.label.setFont(QFont("Microsoft YaHei",  10,   87))
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        # if self.info:
        #     self.PaintInfo()

    def SetPicture(self, data):
        if not data:
            return
        self.pictureData = data
        pic = QPixmap()
        pic.loadFromData(data)
        # maxW = self.picIcon.width()
        # maxH = self.picIcon.height()
        # picW = pic.width()
        # picH = pic.height()
        # if maxW / picW < maxH / picH:
        #     toW = maxW
        #     toH = (picH/(picW/maxW))
        # else:
        #     toH = maxH
        #     toW = (picW / (picH / maxH))
        newPic = pic.scaled(self.picIcon.width(), self.picIcon.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.picIcon.setPixmap(newPic)


    def GetTitle(self):
        return self.label.text()

    def GetId(self):
        return self.id


class QtBookList(QListWidget, QtTaskBase):
    def __init__(self, parent):
        QListWidget.__init__(self, parent)
        QtTaskBase.__init__(self)
        self.page = 1
        self.pages = 1
        self.verticalScrollBar().actionTriggered.connect(self.OnActionTriggered)
        # self.verticalScrollBar().valueChanged.connect(self.OnMove)
        self.isLoadingPage = False
        self.LoadCallBack = None
        self.parentId = -1
        self.popMenu = None
        QScroller.grabGesture(self, QScroller.LeftMouseButtonGesture)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setStyleSheet(QssDataMgr().GetData('qt_list_scrollbar'))
        self.verticalScrollBar().setSingleStep(30)

        self.fps = 60
        self.duration = 400
        self.stepsTotal = 0
        self.stepRatio = 1.5
        self.acceleration = 1
        self.lastWheelEvent = None
        self.scrollStamps = deque()
        self.stepsLeftQueue = deque()
        self.smoothMoveTimer = QTimer(self)
        self.smoothMode = SmoothMode(SmoothMode.LINEAR)
        self.smoothMoveTimer.timeout.connect(self.__smoothMove)
        self.qEventParam = []
        self.wheelStatus = True

    def wheelEvent(self, e):
        if not self.wheelStatus:
            return
        if self.smoothMode == SmoothMode.NO_SMOOTH:
            super().wheelEvent(e)
            return False

        # 将当前时间点插入队尾
        now = QDateTime.currentDateTime().toMSecsSinceEpoch()
        self.scrollStamps.append(now)
        while now - self.scrollStamps[0] > 500:
            self.scrollStamps.popleft()
        # 根据未处理完的事件调整移动速率增益
        accerationRatio = min(len(self.scrollStamps) / 15, 1)
        self.qEventParam = (e.pos(), e.globalPos(), e.buttons())
        # 计算步数
        self.stepsTotal = self.fps * self.duration / 1000
        # 计算每一个事件对应的移动距离
        delta = e.angleDelta().y() * self.stepRatio
        if self.acceleration > 0:
            delta += delta * self.acceleration * accerationRatio
        # 将移动距离和步数组成列表，插入队列等待处理
        self.stepsLeftQueue.append([delta, self.stepsTotal])
        # 定时器的溢出时间t=1000ms/帧数
        self.smoothMoveTimer.start(1000 // self.fps)
        return False
        # print(e)

    def __smoothMove(self):
        """ 计时器溢出时进行平滑滚动 """
        totalDelta = 0
        # 计算所有未处理完事件的滚动距离，定时器每溢出一次就将步数-1
        for i in self.stepsLeftQueue:
            totalDelta += self.__subDelta(i[0], i[1])
            i[1] -= 1
        # 如果事件已处理完，就将其移出队列
        while self.stepsLeftQueue and self.stepsLeftQueue[0][1] == 0:
            self.stepsLeftQueue.popleft()
        # 构造滚轮事件
        e = QWheelEvent(self.qEventParam[0],
                        self.qEventParam[1],
                        QPoint(),
                        QPoint(0, totalDelta),
                        round(totalDelta),
                        Qt.Vertical,
                        self.qEventParam[2],
                        Qt.NoModifier)
        # print(e)
        # 将构造出来的滚轮事件发送给app处理
        QApplication.sendEvent(self.verticalScrollBar(), e)
        # 如果队列已空，停止滚动
        if not self.stepsLeftQueue:
            self.smoothMoveTimer.stop()

    def __subDelta(self, delta, stepsLeft):
        """ 计算每一步的插值 """
        m = self.stepsTotal / 2
        x = abs(self.stepsTotal - stepsLeft - m)
        # 根据滚动模式计算插值
        res = 0
        if self.smoothMode == SmoothMode.NO_SMOOTH:
            res = 0
        elif self.smoothMode == SmoothMode.CONSTANT:
            res = delta / self.stepsTotal
        elif self.smoothMode == SmoothMode.LINEAR:
            res = 2 * delta / self.stepsTotal * (m - x) / m
        elif self.smoothMode == SmoothMode.QUADRATI:
            res = 3 / 4 / m * (1 - x * x / m / m) * delta
        elif self.smoothMode == SmoothMode.COSINE:
            res = (cos(x * pi / m) + 1) / (2 * m) * delta
        return res

    def InitBook(self, callBack=None):
        self.resize(800, 600)
        self.setMinimumHeight(400)
        self.setFrameShape(self.NoFrame)  # 无边框
        self.setFlow(self.LeftToRight)  # 从左到右
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        self.LoadCallBack = callBack

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.SelectMenuBook)
        self.doubleClicked.connect(self.OpenBookInfo)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def InitFavorite(self, callBack=None):
        self.resize(800, 600)
        self.setMinimumHeight(400)
        self.setFrameShape(self.NoFrame)  # 无边框
        self.setFlow(self.LeftToRight)  # 从左到右
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        self.LoadCallBack = callBack

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.SelectMenuFavorite)
        self.doubleClicked.connect(self.OpenBookInfo)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def InstallCategory(self):
        self.doubleClicked.disconnect(self.OpenBookInfo)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.SelectMenuCategory)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return

    def InstallDel(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.SelectMenuDel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def SelectMenuCategory(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            popMenu = QMenu(self)
            action = popMenu.addAction(self.tr("查看封面"))
            action.triggered.connect(self.OpenPicture)
            popMenu.exec_(QCursor.pos())
        pass

    def SelectMenuDel(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            popMenu = QMenu(self)

            action = popMenu.addAction(self.tr("刪除"))
            action.triggered.connect(self.DelHandler)
            popMenu.exec_(QCursor.pos())
        pass

    def InitUser(self, callBack=None):
        self.setFrameShape(self.NoFrame)  # 无边框
        self.LoadCallBack = callBack
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def SelectMenuBook(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            popMenu = QMenu(self)
            action = popMenu.addAction(self.tr("打开"))
            action.triggered.connect(self.OpenBookInfoHandler)
            action = popMenu.addAction(self.tr("查看封面"))
            action.triggered.connect(self.OpenPicture)
            action = popMenu.addAction(self.tr("重下封面"))
            action.triggered.connect(self.ReDownloadPicture)
            action = popMenu.addAction(self.tr("复制标题"))
            action.triggered.connect(self.CopyHandler)
            action = popMenu.addAction(self.tr("下载"))
            action.triggered.connect(self.DownloadHandler)
            popMenu.exec_(QCursor.pos())
        pass

    def SelectMenuFavorite(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            popMenu = QMenu(self)
            action = popMenu.addAction(self.tr("打开"))
            action.triggered.connect(self.OpenBookInfoHandler)
            action = popMenu.addAction(self.tr("查看封面"))
            action.triggered.connect(self.OpenPicture)
            action = popMenu.addAction(self.tr("重下封面"))
            action.triggered.connect(self.ReDownloadPicture)
            action = popMenu.addAction(self.tr("复制标题"))
            action.triggered.connect(self.CopyHandler)
            action = popMenu.addAction(self.tr("下载"))
            action.triggered.connect(self.DownloadHandler)
            action = popMenu.addAction(self.tr("删除"))
            action.triggered.connect(self.parent().DeleteHandler)
            popMenu.exec_(QCursor.pos())

    def OnActionTriggered(self, action):
        if action != QAbstractSlider.SliderMove or self.isLoadingPage:
            return
        if self.page >= self.pages:
            return
        if self.verticalScrollBar().sliderPosition() == self.verticalScrollBar().maximum():
            self.isLoadingPage = True
            if self.LoadCallBack:
                self.LoadCallBack()

    def UpdatePage(self, page, pages):
        self.page = page
        self.pages = pages

    def UpdateState(self, isLoading=False):
        self.isLoadingPage = isLoading

    def AddBookItem(self, _id, title, categories="", url="", path="", param="", originalName=""):
        index = self.count()
        iwidget = ItemWidget(_id, title, categories, "", "", "")
        iwidget.url = url
        iwidget.path = path
        item = QListWidgetItem(self)
        item.setSizeHint(iwidget.sizeHint())
        self.setItemWidget(item, iwidget)
        iwidget.picIcon.setText("图片加载中...")
        if url and config.IsLoadingPicture:
            self.AddDownloadTask(url, path, None, self.LoadingPictureComplete, True, index, True)
            pass

    def AddUserItem(self, commnetId, commentsCount, likesCount, content, name, createdTime, floor, url="", path="", originalName="", title="", level=1):
        index = self.count()
        iwidget = QtComment(self)
        iwidget.id = commnetId
        iwidget.commentLabel.setText(content)
        iwidget.nameLabel.setText(name)
        # iwidget.numLabel.setText("({})".format(commentsCount))
        # iwidget.starLabel.setText("({})".format(likesCount))
        iwidget.levelLabel.setText(" LV" + str(level) + " ")
        iwidget.titleLabel.setText(" " + title + " ")
        iwidget.dateLabel.setText("{}".format(createdTime))

        iwidget.indexLabel.setText("{}楼".format(str(floor)))

        item = QListWidgetItem(self)
        item.setSizeHint(iwidget.sizeHint())
        self.setItemWidget(item, iwidget)
        if url and config.IsLoadingPicture:
            self.AddDownloadTask(url, path, None, self.LoadingPictureComplete, True, index, True)
            pass

    def LoadingPictureComplete(self, data, status, index):
        if status == Status.Ok:
            item = self.item(index)
            widget = self.itemWidget(item)
            widget.SetPicture(data)
            pass
        else:
            item = self.item(index)
            widget = self.itemWidget(item)
            widget.picIcon.setText("图片加载失败")
        return

    def clear(self) -> None:
        QListWidget.clear(self)

        # 防止异步加载时，信息错乱
        self.ClearTask()

    def DownloadHandler(self):
        selected = self.selectedItems()
        for item in selected:
            widget = self.itemWidget(item)
            bookId = widget.GetId()
            info = BookMgr().GetBook(bookId)
            QtOwner().owner.downloadForm.AddDownload(bookId, info.baseInfo.token, config.CurSite)
            QtMsgLabel().ShowMsgEx(self, self.tr("添加下载成功"))
        pass

    def OpenBookInfoHandler(self):
        selected = self.selectedItems()
        for item in selected:
            widget = self.itemWidget(item)
            QtOwner().owner.bookInfoForm.OpenBook(widget.GetId())
            return

    def CopyHandler(self):
        selected = self.selectedItems()
        if not selected:
            return

        data = ''
        for item in selected:
            widget = self.itemWidget(item)
            data += widget.GetTitle() + str("\r\n")
        clipboard = QApplication.clipboard()
        data = data.strip("\r\n")
        clipboard.setText(data)
        pass

    def DelHandler(self):
        bookIds = set()
        selected = self.selectedItems()
        for item in selected:
            widget = self.itemWidget(item)
            bookIds.add(widget.GetId())
        if not bookIds:
            return
        self.parent().DelCallBack(bookIds)

    def OpenBookInfo(self, modelIndex):
        index = modelIndex.row()
        item = self.item(index)
        if not item:
            return
        widget = self.itemWidget(item)
        if not widget:
            return
        bookId = widget.id
        if not bookId:
            return
        QtOwner().owner.bookInfoForm.OpenBook(bookId)

    def OpenPicture(self):
        selected = self.selectedItems()
        for item in selected:
            widget = self.itemWidget(item)
            QtImgMgr().ShowImg(widget.pictureData)
            return

    def ReDownloadPicture(self):
        selected = self.selectedItems()
        for item in selected:
            widget = self.itemWidget(item)
            index = self.row(item)
            if widget.url and config.IsLoadingPicture:
                widget.picIcon.setPixmap(None)
                widget.picIcon.setText("图片加载中")
                self.AddDownloadTask(widget.url, widget.path, None, self.LoadingPictureComplete, True, index, False)
                pass


class QtCategoryList(QListWidget):
    def __init__(self, parent):
        QListWidget.__init__(self, parent)
        self.setViewMode(self.ListMode)
        self.setFlow(self.LeftToRight)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(self.ScrollPerItem)
        QScroller.grabGesture(self, QScroller.LeftMouseButtonGesture)
        self.setMaximumHeight(30)
        self.setFocusPolicy(Qt.NoFocus)

    def AddItem(self, name):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignCenter)
        # item.setBackground(QColor(87, 195, 194))
        item.setBackground(QColor(0, 0, 0, 0))
        item.setSizeHint(QSize(90, 30))
        item.setFlags(item.flags() & (~Qt.ItemIsSelectable))

        self.addItem(item)

    def ClickItem(self, item):
        if item.background().color() == QColor(0, 0, 0, 0):
            item.setBackground(QColor(87, 195, 194))
            return True
        else:
            item.setBackground(QColor(0, 0, 0, 0))
            return False

    def GetAllSelectItem(self):
        data = set()
        for i in range(self.count()):
            item = self.item(i)
            if item.background().color() == QColor(87, 195, 194):
                data.add(item.text())
        return data
