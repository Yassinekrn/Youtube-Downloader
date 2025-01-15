import ttkbootstrap as tb
from gui.app import VideoDownloaderApp

def main():
    root = tb.Window(themename="darkly")
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()