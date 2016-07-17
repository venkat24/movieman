from PyQt4.QtGui import * 
from PyQt4.QtCore import * 
import sys

class MyListView(QListView): 

  @pyqtSlot("QModelIndex")
  def ItemClicked(self,index):
    QMessageBox.information(None,"Hello!","You Clicked: \n"+index.data().toString())    
   
   
def main():  
    app 	= QApplication(sys.argv)
    listView 	= MyListView(None)
    model 	= QStringListModel()        
    
    model.setStringList(QString("Item 1;Item 2;Item 3;Item 4").split(";"))    
    listView.setModel(model)
    listView.setWindowTitle("QListView Detect Click")
    listView.show()  
    
    QObject.connect(listView,SIGNAL("clicked(QModelIndex)"),
		    listView,SLOT("ItemClicked(QModelIndex)"))    
    return app.exec_()
if __name__ == '__main__':
  main()