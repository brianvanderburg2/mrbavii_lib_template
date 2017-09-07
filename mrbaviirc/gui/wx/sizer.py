""" Customer wxPython sizers. """

__author__      =   "Brian Allen Vanderburg II"
__copyright__   =   "Copyright (C) 2017 Brian Allen Vanderburg II"
__license__     =   "Apache License 2.0"


__all__ = ["SingleItemSizer"]

import wx


class SingleItemSizer(wx.PySizer):
    """
        Represent a box sizer that shows a single item.
        You must call SetSelection after adding items to make it the
        active item.  You can hide all items by calling SetSelection(None),
        however, this will cause any parent sizer mechanism to skip our sizer
        for dimentions.  After calling SetSelection, a call to the containing
        window's Layout should be made to update any positions.
    """

    def __init__(self, *args, **kwargs):
        wx.PySizer.__init__(self, *args, **kwargs)
        self.__selected_item = None

    def _Added(self, item):
        if self.GetItemCount() > 1:
            # Hide all but the first items
            item.Show(False)
        else:
            item.Show(True)
            self.__selected_item = item
        return item

    def Add(self, *args, **kwargs):
        return self._Added(wx.PySizer.Add(self, *args, **kwargs))

    def AddF(self, *args, **kwargs):
        return self._Added(wx.PySizer.AddF(self, *args, **kwargs))

    def Insert(self, *args, **kwargs):
        return self._Added(wx.PySizer.Insert(self, *args, **kwargs))

    def InsertF(self, *args, **kwargs):
        return self._Added(wx.PySizer.InsertF(self, *args, **kwargs))

    def Prepend(self, *args, **kwargs):
        return self._Added(wx.PySizer.Prepend(self, *args, **kwargs))

    def PrependF(self, *args, **kwargs):
        return self._Added(wx.PySizer.PrependF(self, *args, **kwargs))

    def SetSelection(self, item):
        """ Set the selected item and hide all other items. """
        # Hide all items
        self.ShowItems(False)
        
        # Show only the selected item
        if not isinstance(item, wx.SizerItem):
            _item = self.GetItem(item)
        self.__selected_item = _item

        item.Show(True)
            
    def GetSelection(self):
        """ Return the wx.SizerItem of the selected item. """
        return self.__selected_item

    def CalcMin(self):
        """ Calculate the min size of all items. """
        calced = wx.Size(0, 0)
        for item in self.GetChildren():
            calced.IncTo(item.CalcMin())

        return calced

    def RecalcSizes(self):
        """ Set the dimention of the selected item. """
        # We only show the current item's size.
        if not self.__selected_item is None:
            pos = self.GetPosition()
            size = self.GetSize()
            self.__selected_item.SetDimension(pos, size)


