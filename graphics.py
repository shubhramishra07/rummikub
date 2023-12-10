import tkinter as tk
from PIL import Image, ImageTk
import os

class Tile:
    def __init__(self, color, number):
        self.color = color
        self.number = number

def drag_start(event):
    widget = event.widget
    widget.startX = event.x
    widget.startY = event.y

def drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget.startX + event.x
    y = widget.winfo_y() - widget.startY + event.y
    widget.place(x=x, y=y)

def resize_image(image_path, width, height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(resized_image)

def create_new_label(root, image, tile, tiles):
    label = tk.Label(root, image=image)
    label.grid(row=0, column=tiles.index(tile), padx=10, pady=10)
    label.bind("<Button-1>", drag_start)
    label.bind("<B1-Motion>", drag_motion)
    return label
    
def main(tiles):
    root = tk.Tk()
    root.geometry("1000x700")
    root.title("Rummikub")

    # Set the desired width and height
    new_width = 53
    new_height = 76
    
    


    imgs = []
    for tile in tiles:
        # Replace 'your_image.jpg' with the path to your image file
        img_path = f"/{tile.color}-{tile.number}.png"
        path = os.getcwd() + "/assets" + img_path

        # Resize the image
        resized_image = resize_image(path, new_width, new_height)
        imgs.append(resized_image)
        create_new_label(root, resized_image, tile, tiles)
        #tk.Label(root, image=imgs[-1], width=new_width, height=new_height).grid()
        # Create a label to display the resized image
        #labels.append(create_new_label(root, resized_image, tile, tiles))

    root.mainloop()

if __name__ == "__main__":
    tiles = [Tile("red", 1), Tile("blue", 2), Tile("green", 3)]  # Replace with your tile data
    main(tiles)
