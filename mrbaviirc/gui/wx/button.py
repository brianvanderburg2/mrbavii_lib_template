""" Button replaced widgets. """

from __future__ import absolute_import

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"

__all__ = []


import wx
import wx.lib.newevent as newevent
import wx.lib.scrolledpanel as scrolled


# Scrolled button panel
__all__.extend(("ScrolledButtonPanel", "EVT_SCROLLED_BUTTON_CLICK", "ScrolledButtonEvent"))

(ScrolledButtonEvent, EVT_SCROLLED_BUTTON_CLICKED) = newevent.NewCommandEvent()

class _ScrolledButtonPanelItem(object):
    """ Contain data about a button. """
    def __init__(self):
        self.window = None
        self.label = ""
        self.bitmap = wx.NullBitmap
        self.dir = wx.LEFT
        self.userdata = None

class ScrolledButtonPanel(scrolled.ScrolledPanel):
    """ A panel which can have buttons added to it. """

    def __init__(self, parent=None, id=wx.ID_ANY, dir=wx.HORIZONTAL, border=-1, spacing=-1):
        scrolled.ScrolledPanel.__init__(self, parent, id)

        if dir == wx.HORIZONTAL:
            self.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_NEVER)
        else:
            self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)

        self._buttons = []
        self._dir = dir
        self._border = wx.SizerFlags.GetDefaultBorder() if border == -1 else border
        self._spacing = wx.SizerFlags.GetDefaultBorder() if border == -1 else spacing
        self._sizer = wx.GridSizer(0, 1, spacing, 0)

        self._topsizer = wx.BoxSizer(wx.VERTICAL)
        self._topsizer.AddF(self._sizer, wx.SizerFlags(0).Expand().Border(wx.ALL, self._border))
        self._topsizer.AddStretchSpacer(1)


        if dir == wx.HORIZONTAL:
            self._scrollbar_size = wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y)
        else:
            self._scrollbar_size = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)

        self.SetSizer(self._topsizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)

    def Update(self):
        if self._dir == wx.HORIZONTAL:
            size = wx.Size(self.GetMinSize().width, self._topsizer.GetMinSize().height + self._scrollbar_size)
            #for item in self._sizer.GetChildren():
            #    size.IncTo(item.CalcMin())
            self.SetMinSize(size)
        else:
            size = wx.Size(self._topsizer.GetMinSize().width + self._scrollbar_size, self.GetMinSize().height)
            #for item in self._sizer.GetChildren():
            #    size.IncTo(item.CalcMin())
            self.SetMinSize(size)
            
        self.SetupScrolling()
        self.Layout()

    def AddButton(self, id=wx.ID_ANY, label="", bitmap=wx.NullBitmap, dir=wx.LEFT, userdata=None):
        btn = _ScrolledButtonPanelItem()

        btn.window = wx.Button(self, id, label)
        btn.label = label
        btn.bitmap = bitmap
        btn.dir = dir
        btn.userdata = userdata

        if bitmap.IsOk():
            btn.window.SetBitmap(bitmap, 0 if dir is None else dir)

        self._sizer.Add(btn.window, 0, wx.EXPAND | wx.ALL, self._border)

        self._buttons.append(btn)
        self.Update()

        return len(self._buttons) - 1

    def RemoveButton(self, index):
        if index >= len(self._buttons):
            return

        btn = self._buttons.pop(index)
        btn.window.Destroy()
                
        self.Update()

    def SetButtonLabel(self, index, label):
        if index >= len(self._buttons):
            return

        btn = self._buttons[index]
        btn.label = label
        btn.window.SetLabel(label)
        self.Update()

    def GetButtonLabel(self, index):
        if index >= len(self._buttons):
            return ""

        btn = self._buttons[index]
        return btn.label

    def SetButtonBitmap(self, index, bitmap, dir=None):
        if index >= len(self._buttons):
            return

        btn = self._buttons[index]
        btn.bitmap = bitmap
        if dir is None:
            dir = btn.dir
        else:
            btn.dir = dir

        btn.window.SetBitmap(bitmap, dir)
        self.Update()

    def GetButtonBitmap(self, index):
        if index >= len(self._buttons):
            return wx.NullBitmap

        btn = self._buttons[index]
        return btn.bitmap

    def SetButtonUserData(self, index, userdata):
        if index >= len(self._buttons):
            return

        btn = self._buttons[index]
        btn.userdata = userdata

    def GetButtonUserData(self, index):
        if index >= len(self._buttons):
            return None

        btn = self._buttons[index]
        return btn.userdata

    def GetButtonWindowID(self, index):
        pass

    def OnButtonClick(self, event):
        window = event.GetEventObject()

        for (index, btn) in enumerate(self._buttons):
            if btn.window is window:
                evt = ScrolledButtonEvent(self.GetId())

                evt.SetEventObject(self)
                evt.SetClientData(btn.userdata)
                evt.SetInt(index)

                wx.PostEvent(self.GetEventHandler(), evt)

                break
        else:
            event.Skip()

                
        


# Test code
def main():
    class Frame(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, "Test")

            scrolled = ScrolledButtonPanel(self, wx.ID_ANY, wx.VERTICAL, 10, 10)

            scrolled.AddButton(wx.ID_ANY, "Home", wx.ArtProvider.GetBitmap(wx.ART_ERROR), wx.TOP)
            scrolled.AddButton(wx.ID_ANY, "Home And Back to Home", wx.ArtProvider.GetBitmap(wx.ART_ERROR), wx.TOP)
            scrolled.AddButton(wx.ID_ANY, "Home And Back", wx.ArtProvider.GetBitmap(wx.ART_WARNING), wx.TOP)

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(scrolled, 0, wx.EXPAND)
            sizer.Add(wx.StaticText(self, wx.ID_ANY, "Test Text"))
            #sizer.AddStretchSpacer(1)

            self.SetSizerAndFit(sizer)
            self.SetAutoLayout(1)

            self.scrolled = scrolled

            self.Bind(EVT_SCROLLED_BUTTON_CLICKED, self.OnButton)
            #self.Bind(wx.EVT_BUTTON, self.OnButton)

        def OnButton(self, event):
            print(event.GetInt())
            print(event.GetClientData())
            self.scrolled.SetButtonBitmap(0, self.scrolled.GetButtonBitmap(1))
            self.scrolled.RemoveButton(1)
            #self.scrolled.SetButtonBitmap(1, wx.ArtProvider.GetBitmap(wx.ART_WARNING), wx.BOTTOM)
            #self.scrolled.SetButtonLabel(0, "Hahahahahahahahahahaha")

            self.Layout()
            self.SetMinClientSize(self.GetSizer().GetMinSize())


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









