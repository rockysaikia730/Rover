import sys,os,json
from PyQt5.QtGui import QIcon, QFont, QPalette, QImage, QPixmap
from PyQt5.QtCore import (Qt, QThread, QDir, QFile, QFileInfo, QPropertyAnimation, QRect,
                          QAbstractAnimation, QTranslator, QLocale, QLibraryInfo,pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QMessageBox,
                             QFrame, QLabel, QFileDialog,QHBoxLayout)
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy, QFileDialog, QLineEdit
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import cv2, ctypes





categories = [{
            "supercategory": "vehicle",
            "id": 1,
            "name": "rover",
            "keypoints": [
                        #Write names of the keypoint within "" and not ''
                        "Front wheel-L",
                        "Front wheel-R",
                        "Front-Chasis-R",
                        "Front-Chasis-L",
                        "Rear Chasis-L",
                        "Rear Chasis-R",
                        "Rear Wheel-R",
                        "Rear Wheel-L",
                        "Cam"
                        ]
            }]

images = []
annotations = []



class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.dicAnnot_ID = -1

        self.reset()
        self.dicAnnot = None
        self.imgAnnot = None

        p =self.palette()
        p.setColor(QPalette.Window, Qt.white)
        self.setPalette(p)
        
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)

        # disable (but not hide) close button
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)  

        self.initUI()
        self.show()

    def initUI(self):

        self.framePrincipal = QLabel()

        self.openBtn = QPushButton('Open Image')
        self.openBtn.clicked.connect(self.open_file)

        self.prev = QPushButton('Previous Image')
        self.prev.clicked.connect(self.previous_img)

        self.next = QPushButton('Next Image')
        self.next.clicked.connect(self.next_img)

        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0,0,0,0)
        hboxLayout.addWidget(self.prev)
        hboxLayout.addWidget(self.openBtn)
        hboxLayout.addWidget(self.next)


        self.BoundingBox = QPushButton('Bounding Box')
        self.BoundingBox.clicked.connect(self.bbox)
        
        self.Keypoints = QPushButton('Keypoints')
        self.Keypoints.clicked.connect(self.kpts)

        self.Segmentation = QPushButton('Segmentation')
        self.Segmentation.clicked.connect(self.seg)

        hboxLayout2 = QHBoxLayout()
        hboxLayout2.setContentsMargins(0,0,0,0)
        hboxLayout2.addWidget(self.BoundingBox)
        hboxLayout2.addWidget(self.Keypoints)
        hboxLayout2.addWidget(self.Segmentation)
        
        self.label = QLabel()
        self.label.setStyleSheet("background-color: white; border: 1px solid black;")

        self.display = QLabel()
        self.display.setStyleSheet("background-color: white; border: 1px solid black;")

        self.showan = QPushButton('Show')
        self.showan.clicked.connect(self.showAnnot)

        self.dele = QPushButton('Delete')
        self.dele.clicked.connect(self.delete)

        hboxLayout3 = QHBoxLayout()
        hboxLayout3.setContentsMargins(0,0,0,0)
        hboxLayout3.addWidget(self.label)
        hboxLayout3.addWidget(self.display)
        hboxLayout3.addWidget(self.showan)
        hboxLayout3.addWidget(self.dele)

        self.exitApp = QPushButton('Exit')
        self.exitApp.clicked.connect(self.exit)
        
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.framePrincipal)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addLayout(hboxLayout2)
        vboxLayout.addLayout(hboxLayout3)
        vboxLayout.addWidget(self.exitApp)
        self.setLayout(vboxLayout)

    def showAnnot(self):
        try:
            coord = self.dicAnnot["bbox"]
            painter = QtGui.QPainter(self.framePrincipal.pixmap())
            painter.drawRect(coord[0], coord[1], coord[2]-coord[0], coord[3]-coord[1])
            painter.end()
            self.framePrincipal.update()
        except:
            print('No Annotations')

    def delete(self):
        self.dicAnnot["bbox"] = []
        self.dicAnnot["segmentation"] = [[]]
        self.dicAnnot["num_keypoints"] = 0
        self.dicAnnot["area"] = 0
        self.dicAnnot["keypoints"] = []
        self.label.setText('[]')
        try:
            self.display.setText( str(categories[0]["keypoints"][self.dicAnnot["num_keypoints"]]) )
        except:
            pass
        self.pixmap = QPixmap(self.fname[0])
        self.framePrincipal.setPixmap(self.pixmap)

    def initializeList(self):
        key_file = self.extract_name()
        for i in images:
            if(i["id"] == key_file.split('.')[0]):
                #Implies that file has already been annoted
                self.imgAnnot = i
                self.dicAnnot = ctypes.cast(i["address"], ctypes.py_object).value
                break   
        else:
            self.dicAnnot_ID +=1

            self.dicAnnot = {"segmentation": [[]],
                        "num_keypoints": 0,
                        "area":0,
                        "iscrowd": 0,
                        "keypoints": [],
                        "image_id": self.Image_id.split('.')[0],
                        "bbox": [],
                        "category_id": categories[0]["id"],
                        "id": self.dicAnnot_ID}
            
            annotations.append(self.dicAnnot)

            self.imgAnnot = {"id": self.Image_id.split('.')[0],
                        "width": self.width,
                        "height": self.height,
                        "file_name": self.Image_id,
                        "address": id(annotations[-1])
                        }
            images.append(self.imgAnnot)

        print(annotations)
        self.label.setText(str(self.dicAnnot["bbox"]))
        try:
            self.display.setText( str(categories[0]["keypoints"][self.dicAnnot["num_keypoints"]]) )
        except:
            pass

    def extract_name(self):
        split_reverse = self.fname[0][::-1].split('/')
        self.Image_id = split_reverse[0][::-1]
        return self.Image_id

    def open_file(self):
        self.fname = QFileDialog.getOpenFileName(self, "Open image",os.getcwd())
        self.pixmap = QPixmap(self.fname[0])
        self.framePrincipal.setPixmap(self.pixmap)
        img = cv2.imread(self.fname[0])
        self.height, self.width, _ = img.shape
        self.initializeList()
        

    def previous_img(self):
        self.reset()
        try:
            mod = self.fname[0][::-1].split('/')
            mod1 = mod[0][::-1].split('.') 
            new_path = self.fname[0][:self.fname[0].find('.'.join(mod1))] + str(int(mod1[0])-1) + '.' + mod1[-1]
            if(os.path.exists(new_path)):
                self.fname = (new_path, self.fname[1])
                self.pixmap = QPixmap(self.fname[0])
                self.framePrincipal.setPixmap(self.pixmap)
                self.initializeList()
            else:
                print('No more images')
        except:
            print("No more images")
        

    def next_img(self):
        self.reset()
        try:
            mod = self.fname[0][::-1].split('/')
            mod1 = mod[0][::-1].split('.')
            new_path = self.fname[0][:self.fname[0].find('.'.join(mod1))] + str(int(mod1[0])+1) + '.' + mod1[-1]
            if(os.path.exists(new_path)):
                self.fname = (new_path, self.fname[1])
                self.pixmap = QPixmap(self.fname[0])
                self.framePrincipal.setPixmap(self.pixmap)
                self.initializeList()
            else:
                print('No more images')
        except:
            print("No more images")
        
        
    def reset(self):
        self.bboxVal = False
        self.segVal = False
        self.kptsVal = False

    def bbox(self):
        self.bboxVal = True
        self.kptsVal = False
        self.segVal = False
        
    def kpts(self):
        self.bboxVal = False
        self.kptsVal = True
        self.segVal = False

    def seg(self):
        self.bboxVal = False
        self.kptsVal = False
        self.segVal = True

    def area(self,p):
        z = []
        for i in range(0,len(p)-1,2):
            z.extend([(p[i],p[i+1])])
        return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in self.segments(z)))

    def segments(self,p):
        return zip(p, p[1:] + [p[0]])
    
    def mousePressEvent(self, event):

        self.lastPoint = self.framePrincipal.mapFromParent(event.pos() )
        self.X = self.lastPoint.x()-5
        self.Y = self.lastPoint.y()-5
        if((self.X,self.Y) <=  (self.framePrincipal.width(),self.framePrincipal.height())):
            if(self.bboxVal and len(self.dicAnnot["bbox"]) < 4):
                #Display bbox
                painter = QtGui.QPainter(self.framePrincipal.pixmap())
                painter.drawEllipse(self.X,self.Y, 10, 10)
                painter.end()
                self.dicAnnot["bbox"].extend([self.X,self.Y])
                if(len(self.dicAnnot["bbox"]) == 4):
                    coord = self.dicAnnot["bbox"]
                    painter = QtGui.QPainter(self.framePrincipal.pixmap())
                    painter.drawRect(coord[0], coord[1], coord[2]-coord[0], coord[3]-coord[1])
                    painter.end()
                self.label.setText(str(self.dicAnnot["bbox"]))
                

            elif(self.kptsVal):
                painter = QtGui.QPainter(self.framePrincipal.pixmap())
                painter.drawEllipse(self.X,self.Y, 10, 10)
                painter.end()

                self.dicAnnot["num_keypoints"] += 1
                self.dicAnnot["keypoints"].extend([self.X,self.Y,2])
                try:
                    self.display.setText( str(categories[0]["keypoints"][self.dicAnnot["num_keypoints"]]) )
                except:
                    pass
                #To see the number/name of the keypoint

            elif(self.segVal):
                
                painter = QtGui.QPainter(self.framePrincipal.pixmap())
                painter.drawEllipse(self.X,self.Y, 10, 10)
                
                last_segment = self.dicAnnot["segmentation"][-1]

                try:
                    painter.drawLine(last_segment[-2]+5, last_segment[-1]+5, self.X+5, self.Y+5)    
                except:
                    pass

                last_segment.extend([self.X,self.Y])
                
                if(abs(self.X-last_segment[0]) < 30 and abs(self.Y-last_segment[1]) < 30 and len(last_segment)>=4):
                        self.dicAnnot["area"] = self.area(last_segment)
                        painter.drawLine(last_segment[0]+5, last_segment[1]+5, self.X+5, self.Y+5) 
                        self.reset()
                painter.end()
                
                
            #print(self.dicAnnot)
            self.framePrincipal.update()
        
    def exit(self):
        json_dict = {
                "info": {},
                "licenses": {},
                "images":images,
                "annotations": annotations,
                "categories" :categories
            }
        json_object = json.dumps(json_dict, indent = 4) 
        with open("coco.json", "w") as outfile:
            outfile.write(json_object)
        self.close()
        




app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())


