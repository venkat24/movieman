from layout import Ui_Form,_translate
from PyQt4 import QtCore,QtGui
import sys
import os
import PTN as ptn
import json
import tmdb3
import requests
import urllib

config = 'http://api.themoviedb.org/3/configuration?api_key={key}'
api_key = '012b3191a9febcd3a532cfa5505daeca'
url = config.format(key=api_key)
r = requests.get(url)
config = r.json()
base_url = config['images']['base_url']
sizes = config['images']['poster_sizes']
max_size='w500'
movieList=[]
movieFolder="/home/venkat/movie_test"
temp_path=""

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
def calc_cache_size():
    filelist=[f for f in os.listdir("posters/")]
    size=0
    for f in filelist:
        size+=os.path.getsize("posters/"+f)
    readable_size=str(sizeof_fmt(size))
    ui.label_3.setText(QtCore.QString("Poster cache takes up "+ str(readable_size)))

def change_poster_quality(ui):
    quality=str(ui.comboBox.currentText())
    switcher = {
        "Low" : "w154",
        "Medium" : "w300",
        "High (Default)" : "w500",
        "Massive" : "original"
    }
    global max_size
    max_size=switcher[quality]

def get_path(ui):
    file_path=QtGui.QFileDialog.getExistingDirectory()
    global temp_path
    temp_path=file_path
    display_path=QtCore.QString(temp_path)
    ui.lineEdit.setText(display_path)
def imdb_id_from_title(title):
    pattern = 'http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q={movie_title}'
    url = pattern.format(movie_title=urllib.quote(title))
    r = requests.get(url)
    res = r.json()
    for section in ['popular','exact','substring']:
        key = 'title_' + section 
        if key in res:
            return res[key][0]['id']
def set_path(ui):
    global movieFolder
    if temp_path == "":
        return
    else:
        display_path=str(ui.lineEdit.text())
        movieFolder = display_path
        displayList()
def clear_poster_cache():
    filelist=[f for f in os.listdir("posters/")]
    for f in filelist:
        os.remove("posters/"+f)
    calc_cache_size()
def getMovieList():
    global movieFolder
    file_list=[]
    extensions = [
        '.avi',
        '.mkv',
        '.mp4',
    ]
    for root, directories, filenames in os.walk(movieFolder):
        for filename in filenames:
            if os.path.splitext(filename)[1] in extensions: 
                file_list.append(filename)
    return file_list 
def set_movie(ui):
    moviename=str(ui.listView.currentItem().text()).lower()
    global movieList
    global base_url
    global max_size
    global api_key
    for movie in movieList:
        if movie["title"].lower()==moviename:
            movieInfo=movie
            break
    res_print_text_list=[]
    if "resolution" in movieInfo.keys():
        res_print_text_list.append("Quality - " + movieInfo["resolution"])
    else:
        res_print_text_list.append("No Quality Info")
    if "quality" in movieInfo.keys():
        res_print_text_list.append(movieInfo["quality"])
    resPrintText=' '.join(res_print_text_list)
    if "year" in movieInfo.keys():
        ui.lineEdit_3.setText(QtCore.QString("Year - " + str(movieInfo["year"])))
    ui.lineEdit_2.setText(QtCore.QString(resPrintText))
    #Poster Code
    if "imdbid" not in movieInfo.keys():
        imdb_id=imdb_id_from_title(movieInfo["title"])
        movieInfo["imdbid"]=imdb_id
    else:
        imdb_id=movieInfo["imdbid"]
    if not os.path.isfile("posters/poster_" + imdb_id + "_" + max_size + ".jpeg"):
        ui.label_2.setText("Downloading...")
        image_req = 'http://api.themoviedb.org/3/movie/{imdbid}/images?api_key={key}' 
        r = requests.get(image_req.format(key=api_key,imdbid=imdb_id))
        api_response = r.json()
        posters  = api_response['posters']
        poster_urls = []
        for poster in posters:
            rel_path = poster['file_path']
            url = "{0}{1}{2}".format(base_url, max_size, rel_path)
            poster_urls.append(url)
        url=poster_urls[0]
        r = requests.get(url)
        filetype = r.headers['content-type'].split('/')[-1]
        filename = 'posters/poster_{0}_{1}.{2}'.format(imdb_id,max_size,filetype) 
        with open(filename,'wb') as w:
            w.write(r.content)
    ui.label_2.setPixmap(QtGui.QPixmap(os.getcwd() + "/posters/poster_" + imdb_id + "_" + max_size + '.jpeg'))
    calc_cache_size()

def displayList(mode="display"):
    search_string=str(ui.lineEdit_5.text()).lower()
    movies=getMovieList()
    if mode=="search" and search_string=="":
        mode="display"
    global movieList
    ui.listView.clear()
    for movie in movies:
        movieInfo = ptn.parse(movie)
        movie=movieInfo["title"].title()
        movieList.append(movieInfo)
        itemString = QtCore.QString(movie)
        item = QtGui.QListWidgetItem(itemString)
        if mode=="search":
            if search_string in movieInfo["title"].lower():
                ui.listView.addItem(item)
        else:
            ui.listView.addItem(item)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    ui.label.setText(_translate("Form","MovieManager",None))
    ui.pushButton_5.clicked.connect(displayList)
    ui.pushButton_2.clicked.connect(lambda: get_path(ui))
    ui.toolButton.clicked.connect(lambda: set_path(ui))
    ui.lineEdit_5.textChanged.connect(lambda: displayList(mode="search"))
    ui.listView.itemSelectionChanged.connect(lambda: set_movie(ui))
    ui.pushButton.clicked.connect(lambda: change_poster_quality(ui))
    ui.pushButton_3.clicked.connect(lambda: clear_poster_cache())
    ui.pushButton_4.clicked.connect(lambda: calc_cache_size())
    calc_cache_size()
    Form.show()
    displayList()
    sys.exit(app.exec_())