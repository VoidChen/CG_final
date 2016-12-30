import sys
from PIL import Image, ImageQt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from palette import *
from util import *

class ImageLabel(QLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(ImageLabel, self).__init__(parent, flags)
        self.bind_image = None

    def setImage(self, image):
        self.bind_image = ImageQt.ImageQt(image)
        self.setPixmap(QPixmap.fromImage(self.bind_image))

class PaletteLabel(ImageLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(PaletteLabel, self).__init__(parent, flags)
        self.palette_index = -1
        self.bind_color = None

    def setColor(self, color):
        self.bind_color = color
        self.setImage(draw_color(color))

    def mousePressEvent(self, event):
        #get color
        color = QColorDialog.getColor()
        if color.isValid():
            RGB = color.red(), color.green(), color.blue()
            LAB = ByteLAB(RGBtoLAB(RGB))
            print('Set palette color', self.palette_index, RGB, LAB)

            #set palette
            self.setColor(LAB)

def load_image(label_image, labels_palette):
    #get image
    image_name = QFileDialog.getOpenFileName()[0]
    image = Image.open(image_name)
    print(image_name, image.format, image.size, image.mode)

    #get palette
    lab = rgb2lab(image)
    palette = build_palette(lab, len(labels_palette))

    #set image label
    label_image.setImage(limit_scale(image, width, height))

    #set palette label
    for i in range(len(palette)):
        print('LAB:', palette[i], 'LAB_fix:', RegularLAB(palette[i]), 'RGB:', LABtoRGB(RegularLAB(palette[i])))
        labels_palette[i].setImage(draw_color(palette[i]))

def save_image():
    pass

def reset():
    pass

if __name__ == '__main__':
    #init
    width = 900
    height = 600
    palette_num = 5
    app = QApplication(sys.argv)

    #main widget
    widget = QWidget()
    widget.resize(width, height)
    widget.setWindowTitle('CG')
    widget.show()

    #label
    label_image = ImageLabel()
    label_image.setAlignment(Qt.AlignCenter)

    labels_palette = []
    for i in range(palette_num):
        labels_palette.append(PaletteLabel())
        labels_palette[-1].setAlignment(Qt.AlignCenter)
        labels_palette[-1].palette_index = i
        labels_palette[-1].setPixmap(QPixmap(100, 100))
        labels_palette[-1].pixmap().fill(QColor(0, 0, 0, 0))

    #button
    btn_load = QPushButton('Load image')
    btn_load.clicked.connect(lambda: load_image(label_image, labels_palette))
    btn_load.show()

    btn_save = QPushButton('Save image')
    btn_save.clicked.connect(lambda: save_image())
    btn_save.show()

    btn_reset = QPushButton('Reset')
    btn_reset.clicked.connect(lambda: reset())
    btn_reset.show()

    #layout
    layout_image = QHBoxLayout()
    layout_image.addWidget(label_image)

    layout_palette = QHBoxLayout()
    for label in labels_palette:
        layout_palette.addWidget(label)

    layout_btn = QHBoxLayout()
    layout_btn.addWidget(btn_load)
    layout_btn.addWidget(btn_save)
    layout_btn.addWidget(btn_reset)

    layout = QVBoxLayout()
    layout.addLayout(layout_image)
    layout.addLayout(layout_palette)
    layout.addLayout(layout_btn)

    widget.setLayout(layout)

    app.exec()
