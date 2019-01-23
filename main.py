from PIL import Image
import random as rand
import sys


# Class representing a Circle.
class Circle:
    color = (0,0,0)
    pos = (0,0)
    size = (0,0)

    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color


# Creates a circle with random parameters which fits inside the given 
# width/height.
def random_circle(width, height):
    pos = (int(rand.random() * width), int(rand.random() * height))
    size = (int(rand.random() * (width-pos[0])) , int(rand.random() * (height-pos[1])) )
    color = (int(rand.random() * 255), int(rand.random() * 255), int(rand.random() * 255))
    
    circle = Circle(pos, size, color)

    return circle


# Draws the circle to the image, pixel for pixel.
def draw_circle(circle, image):
    for y in range(circle.pos[1]):
        for x in range(circle.pos[0]):
            image[y][x] = "#ff00ee" #(0,255,255)


# Approximates an image through the use of a coloring strategy.
# The coloring strategy takes a group of pixels and returns 
def approximate_image(image_name):
    image = Image.open(image_name)
    pix = image.load()

    for i in range(10):
        print("Whait\n")
        circle = random_circle(500, 500)
        #draw_circle(circle, pix)

    return image


# Print program usage.
def printUsage():
    print("Usage: python main.py IMAGE\n")

# 
if __name__ == '__main__':
    print("what the hell is goin on?")
    if len(sys.argv) == 2:
        approximation = approximate_image(sys.argv[1])
        approximation.save("new.jpg")
    else:
        printUsage()
