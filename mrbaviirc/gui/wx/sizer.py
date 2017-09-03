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

    def SetSelection(self, item):
        """ Set the selected item and hide all other items. """
        # Hide all items
        self.ShowItems(False)
        #for _item in self.GetChildren():
        #    _item.Show(False)
        
        # Show only the selected item
        if item is None:
            self.__selected_item = None
        else:
            _item = self.GetItem(item)
            _item.Show(True)
            self.__selected_item = _item
            #self.Show(_item.GetWindow())
            
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


