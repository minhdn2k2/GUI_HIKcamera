from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ultis.API_CAM.Camera_SDK.CamOperation_class import CameraOperation 
from ultis.API_CAM.Camera_SDK.CamOperation_class import TxtWrapBy, ToHexStr
from ultis.API_CAM.MvCameraControl_class import *
from ultis.API_CAM.MvErrorDefine_const import *
from ultis.API_CAM.CameraParams_header import *
import cv2, imutils, threading
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QTimer
import numpy as np
import os
from time import time
from tqdm import tqdm
from ultis.API_XUOC_CANH.display_error_detection import *

global deviceList
deviceList = MV_CC_DEVICE_INFO_LIST()
global cam
cam = MvCamera()
global nSelCamIndex
nSelCamIndex = 0
global obj_cam_operation
obj_cam_operation = 0
global isOpen
isOpen = False
global isGrabbing
isGrabbing = False
global isCalibMode  # CalibMode check
isCalibMode = True
display_error_detection_model = DisplayErrorModel() 


class Ui_MainWindow():#object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)                      
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 1320, 951))      
        self.groupBox.setObjectName("groupBox")
        self.displayLabel = QtWidgets.QLabel(self.groupBox)
        self.displayLabel.setGeometry(QtCore.QRect(10, 20, 1300, 911))
        self.displayLabel.setText("")
        self.displayLabel.setObjectName("displayLabel")
        self.displayImg = QtWidgets.QLabel(self.groupBox)
        self.displayImg.setGeometry(QtCore.QRect(10, 20, 1300, 911))
        self.displayImg.setText("")
        self.displayImg.setObjectName("displayImg")
        self.scroll_area = QScrollArea(self.groupBox)
        self.scroll_area.setGeometry(QtCore.QRect(10, 20, 1300, 911))
        self.scroll_area.setWidget(self.displayImg)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)
        self.scroll_area.setMouseTracking(True)
        self.zoom_factor = 1.0
        self.image = None
        self.bnStart = QtWidgets.QPushButton(self.centralwidget)
        self.bnStart.setGeometry(QtCore.QRect(1350, 20, 271, 85))
        self.bnStart.setObjectName("bnStart")
        self.bnStop = QtWidgets.QPushButton(self.centralwidget)
        self.bnStop.setGeometry(QtCore.QRect(1350, 120, 271, 85))
        self.bnStop.setObjectName("bnStop")
        self.bnSave = QtWidgets.QPushButton(self.centralwidget)
        self.bnSave.setGeometry(QtCore.QRect(1350, 220, 271, 85))
        self.bnSave.setObjectName("bnSave")
        self.spin_box = QSpinBox(self.centralwidget)
        self.spin_box.setGeometry(QtCore.QRect(1520, 450, 75, 45))
        self.spin_box.setStyleSheet('font: 18pt Arial;')
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(150)
        self.spin_box.setValue(25)
        self.area = 25
        self.text_area = QtWidgets.QLabel(self.centralwidget)
        self.text_area.setGeometry(QtCore.QRect(1390, 450, 185, 45))
        self.text_area.setText("Set Area:")
        self.text_area.setFont(QFont('Arial', 18))
        self.comboModels = QComboBox(self.centralwidget)
        self.comboModels.addItem("")
        self.comboModels.addItem("")
        self.comboModels.addItem("")
        self.comboModels.addItem("")
        self.comboModels.addItem("")
        self.comboModels.setGeometry(QtCore.QRect(1640, 20, 250, 61))
        self.predict = QtWidgets.QPushButton(self.centralwidget)
        self.predict.setGeometry(QtCore.QRect(1640, 96, 250, 90))
        self.predict.setObjectName("predict")
        self.list_widget = QListWidget(self.centralwidget)
        self.list_widget.setGeometry(QtCore.QRect(1640, 200, 250, 330))
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(1350, 550, 540, 412))
        self.groupBox_4.setObjectName("Combo_model")
        self.text1 = QtWidgets.QLabel(self.groupBox_4)
        self.text1.setGeometry(QtCore.QRect(75, 0, 540, 412))
        self.text1.setObjectName("text1")
        self.text2 = QtWidgets.QLabel(self.groupBox_4)
        self.text2.setGeometry(QtCore.QRect(205, 0, 540, 412))
        self.text2.setObjectName("text2")
        self.back_cam = QtWidgets.QPushButton(self.centralwidget)
        self.back_cam.setGeometry(QtCore.QRect(1350, 320, 271, 85))
        self.back_cam.setObjectName("back_cam")        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1339, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.run = False
        self.runcam = True
        self.Timer = QTimer()
        self.mode = None

###        Connections Connections Connections Connections Connections       ###
        
        self.retranslateUi(MainWindow)
        self.bnStart.clicked.connect(self.enum_devices)
        self.bnStop.clicked.connect(self.stop_grabbing)
        self.bnSave.clicked.connect(self.saveImage)
        self.comboModels.currentIndexChanged.connect(self.select_model)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.predict.clicked.connect(self.Predict)
        self.list_widget.itemClicked.connect(self.item_click)
        self.back_cam.clicked.connect(self.Back_cam)
        self.Timer.timeout.connect(self.trigger_once)
        self.spin_box.valueChanged.connect(self.on_value_changed)

    def saveImage(self):
        if self.runcam:
            try:
                self.filename = QFileDialog.getSaveFileName(filter="PNG(*.png)")[0]
                cv2.imwrite(self.filename, self.img)
                print('Image saved as:', self.filename)
            except:
                pass
        if not self.runcam:
            if self.final_img:
                try:
                    self.filename = QFileDialog.getSaveFileName(filter="PNG(*.png)")[0]
                    cv2.imwrite(self.filename, self.final_img)
                except:
                    pass

    def select_model(self, i):
        if i == 1:
            self.mode = 'xuoc_man_hinh'
            ret = obj_cam_operation.Set_parameter(35.60, 18000.00, 20.00)
            if ret != MV_OK:
                strError = "Set param failed ret:" + ToHexStr(ret)
                QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)
        if i == 2:
            self.mode = 'xuoc_canh'
        if i == 3:
            self.mode = 'bong_da'
        if i == 4:
            self.mode = 'toet_oc'
    def display_result(self, i):
        if i > 0:
            self.text1.setText(f'Phát hiện được {i} lỗi')
            self.text1.setFont(QFont('Arial', 30))
        else:
            self.text2.setText('Pass!')
            self.text2.setFont(QFont('Arial', 40))
    def Predict(self):
        name = time()
        if self.mode == 'xuoc_man_hinh':
            self.final_img, num = display_error_detection_model.detect_error_end2end(self.img.copy(), self.area)
            self.Stopcam()
            img_show = imutils.resize(self.final_img.copy(), width=2448)
            self.displayLabel.clear()
            self.scroll_area.setVisible(True)
            self.image = QtGui.QPixmap.fromImage(QImage(img_show, img_show.shape[1], img_show.shape[0], img_show.strides[0], QImage.Format_BGR888))
            self.display_image()
            self.display_result(num)
            for i in range(num):
                name_item = f'Error {i}'
                item = QListWidgetItem(name_item)
                item.setFont(QFont('Arial', 14))
                self.list_widget.addItem(item)
            self.runcam = False
        if self.mode == 'xuoc_canh':
            print('None')
        if self.mode == 'bong_da':
            print('None')
        if self.mode == 'toet_oc':
            print('None')
        end = time()
        print(end-name)

    def display_image(self):
        if self.image is not None:
            # Scale the image based on the zoom factor
            scaled_image = self.image.scaled(
                int(self.image.width() * self.zoom_factor),
                int(self.image.height() * self.zoom_factor),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.displayImg.setPixmap(scaled_image)
            self.displayImg.adjustSize()

    def zoom_in(self):
        self.zoom_factor *= 1.2  # Increase the zoom factor by 20%
        self.display_image()

    def zoom_out(self):
        self.zoom_factor *= 0.8  # Decrease the zoom factor by 20%
        self.display_image()

    def wheelEvent(self, event: QtGui.QWheelEvent):
        # Zoom in or out based on the wheel event
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def item_click(self, item):        #------------------Coming Soon------------------#
        clicked_text = item.text()
        i = int(clicked_text[6:])

    def on_value_changed(self, value):
        self.area = value
        

    #-------------------------------API CAM---------------------------------------------------#
    def enum_devices(self):      
        global deviceList
        global obj_cam_operation

        deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)
            return ret

        if deviceList.nDeviceNum == 0:
            QMessageBox.warning(QMainWindow(), "Info", "Find no device", QMessageBox.Ok)
            return ret
        print("Find %d devices!" % deviceList.nDeviceNum)
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName:
                    if 0 == per:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print("device user define name: %s" % chUserDefinedName)

                chModelName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                    if 0 == per:
                        break
                    chModelName = chModelName + chr(per)

                print("device model name: %s" % chModelName)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName:
                    if per == 0:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print("device user define name: %s" % chUserDefinedName)

                chModelName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                    if 0 == per:
                        break
                    chModelName = chModelName + chr(per)
                print("device model name: %s" % chModelName)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: %s" % strSerialNumber)
               
        self.open_device()
        self.start_grabbing()
        self.runcam = True
        button = self.sender()  # Get the button that triggered the signal
        button.setEnabled(False)  # Disable the button
       
        
    def open_device(self):
        global deviceList
        global nSelCamIndex
        global obj_cam_operation
        global isOpen
        if isOpen:
            QMessageBox.warning(QMainWindow(), "Error", 'Camera is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER
        obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)
        ret = obj_cam_operation.Open_device()
        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)
            isOpen = False
        else:
            self.set_software_trigger_mode()
    def start_grabbing(self):
        global obj_cam_operation
        global isGrabbing
        global cam
        isGrabbing = True
        self.Timer.start(int(500))
        grab_thread = threading.Thread(target=self.thread)
        grab_thread.start()
    def thread(self):
        global obj_cam_operation
        while True:
            self.img = obj_cam_operation.get_np_image()
            try:
                if self.run:
                    if self.editScoreThreshold.toPlainText() == "":
                        score_threshold = 0.5  # Default threshold Value = 0.5
                    else:
                        score_threshold = float(self.editScoreThreshold.toPlainText())
                    self.img = self.detect(self.img, score_threshold)
                self.set_image(self.img)
                if isGrabbing == False:
                    break
            except:
                continue
    def stop_grabbing(self):
        global obj_cam_operation
        global isGrabbing
        self.text1.clear()
        self.text2.clear()
        self.list_widget.clear()
        ret = obj_cam_operation.Stop_grabbing()
        print(ToHexStr(ret))
        isGrabbing = False
        self.thread()
        self.Timer.stop()
        print('Camera stopped')
    def set_continue_mode(self):
        global is_trigger_mode
        strError = None
        ret = obj_cam_operation.Set_trigger_mode(False)
        if ret != 0:
            strError = "Set continue mode failed ret:" + ToHexStr(ret) + " mode is " + str(is_trigger_mode)
            QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)
    def set_software_trigger_mode(self):
        global isOpen
        global isGrabbing
        global obj_cam_operation
        ret = obj_cam_operation.Set_trigger_mode(True)
        if ret != 0:
            strError = "Set trigger mode failed ret:" + ToHexStr(ret)
            QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)
    def trigger_once(self):
        ret = obj_cam_operation.Trigger_once()
        if ret != 0:
            print('TriggerSoffware failed ret:' + ToHexStr(ret))
    #_______________________________________________________________________________________________________________________#

    def get_param(self):
        ret = obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)
        else:
            self.edtExposureTime.setText("{0:.2f}".format(obj_cam_operation.exposure_time))
            self.edtGain.setText("{0:.2f}".format(obj_cam_operation.gain))
            self.edtFrameRate.setText("{0:.2f}".format(obj_cam_operation.frame_rate))

        # en:set param


    def set_param(self):
        frame_rate = self.edtFrameRate.toPlainText()
        exposure = self.edtExposureTime.toPlainText()
        gain = self.edtGain.toPlainText()
        print(frame_rate)
        print(exposure)
        print(gain)
        ret = obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
        if ret != MV_OK:
            strError = "Set param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(QMainWindow(), "Error", strError, QMessageBox.Ok)

        return MV_OK
    def enable_controls(self):
        global isGrabbing
        global isOpen
        self.btnOpen.setEnabled(not isOpen)
        self.btnClose.setEnabled(isOpen)
        self.bnStart.setEnabled(isOpen and (not isGrabbing))
        self.bnStop.setEnabled(isOpen and isGrabbing)
    def set_image(self, image):
        """ This function will take image input and resize it
            only for display purpose and convert it to QImage
            to set at the label.
        """
        self.tmp = image
        try:
            image = imutils.resize(image, width=1300)
        except:
            print('no image')
            return
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.displayLabel.setPixmap(QtGui.QPixmap.fromImage(image))
    def StopCam(self):
        global obj_cam_operation
        global isGrabbing
        ret = obj_cam_operation.Stop_grabbing()
        print(ToHexStr(ret))
        isGrabbing = False
        self.thread()
        self.Timer.stop()
        print('Camera stopped')
    def Back_cam(self):
        global obj_cam_operation
        global isGrabbing
        global cam
        self.displayImg.clear()
        self.text1.clear()
        self.text2.clear()
        self.list_widget.clear()
        self.scroll_area.setVisible(False)
        self.image = None
        isGrabbing = True
        self.Timer.start(int(500))
        grab_thread = threading.Thread(target=self.thread)
        grab_thread.start()
        self.runcam = True
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "DISPLAY"))
        self.bnStart.setText(_translate("MainWindow", "Start"))
        self.bnStart.setFont(QFont('Arial', 36))
        self.bnStop.setText(_translate("MainWindow", "Stop"))
        self.bnStop.setFont(QFont('Arial', 36))
        self.bnSave.setText(_translate("MainWindow", "Save"))
        self.bnSave.setFont(QFont('Arial', 36))
        self.predict.setText(_translate("MainWindow", "Predict"))
        self.predict.setFont(QFont('Arial', 36))
        self.comboModels.setItemText(0, _translate("MainWindow", "-- None --"))
        self.comboModels.setItemText(1, _translate("MainWindow", "Xước màn hình"))
        self.comboModels.setItemText(2, _translate("MainWindow", "Xước cạnh"))
        self.comboModels.setItemText(3, _translate("MainWindow", "Bong da"))
        self.comboModels.setItemText(4, _translate("MainWindow", "Toét ốc"))
        self.comboModels.setFont(QFont('Arial', 26))
        self.back_cam.setText(_translate("MainWindow", "Back Cam"))        
        self.back_cam.setFont(QFont('Arial', 34))
        self.groupBox_4.setTitle(_translate("MainWindow", "Result"))
        self.groupBox_4.setFont(QFont('Arial', 24))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    def wheelEvent(event: QtGui.QWheelEvent):
        ui.wheelEvent(event)

    MainWindow.wheelEvent = wheelEvent
    MainWindow.show()
    sys.exit(app.exec_())
    

    








