from strategy.CHOIStrategy import *
from api.Kiwoom import *
from util.notifier import *
import sys

app = QApplication(sys.argv)

# choi_strategy = CHOIStrategy()
# choi_strategy.start()
kiwoom = Kiwoom()
kiwoom.show()
# sendMessage()

app.exec_()