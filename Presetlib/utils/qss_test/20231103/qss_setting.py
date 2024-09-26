MAIN_UI_QSS = """
                color: #FFFFFF;
                background-color: #212121;
                font-family: Titillium;
                font-size: 18px;
                """

MAIN_TAB_BACKGROUND_QSS = """
                color: #FFFFFF;
                background-color: #1F2D3C;
                font-family: Titillium;
                font-size: 18px;
                """


BUTTON_QSS = """
            QPushButton {
                color: #FFFFFF;
                font-family: Titillium;
                font-size: 15px;
                border-radius: 5px;
                background-color: #6495ED;   /* Set the default background color */
            }
            QPushButton:hover {
                /* background-color: #6495ED;*/   /* Keep the original background color first */
                border: 3px solid transparent; /* Ensure the border remains unaffected */
                background-image: rgba(255, 255, 255, 0.1);  /* Then overlay with a semi-transparent white */
                    color: #ffffff;
                background-color: 
                    QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                    stop: 0 #000000, stop: 1 #00aaff);
            }
            QPushButton:pressed {
                background-color: #00BFFF;   /* Background color for when the button is pressed */
            }
            """

DRAG_QSS = '''
            QSlider {
                border-radius: 10px;
            }
            QSlider::groove:horizontal {
                height: 5px;
                background: #000;
            }
            QSlider::handle:horizontal{
                background: #f00;
                width: 16px;
                height: 16px;
                margin:-6px 0;
                border-radius:8px;
            }
            QSlider::sub-page:horizontal{
                background:#f90;
            }
        '''

LINE_EDIT_QSS = """
    QLineEdit {
        border: 1px solid #6495ED; /* Set the border color of the line edit to red */
        /* Add any other styles you want for the line edit */
        border-color: #6495ED;
        border-radius: 5px;
    }
    QLineEdit:focus {
        border-color: blue; /* Change border color to blue when the line edit is focused */
    }
"""


RADIOBUTTON_QSS = """
    QRadioButton {
        border: 1px solid #6495ED; /* Set the border color of the radio button to red */
        /* Add any other styles you want for the radio button */
        border-radius: 10px;
    }
    QRadioButton::indicator {
        /* You can also define the style for the indicator, for example: */
        width: 13px;  /* Set the width of the indicator */
        height: 13px; /* Set the height of the indicator */
    }
    QRadioButton::indicator:checked {
        border: 1px solid #6495ED; /* Style for the indicator when the radio button is checked */
    }
    QRadioButton::indicator:unchecked {
        background-color: none; /* Style for the indicator when the radio button is unchecked */
    }
"""