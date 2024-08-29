from PyQt5 import QtWidgets
from inter import Ui_MainWindow
import socket
import sys
import serial
import time
import struct

class mywindow(QtWidgets.QMainWindow):
    data = ''
    
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btnOpros.clicked.connect(self.otpravka)

    def otpravka(self):
        
        if self.ui.chIPterm.isChecked():
            adr = self.ui.entAdrTerIP.value()
            ipadr = self.ui.entIpadr.text()
            ipport = self.ui.entPortIp.text()                 
        else:
            adr = self.ui.sbAdrCom.value()
            portcom = self.ui.sbPortCom.value()
            speedcom = self.ui.cmSpeedCom.currentText()

        commandset = self.ui.entCommand.text()
        commandset = int(commandset, 16)
        
        crcdata= []
        crcdata.append(adr)
        crcdata.append(commandset)
        crcdata.append(0)
        
        crc = 0 
        polinom = 0x69
        for data in crcdata:
            for _ in range(8):
                if crc & (1 << 7):
                    crc *= 2
                    if data & (1 << 7):
                        crc += 1
                    crc ^= polinom
                else:
                    crc *= 2
                    if data & (1 << 7):
                        crc += 1
                data *= 2
        crc=crc%256
        dataOtp = [hex(255), hex(adr), hex(commandset), hex(crc), hex(255), hex(255)]
        dataOtp = '  '.join(dataOtp)
        dataOtp = dataOtp.replace('0x','').upper()
        self.ui.teOtp.setText(dataOtp) 
        self.data = struct.pack('BBBBBB', 255, adr,commandset,crc,255,255)    
        if self.ui.chIPterm.isChecked():
            try:
                conn=socket.socket()
                conn.settimeout(2)
                conn.connect((self.ui.entIpadr.text(),int(self.ui.entPortIp.text())))
            
                conn.send(self.data)
                time.sleep(0.3)
                temp=conn.recv(2048)
                print(temp)
                temp=(temp.hex()).upper()
                temp = [temp[i:i+2] for i in range(0,len(temp),2)]
                temp = ' '.join(temp)
                self.ui.teOtv.setText(temp)
            except:
                self.ui.teOtv.setText('Нет связи')
            
            
        else:
            try:
                ser=serial.Serial(port='COM'+ str(self.ui.sbPortCom.value()), baudrate=int(self.ui.cmSpeedCom.currentText()), bytesize =8,stopbits=1, parity='N' , timeout=0.3, xonxoff=0, rtscts=0  )
                ser.write(self.data)
                line = ser.read(10)
                line = (line.hex()).upper()
                line = [line[i:i+2] for i in range(0,len(line),2)]
                line = ' '.join(line)
                self.ui.teOtv.setText(line)
            except:
                self.ui.teOtv.setText('Ошибка открытия порта')
            
            

        
    
        
        
app = QtWidgets.QApplication([])
app.setStyle('Fusion')
application = mywindow()
application.setWindowTitle('Tester')
application.show()

sys.exit(app.exec())
