import os
import sys 
#from pathlib import Path
from PySide2.QtWidgets import QPushButton, QVBoxLayout, QApplication ,QListWidget, QListView, QLabel, QWidget, QAbstractItemView, QSplitter 
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon, Qt, QDrag
from PySide2 import QtCore

PATH = os.path.join('.','img_src')
print('LayerSelector Loaded with path:' , PATH)

class CustomQStandardItem(QStandardItem):
    def __init__(self, icon, text):
        super().__init__(icon, text)
    
    def dropMimeData(self, data, action, row, column, parent):
        pass
        
class LayersList(QWidget):
    '''
    LayerList class which acts as collapsable list.
    '''
    def __init__(self, name, layers, expand = True):
        super().__init__()
        self.currently_expanded = True
        self.main_layout = QVBoxLayout()
        self.main_layout.setMargin(0)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.expand_button = QPushButton(name)
        self.expand_button.setToolTip("List of {} Layers".format(name))
        #self.expand_button.setIcon(QIcon(os.path.join(PATH,'LayersList_Up.png')))
        self.layer_list = QListView()
        self.layer_list.setDragEnabled(True)
        self.container_model = QStandardItemModel()
        for l in layers:
            #qs = CustomQStandardItem(QIcon(os.path.join(PATH,'LayersList_Layer_Icon.png')),l)
            pass
            #self.container_model.appendRow(qs)
        self.layer_list.setModel(self.container_model)
        self.layer_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.main_layout.addWidget(self.expand_button,0, Qt.AlignTop)
        self.main_layout.addWidget(self.layer_list, 0, Qt.AlignTop)
        self.expand_button.clicked.connect(self.expand)
        self.setLayout(self.main_layout)
        self.resized_size = 16.5 * len(layers)
        self.set_styling()
        if not expand:
            self.expand()
            
    @QtCore.Slot()
    def expand(self):
        if self.currently_expanded:
            self.layer_list.setMaximumHeight(0)
            #self.expand_button.setIcon(QIcon(os.path.join(PATH,'LayersList_Down.png')))
            self.currently_expanded = False
        else:
            self.layer_list.setMaximumHeight(self.resized_size)
            #self.expand_button.setIcon(QIcon(os.path.join(PATH,'LayersList_Up.png')))
            self.currently_expanded = True
            
    def set_styling(self):
        self.setStyleSheet("background-color:aliceblue ;")
        self.expand_button.setStyleSheet("text-align:left;")
        self.layer_list.setStyleSheet("background-color:aliceblue; border:1px solid;border-style: ridge;")

class LayersSelectorWidget(QWidget):
    '''
    LayerChoiceWidget class provide widget plugin for picking layers.
    '''
    def __init__(self):
        super().__init__()
        names = ['Core Layers',
                 'Convolution Layers',
                 'Pooling Layers',
                 'Recurrent Layers',
                 'Preprocessing Layers',
                 'Attention Layers',
                 'Reshaping Layers',
                 'Locally-Connected Layers'
                 ]
        layers = [
            ['Dense', 'Activation', 'Embedding', 'Masking', 'Lambda'],
            ['Conv1D', 'Conv2D', 'Conv3D', 'SeparableConv1D', 'SeparableConv2D', 'DepthwiseConv2D', 'Conv2DTranspose', 'Conv3Dtranspose'],
            ['MaxPooling1D', 'MaxPooling2D', 'MaxPooling3D', 'AveragePooling1D', 'AveragePooling2D', 'AveragePooling3D', 'GlobalMAxPooling1D', 'GlobalMAxPooling2D', 'GlobalMAxPooling3D', 'GlobalAveragePooling1D', 'GlobalAveragePooling2D', 'GlobalAveragePooling3D'],
            ['LSTM', 'GRU', 'SimpleRNN', 'TimeDistributed', 'BiDirectional', 'ConvLSTM2D'],
            ['TextToVector', 'Normalization'],
            ['Attention', 'AdditiveAttention'],
            ['Reshape', 'Flatten', 'Cropping1D', 'Cropping2D', 'Cropping3D', 'UpSampling1D', 'UpSampling2D', 'UpSampling3D', 'ZeroPadding1D', 'ZeroPadding2D', 'ZeroPadding3D'],
            ['LocallyConnected1D', 'LocallyConnected2D']
        ]
        self.main_layout = QVBoxLayout()
        for i in range(len(names)):
            if i > 3:
                self.main_layout.addWidget(LayersList(names[i], layers[i], False))
            else:
                self.main_layout.addWidget(LayersList(names[i], layers[i]))                
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignTop)        
        self.main_layout.setMargin(0)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        del(names)
        del(layers)
        self.set_styling()
        
    def set_styling(self):
        self.setStyleSheet("background-color:aliceblue; border:0px solid;border-style: solid;")
        