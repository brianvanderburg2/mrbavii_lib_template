""" Customer book-control like classes. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []

import wx

from .button import ScrolledButtonPanel, EVT_SCROLLED_BUTTON_CLICKED
from .sizer import SingleItemSizer

__all__.append("ScrolledButtonBook")
class ScrolledButtonBook(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, style=0):
        """ Initialize the book control. """

        wx.Panel.__init__(self, parent, id)
        self._pages = []
        self.InitGUI()

    def InitGUI(self):
        # On the left is the scrolled button window.  On the right
        # is split.  Top is an icon and a page text, bottom is the
        # contents of the control.

        self._buttons = ScrolledButtonPanel(self, dir=wx.VERTICAL)
        self._bitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap)
        self._text = wx.StaticText(self, wx.ID_ANY, "")
        self._panels = SingleItemSizer()

        labelSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelSizer.Add(self._bitmap, 0, wx.EXPAND)
        labelSizer.Add(self._text, 1, wx.EXPAND)

        areaSizer = wx.BoxSizer(wx.VERTICAL)
        areaSizer.Add(labelSizer, 0, wx.EXPAND)
        areaSizer.Add(self._panels, 1, wx.EXPAND)

        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(self._buttons, 0, wx.EXPAND)
        topSizer.Add(areaSizer, 1, wx.EXPAND)

        self.SetSizer(topSizer)

        self.Bind(EVT_SCROLLED_BUTTON_CLICKED, self.OnClick)

    def AddPage(self, text, bitmap, window):
        page = (text, bitmap, window)
        self._pages.append(page)

        index = self._buttons.AddButton(wx.ID_ANY, text, bitmap, wx.TOP)
        self._panels.Add(window)
        self.SetPage(index)

    def SetPage(self, index):
        if index >= len(self._pages):
            return

        (text, bitmap, window) = self._pages[index]

        self._text.SetLabel(text)
        self._bitmap.SetBitmap(bitmap)
        self._panels.SetSelection(window)
        self.Layout()

    def OnClick(self, event):
        self.SetPage(event.GetInt())

def main():
    class Frame(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, "Test")

            book =  ScrolledButtonBook(self, wx.ID_ANY)

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(book, 1, wx.EXPAND)

            book.AddPage("Notes", wx.ArtProvider.GetBitmap(wx.ART_ERROR), wx.StaticText(book, wx.ID_ANY, "HAHAAH"))
            book.AddPage("Poop", wx.ArtProvider.GetBitmap(wx.ART_WARNING), wx.StaticText(book, wx.ID_ANY, "Hol"))

            self.SetSizerAndFit(sizer)
            self.SetAutoLayout(1)


    class App(wx.App):
        def OnInit(self):
            frame = Frame()
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = App()
    app.MainLoop()


if __name__ == "__main__":
    main()


