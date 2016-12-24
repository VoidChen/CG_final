import sys
from PIL import Image, ImageQt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from palette import *
from util import *

class CustomLabel(QLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(CustomLabel, self).__init__(parent, flags)
        self.bind_image = None

def limit_scale(image, width, height):
    if image.width > width or image.height > height:
        if image.width/image.height > width/height:
            scale_size = (width, width * image.height//image.width)
        else:
            scale_size = (height * image.width//image.height, height)

        return image.resize(scale_size)
    else:
        return image

def load_image(label_image, label_palette):
    #get image
    image_name = QFileDialog.getOpenFileName()[0]
    image = Image.open(image_name)
    print(image_name, image.format, image.size, image.mode)

    #get palette
    lab = rgb2lab(image)
    palette = build_palette(lab)

    #set image label
    label_image.bind_image = ImageQt.ImageQt(limit_scale(image, width, height))
    label_image.setPixmap(QPixmap.fromImage(label_image.bind_image))

    #set palette label
    label_palette.bind_image = ImageQt.ImageQt(draw_palette(palette))
    label_palette.setPixmap(QPixmap.fromImage(label_palette.bind_image))

def save_image():
    pass

def reset():
    pass

if __name__ == '__main__':
    #init
    width = 900
    height = 600
    app = QApplication(sys.argv)

    #main widget
    widget = QWidget()
    widget.resize(width, height)
    widget.setWindowTitle('CG')
    widget.show()

    #label
    label_image = CustomLabel()
    label_image.setAlignment(Qt.AlignCenter)
    label_image.resize(width, height)

    label_palette = CustomLabel()
    label_palette.setAlignment(Qt.AlignCenter)
    label_palette.resize(width, 100)

    #button
    btn_load = QPushButton('Load image')
    btn_load.clicked.connect(lambda: load_image(label_image, label_palette))
    btn_load.show()

    btn_save = QPushButton('Save image')
    btn_save.clicked.connect(lambda: save_image())
    btn_save.show()

    btn_reset = QPushButton('Reset')
    btn_reset.clicked.connect(lambda: reset())
    btn_reset.show()

    #layout
    layout_btn = QHBoxLayout()
    layout_btn.addWidget(btn_load)
    layout_btn.addWidget(btn_save)
    layout_btn.addWidget(btn_reset)

    layout = QVBoxLayout()
    layout.addWidget(label_image)
    layout.addWidget(label_palette)
    layout.addLayout(layout_btn)

    widget.setLayout(layout)

    app.exec()
