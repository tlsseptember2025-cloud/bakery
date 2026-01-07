def center_window(win, width=800, height=500):
    """
    Centers a Tkinter window on the screen.
    win    : Tk() or Toplevel() window
    width  : window width
    height : window height
    """
    win.update_idletasks()  # ✅ IMPORTANT FIX

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")
