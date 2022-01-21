from api.Kiwoom import *
from PyQt5.QtWidgets import QApplication
from strategy.CHOIStrategy import *
import sys

app = QApplication(sys.argv)

choi_strategy = CHOIStrategy()
choi_strategy.start()
#kiwoom = Kiwoom()
#kiwoom.show()

app.exec_()