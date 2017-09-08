""" Customer book-control like classes. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []

import wx

from .button import ScrolledButtonPanel, EVT_SCROLLED_BUTTON_CLICKED
from .sizer import SingleItemSizer
from .event import NotifyEvent, NewEventTypes

# A scrolled button book control

__all__.extend([
    "ScrolledButtonBook"
    "SCROLLED_BOOKCTRL_PAGE_CHANGING",
    "SCROLLED_BOOKCTRL_PAGE_CHANGED"
])


(_evtSCROLLBOOK_PAGE_CHANGING, EVT_SCROLLBOOK_PAGE_CHANGING,
 _evtSCROLLBOOK_PAGE_CHANGED,  EVT_SCROLLBOOK_PAGE_CHANGED) = NewEventTypes(2)


class ScrolledButtonBook(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, style=wx.LEFT, border=-1, spacing=-1):
        """ Initialize the book control. """

        wx.Panel.__init__(self, parent, id)
        self._pages = []
        self._style = style
        self._dir = style & wx.ALL
        self._border = border
        self._spacing = spacing
        self._index = wx.NOT_FOUND
        self.InitGui()

    def InitGui(self):
        # On the left is the scrolled button window.  On the right
        # is split.  Top is an icon and a page text, bottom is the
        # contents of the control.

        self._buttons = ScrolledButtonPanel(
            self, wx.ID_ANY, 
            wx.VERTICAL if self._dir in (wx.LEFT, wx.RIGHT) else wx.HORIZONTAL,
            self._border, self._spacing
        )
        self._label = wx.Panel(self)
        self._bitmap = wx.StaticBitmap(self._label, wx.ID_ANY, wx.NullBitmap)
        self._text = wx.StaticText(self._label, wx.ID_ANY, "")
        self._panels = SingleItemSizer()

        labelSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelSizer.AddF(self._bitmap, wx.SizerFlags(0).Expand().Border(wx.ALL))
        labelSizer.AddF(self._text, wx.SizerFlags(1).Expand().Border(wx.ALL - wx.LEFT))
        self._label.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        self._text.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOTEXT))
        self._label.SetSizer(labelSizer)

        areaSizer = wx.BoxSizer(wx.VERTICAL)
        areaSizer.AddF(self._label, wx.SizerFlags(0).Expand().Border(wx.BOTTOM))
        areaSizer.AddF(self._panels, wx.SizerFlags(1).Expand())

        topSizer = wx.BoxSizer(wx.HORIZONTAL if self._dir in (wx.LEFT, wx.RIGHT) else wx.VERTICAL)

        if self._dir in (wx.LEFT, wx.TOP):
            topSizer.AddF(self._buttons, wx.SizerFlags(0).Expand().Border(wx.RIGHT if self._dir == wx.LEFT else wx.BOTTOM))

        topSizer.AddF(areaSizer, wx.SizerFlags(1).Expand())
        
        if self._dir in (wx.RIGHT, wx.BOTTOM):
            topSizer.AddF(self._buttons, wx.SizerFlags(0).Expand().Border(wx.LEFT if self._dir == wx.RIGHT else wx.TOP))

        self.SetSizer(topSizer)

        self.Bind(EVT_SCROLLED_BUTTON_CLICKED, self.OnClick)

    def AddPage(self, window, text, bitmap, select=False):
        page = (text, bitmap, window)
        self._pages.append(page)

        index = self._buttons.AddButton(wx.ID_ANY, text, bitmap, wx.TOP)
        self._panels.Add(window)

        if select == True or len(self._pages) == 1:
            self.SetPage(index)

    def ChangePage(self, index):
        oldpage = self._index

        if oldpage == index:
            return

        # Page changing event
        event = wx.BookCtrlEvent(_evtSCROLLBOOK_PAGE_CHANGING, self.GetId(), index, oldpage)
        self.GetEventHandler().ProcessEvent(event)

        if event.IsAllowed():
            # Page changed event
            self.SetPage(index)
            event = wx.BookCtrlEvent(_evtSCROLLBOOK_PAGE_CHANGED, self.GetId(), index, oldpage)
            wx.PostEvent(self, event)

    def SetPage(self, index):
        if index >= len(self._pages):
            return

        (text, bitmap, window) = self._pages[index]

        self._bitmap.SetBitmap(bitmap)

        font = self._text.GetFont()
        font.SetPixelSize((0, self._bitmap.GetSize().height))
        self._text.SetFont(font)

        self._text.SetLabel(text)
        self._index = index

        self._panels.SetSelection(window)
        self.Layout()

    def OnClick(self, event):
        self.ChangePage(event.GetInt())


def main():
    class Frame(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, "Test")

            book =  ScrolledButtonBook(self, wx.ID_ANY, style=wx.LEFT)

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.AddF(book, wx.SizerFlags(1).Expand().Border(wx.ALL))

            # Fake page 1
            panel = wx.Panel(book)
            text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
            tree = wx.TreeCtrl(panel)

            sz = wx.BoxSizer(wx.HORIZONTAL)
            sz.AddF(text, wx.SizerFlags(1).Expand().Border(wx.RIGHT))
            sz.AddF(tree, wx.SizerFlags(1).Expand())
            panel.SetSizer(sz)

            book.AddPage(panel, "Page1", wx.ArtProvider.GetBitmap(wx.ART_ERROR, size=(32,32)))

            # Fake page 2
            panel = wx.Panel(book)
            button = wx.Button(panel, wx.ID_ANY, "Revert")
            button2 = wx.Button(panel, wx.ID_ANY, "Save")
            text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

            sz1 = wx.BoxSizer(wx.HORIZONTAL)
            sz1.AddStretchSpacer(1)
            sz1.AddF(button, wx.SizerFlags(0).Center().Border(wx.RIGHT))
            sz1.AddF(button2, wx.SizerFlags(0).Center().Border(wx.LEFT))
            sz1.AddStretchSpacer(1)

            sz2 = wx.BoxSizer(wx.VERTICAL)
            sz2.AddF(sz1, wx.SizerFlags(0).Expand().Border(wx.BOTTOM))
            sz2.AddF(text, wx.SizerFlags(1).Expand())
            
            panel.SetSizer(sz2)
            book.AddPage(panel, "Page2", wx.ArtProvider.GetBitmap(wx.ART_WARNING, size=(32,32)))

            self.SetSizerAndFit(sizer)
            self.SetAutoLayout(1)

            self.Bind(EVT_SCROLLBOOK_PAGE_CHANGING, self.OnChanging)
            self.Bind(EVT_SCROLLBOOK_PAGE_CHANGED, self.OnChanged)

        def OnChanging(self, event):
            if wx.MessageBox("Veto the event", "Question", wx.YES_NO) == wx.YES:
                event.Veto()
            pass

        def OnChanged(self, event):
            wx.MessageBox("Page changed from {0} to {1}".format(event.GetOldSelection(), event.GetSelection()))



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


