import controller
import lxml.etree as ET
import os
import wx

from functools import partial

from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel
from wx.lib.pubsub import pub


class Boomslang(wx.Frame):

    def __init__(self, xml_obj):
        self.size = (800, 600)
        wx.Frame.__init__(self, parent=None, title='Boomslang XML',
                          size=(800, 600))

        self.xml_root = None
        self.current_directory = os.path.expanduser('~')
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel.SetSizer(self.main_sizer)

        self.create_menu()
        self.create_tool_bar()

        self.Show()

    def create_display(self):
        splitter = wx.SplitterWindow(self)

        tree_panel = BoomTreePanel(splitter, self.xml_root)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        splitter.SplitVertically(tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(self.size[0] / 2)
        self.main_sizer.Add(splitter, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.Layout()

    def create_menu(self):
        """
        Creates the menu bar and menu items for the main frame
        """
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()

        save_menu_item = file_menu.Append(
            wx.NewId(), 'Save', '')
        self.Bind(wx.EVT_MENU, self.on_save, save_menu_item)

        exitMenuItem = file_menu.Append(
            wx.NewId(), 'Quit', '')
        menu_bar.Append(file_menu, "&File")

        self.SetMenuBar(menu_bar)

    def create_tool_bar(self):
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((16,16))

        open_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        openTool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, open_ico, "Open", "Open an XML File")
        self.Bind(wx.EVT_MENU, self.on_open, openTool)

        save_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (16,16))
        saveTool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, save_ico, "Save", "Saves the XML")
        self.Bind(wx.EVT_MENU, self.on_save, saveTool)

        self.toolbar.Realize()

    def parse_xml(self, xml_path):
        self.current_directory = os.path.dirname(xml_path)
        try:
            self.xml_tree = ET.parse(xml_path)
        except IOError:
            print('Bad file')
            return
        except Exception as e:
            print('Really bad error')
            print(e)
            return

        self.xml_root = self.xml_tree.getroot()

    def on_open(self, event):
        xml_path = controller.open_file(self)

        if xml_path:
            self.parse_xml(xml_path)
            self.create_display()

    def on_save(self, event):
        """
        Event handler that saves the data to disk
        """
        path = controller.save_file(self)
        if path:
            if '.xml' not in path:
                path += '.xml'

            # Update the current directory to the save location
            self.current_directory = os.path.dirname(path)

            # Save the xml
            self.xml_tree.write(path)


if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = Boomslang(xml_path)
    app.MainLoop()