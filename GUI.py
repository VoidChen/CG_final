import sys
from PIL import Image, ImageQt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from palette import *
from util import *
from transfer import *

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
        self.repaint()

    def mousePressEvent(self, event):
        #init
        global image_rgb_m, image_lab_m, palette_m

        #get color
        current = QColor(*RegularRGB(LABtoRGB(RegularLAB(self.bind_color))))
        color = QColorDialog.getColor(initial=current, options=QColorDialog.DontUseNativeDialog)
        if color.isValid():
            RGB = color.red(), color.green(), color.blue()
            LAB = ByteLAB(RGBtoLAB(RGB))
            print('Set palette color', self.palette_index, RGB, LAB)

            #modify palette_m
            if luminance_flag:
                palette_m = modify_luminance(palette_m, self.palette_index, LAB[0])
            palette_m[self.palette_index] = LAB

            #modify palette labels
            for i in range(len(palette_m)):
                labels_palette[i].setColor(palette_m[i])

            #transfer image
            image_lab_m = image_transfer(image_lab, palette, palette_m, sample_level=10, luminance_flag=luminance_flag)
            image_rgb_m = lab2rgb(image_lab_m)
            label_image.setImage(limit_scale(image_rgb_m, width, height))

def load_image(label_image, labels_palette):
    #init
    global image_rgb, image_rgb_m, image_lab, image_lab_m, palette, palette_m

    #get image
    image_name = QFileDialog.getOpenFileName()[0]
    if image_name == '':
        return

    image_rgb = Image.open(image_name)
    print(image_name, image_rgb.format, image_rgb.size, image_rgb.mode)

    #get palette
    image_lab = rgb2lab(image_rgb)
    palette = build_palette(image_lab, len(labels_palette))
    for color in palette:
        print('LAB:', color, 'LAB_fix:', RegularLAB(color), 'RGB:', LABtoRGB(RegularLAB(color)))

    #set image label
    label_image.setImage(limit_scale(image_rgb, width, height))

    #set palette label
    for i in range(len(palette)):
        labels_palette[i].setColor(palette[i])

    #copy object
    image_rgb_m = copy.deepcopy(image_rgb)
    image_lab_m = copy.deepcopy(image_lab)
    palette_m = copy.deepcopy(palette)

def save_image():
    #get image
    save_name = QFileDialog.getSaveFileName()[0]
    if save_name != '':
        image_rgb_m.save(save_name)

def reset():
    #init
    global image_rgb_m, image_lab_m, palette_m

    #reset object
    image_rgb_m = copy.deepcopy(image_rgb)
    image_lab_m = copy.deepcopy(image_lab)
    palette_m = copy.deepcopy(palette)

    #reset GUI
    label_image.setImage(limit_scale(image_rgb, width, height))
    for i in range(len(palette)):
        labels_palette[i].setColor(palette[i])

def luminance_flag_changed(box):
    global luminance_flag
    luminance_flag = box.currentData()

if __name__ == '__main__':
    #init
    width = 900
    height = 600
    palette_num = 5
    luminance_flag = False
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

    #combobox
    box_luminance_flag = QComboBox()
    box_luminance_flag.activated.connect(lambda: luminance_flag_changed(box_luminance_flag))
    box_luminance_flag.addItem('Luminance transfer: On', QVariant(True))
    box_luminance_flag.addItem('Luminance transfer: Off', QVariant(False))
    box_luminance_flag.setCurrentIndex(1)
    box_luminance_flag.show()

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
    layout.addWidget(box_luminance_flag)

    widget.setLayout(layout)

    app.exec()
