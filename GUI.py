#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2024"
__license__    = "MIT License"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "0.0.1"
"""
# Engineering GUI dashboard to view 8 camera image feeds and develop Computer Vision pipeline

# Disable PyLint (VSCode) linting messages that seem unuseful
# https://pypi.org/project/pylint/
# pylint: disable=invalid-name
# pylint: disable=global-statement
#
# Disable Pyright (Zed IDE) linting messages that seem unuseful
# https://pypi.org/project/pyright/
# https://github.com/microsoft/pyright/blob/main/docs/getting-started.md
# Using Command Line Interface (CLI): pyright GUI.py
# Update using "pip install --upgrade pyright" in CLI

# Standard Python libraries
import sys          # Use to determine which OS (MacOS, Linux, or Windows) code is running on

# Browser base GUI framework to build and display a user interface mobile, PC, and Mac
# https://nicegui.io/
from nicegui import app, ui
from nicegui.events import MouseEventArguments

# Load environment variables for usernames, passwords, & API keys
# https://pypi.org/project/python-dotenv/
from dotenv import dotenv_values

## Internally developed modules
import GlobalConstants as GC    # Useful global constants used across multiple files
import Crater as cr             # Crater class to define name, size, and location of craters
import Database as db           # SQLite database to store crate locations


## Global Variables
# Application boots up in light mode
isDarkModeOn = False
darkMode  = ui.dark_mode()
# Browser window pixel sizes
winWidth  = -1
winHeight = -1

async def page_refresh():
    set_background(GC.STRONG_BOX_GREEN)
    await get_browser_window_size()



def set_background(color: str) -> None:
    ui.query('body').style(f'background-color: {color}')


async def get_browser_window_size() -> None:
    """ Use Javascript to get the size of the current browser window NiceGUI is running in
        https://nicegui.io/documentation/run_javascript#run_javascript

    Args:
        TODO NEEDED? windowID (interger): Number from 0 to ? defining each Window

    Return(s):
        Updates window width (winWidth) and window height (winHeight) global variable 
    """
    global winWidth
    global winHeight
    winWidth  = await ui.run_javascript('window.innerWidth')
    winHeight = await ui.run_javascript('window.innerHeight')

    if GC.DEBUG_STATEMENTS_ON: print(f"Browser Window is {winWidth} px wide and {winHeight} px tall")



if __name__ in {"__main__", "__mp_main__"}:
    darkMode.disable()

    #db1 = db.Database("strongbox-gui-db.db")
    get_browser_window_size()

    #ui.timer(GC.GUI_PAGE_REFRESH_RATE, lambda: page_refresh())
    ui.timer(GC.GUI_PAGE_REFRESH_RATE, lambda: set_background(GC.STRONG_BOX_GREEN))
    with ui.row().classes("self-center"):
        #ui.button("RUN JAVASCRIPT", on_click=lambda e: get_browser_window_size())
        ui.button("RUN JAVASCRIPT", on_click=lambda e: page_refresh())

    #TODO FIND USE FOR SVG DRAWING UPDATE AT BOTTOM OF PAGE ui.timer(GC.CLOCK_UPDATE_TIME, lambda: clock.set_content(build_svg()))

    if __name__ == "__main__":
        # Outgoing API connection should only run once, on single port, in a single threaded main function
        # apiBackgroundProcessCode = start_api()
        pass

    # Incoming APIs
    try:
        config = dotenv_values()
        url = config['STRONG_BOX_GUI_DB_URL']
        key = config['STRONG_BOX_GUI_DB_TOKEN']

        # Create directory and URL for local storage of images
        if sys.platform.startswith('darwin'):
            app.add_static_files('/static/images', GC.MAC_CODE_DIRECTORY +'/static/images')
            app.add_static_files('/static/videos', GC.MAC_CODE_DIRECTORY + '/static/videos')
        elif sys.platform.startswith('linux'):
            app.add_static_files('/static/images', GC.LINUX_CODE_DIRECTORY + '/static/images')
            app.add_static_files('/static/videos', GC.LINUX_CODE_DIRECTORY + '/static/videos')
        elif sys.platform.startswith('win'):
            print("WARNING: Running MainHouse.py server code on Windows OS is NOT fully supported")
            app.add_static_files('/static/images', GC.WINDOWS_CODE_DIRECTORY + '/static/images')
            app.add_static_files('/static/videos', GC.WINDOWS_CODE_DIRECTORY + '/static/videos')
        else:
            print("ERROR: Running on an unknown operating system")
            quit()

    except KeyError:
        pass
        #db1.insert_debug_logging_table("ERROR: Could not find .ENV file when calling dotenv_values()")


    finally:
        pass
        #url = config['STRONG_BOX_GUI_DB_URL']
        #key = config['STRONG_BOX_GUI_DB_TOKEN']


    ui.colors(primary=GC.STRONG_BOX_BLUE)


    # Eight HD 720p (1280 × 720) and/or 4K UHD (3840 × 2160) cameras on the corners of the A & B sides of a Strong Box cube in two 3 x 3 grids (for MVP. Mission code with stitch into two circles)
    imageWidth = 720
    frameRate = 30
    textFontSize = 50

    if winWidth < (1080/2):
        textFontSize = 40
    if winWidth < (1080/4):
        textFontSize = 30
    if GC.DEBUG_STATEMENTS_ON: print(f"Font size was set to: {textFontSize}")

    lastFramesA = [GC.LAST_FRAMES+"A0.jpeg", GC.LAST_FRAMES+"A1.jpeg", GC.LAST_FRAMES+"A2.jpeg", GC.LAST_FRAMES+"A3.jpeg"]
    lastFramesB = [GC.LAST_FRAMES+"B0.jpeg", GC.LAST_FRAMES+"B1.jpeg", GC.LAST_FRAMES+"B2.jpeg", GC.LAST_FRAMES+"B3.jpeg"]
    currentFramesA = [GC.CURRENT_FRAMES+"A0.jpeg", GC.CURRENT_FRAMES+"A1.jpeg", GC.CURRENT_FRAMES+"A2.jpeg", GC.CURRENT_FRAMES+"A3.jpeg"]
    currentFramesB = [GC.CURRENT_FRAMES+"B0.jpeg", GC.CURRENT_FRAMES+"B1.jpeg", GC.CURRENT_FRAMES+"B2.jpeg", GC.CURRENT_FRAMES+"B3.jpeg"]

    with ui.footer(value=True) as footer:
        ui.label('Strong Box: Air Plant One Mission').style(f"font-size: 25px;")

    # A0 is the image on the A side of Strong Box hardware, displayed at 0 degrees (on compass which is North) on GUI
    # B270 os the image on the B side of Strong Box hardware, displayed at 270 degrees (on compass which is West) on GUI
    with ui.grid(columns=3).classes("self-center"):
        ui.label("").style(f"width: {imageWidth}px;")
        ui.label("").style(f"width: {imageWidth}px;")
        ui.label("").style(f"width: {imageWidth}px;")

        blankImageCellInGrid = ui.image('')
        cameraA0image = ui.image(GC.TEST_IMAGE)
        blankImageCellInGrid = ui.image('')

        cameraA270image = ui.image(GC.TEST_IMAGE)
        ui.label(f"SIDE A CAMERA'S: {frameRate} Hz").style(f"width: {imageWidth}px; font-size: {textFontSize}px; display: flex; justify-content: center; align-items: center;")
        cameraA90image = ui.image(GC.TEST_IMAGE)

        blankImageCellInGrid = ui.image('')
        cameraA180image = ui.image(GC.TEST_IMAGE)
        blankImageCellInGrid = ui.image('')

    with ui.grid(columns=3).classes("self-center"):
        ui.label("").style(f"width: {imageWidth}px;")
        ui.label("").style(f"width: {imageWidth}px;")
        ui.label("").style(f"width: {imageWidth}px;")

        blankImageCellInGrid = ui.image('')
        cameraB0image = ui.image(GC.TEST_IMAGE)
        blankImageCellInGrid = ui.image('')

        cameraB270image = ui.image(GC.TEST_IMAGE)
        ui.label(f"SIDE B CAMERA'S: {frameRate} Hz").style(f"width: {imageWidth}px; font-size: 50px; display: flex; justify-content: center; align-items: center;")
        cameraB90image = ui.image(GC.TEST_IMAGE)

        blankImageCellInGrid = ui.image('')
        cameraB180image = ui.image(GC.TEST_IMAGE)
        blankImageCellInGrid = ui.image('')

    ui.run()
