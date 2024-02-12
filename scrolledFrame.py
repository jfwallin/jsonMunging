import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

# taken from
# https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame


class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        #theWindow.title("JSON Editor")
        # theWindow.geometry('1000x1100')
        # theWindow.configure(background='white')
        # theFrame = tk.Frame(theWindow, background="#ffffff",
        #                    width=1000, height=1000, padx=15, pady=5)
        # theFrame.pack(fill="both", expand=True, padx=20, pady=20)
        #self.configure(width=1000, height=1000, padx=15, pady=5)
        #self.pack(fill="both", expand=True, padx=20, pady=20)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)

        hscrollbar = ttk.Scrollbar(self, orient=HORIZONTAL)
        hscrollbar.pack(fill=X, side=BOTTOM, expand=FALSE)

        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.configure(width=1900, height=2000, bg="white")
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=20, pady=20)

        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=20, pady=20)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.

        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
            if interior.winfo_reqheight() != canvas.winfo_height():
                # Update the canvas's height to fit the inner frame.
                canvas.config(height=interior.winfo_reqheight())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
            if interior.winfo_reqheight() != canvas.winfo_height():
                # Update the inner frame's height to fill the canvas.
                canvas.itemconfigure(interior_id, height=canvas.winfo_height())
        canvas.bind('<Configure>', _configure_canvas)
