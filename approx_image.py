from PIL import Image
import pdb
import random as rand
import sys
import math

# TODO: Display every n'th iteration of the approximation.
# TODO: Other methods/shapes for approximation (Shape interface).
# TODO: Concurrency/optimization/faster approximation/implement in CUDA/OpenAL.
# TODO: Floodfill empty space filling algorithm insidead of current method.
# TODO: Combine my other image processing projects into a single module.
# Refactor common parts.


class Ellipse:
    """
    Class representing an Ellipse.
    """

    color = (0,0,0)
    pos = (0,0)
    size = (0,0)

    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color

    def __str__(self):
        return "Ellipse [pos:"+self.pos.__str__()+ \
               ", size:"+self.size.__str__()+", \
               color:"+self.color.__str__()+"]"


def random_ellipse(width, height, el_size):
    """
    Randomly creates an ellipse with which fits inside the given width/height
    and is at a maximum size of el_size.

    Args:
    width (int) - width in pixels.
    height (int) - height in pixels.
    el_size {tuple(int,int)} - Maximum possible size for generated ellipse.
    """

    size = (int(rand.random()*el_size[0]), int(rand.random()*el_size[1]))
    pos = (int(rand.random() * (width - size[0])), int(rand.random() * (height - size[1])))

    #size = (int(rand.random() * (width-pos[0])), \
    #        int(rand.random() * (height-pos[1])) )

    color = (int(rand.random() * 255), \
             int(rand.random() * 255), \
             int(rand.random() * 255))
    
    ellipse = Ellipse(pos, size, color)

    return ellipse


def fill_ellipse(ellipse, x, y, image):
    """
    Merges the ellipse color with the color of the image pixel.

    Args:
    ellipse {Ellipse} - The ellipse area to fill in image.
    x {int} - Pixel X coordinate.
    y {int} - Pixel Y coordinate.
    image {PIL::PixelAccess} - Image pixels to sample pixel color from.
    """
    combined = tuple([int((ellipse.color[0] + image[x,y][0])/2),
                     int((ellipse.color[1] + image[x,y][1])/2),
                     int((ellipse.color[2] + image[x,y][2])/2)] )
    return combined


def avg_color(ellipse, image, canvas):
    """
    Calculates average color of pixels inside ellipse and appends it at the
    canvas pixel index.

    Args:
    ellipse {Ellipse} - The ellipse to use for drawing.
    image {PIL::PixelAccess} - Pixels of image.
    canvas {3D list of colors} - A list of colors for each pixel, indexed like
    [x][y] => colors at that pixel.
    """
    avg = (0,0,0)
    i = 0

    if ellipse.size[0] == 0 or ellipse.size[1] == 0:
        return None

    for y in range(ellipse.pos[1], ellipse.pos[1] + ellipse.size[1]):
        for x in range(ellipse.pos[0], ellipse.pos[0] + ellipse.size[0]):

            if inside_ellipse(ellipse, x, y):
                i += 1
                avg = tuple([avg[0]+image[x,y][0], \
                             avg[1]+image[x,y][1], \
                             avg[2]+image[x,y][2]])
    if i == 0:
        return None

    avg = tuple([int(avg[0]/i), int(avg[1]/i), int(avg[2]/i)])

    for y in range(ellipse.pos[1], ellipse.pos[1] + ellipse.size[1]):
        for x in range(ellipse.pos[0], ellipse.pos[0] + ellipse.size[0]):
            if inside_ellipse(ellipse, x, y):
                canvas[x][y].append(avg)


def merge_colors(image, colors):
    """
    Evenly merges the colors at each pixel location and adds it to the image.

    Args:
    image {PIL::PixelAccess} - The pixels of the image to merge to.
    colors {3D list of colors at [x][y] index} - The colors at each pixel.
    """

    pix = image.load()

    for y in range(image.size[1]):
        derp = [] #colors[x][y]
        prev_col = None

        for x in range(image.size[0]):
            if len(colors[x][y]) > 0:
                tot_col = (0,0,0)
                for col in colors[x][y]:
                    tot_col = tuple([tot_col[0]+col[0],\
                                     tot_col[1]+col[1],\
                                     tot_col[2]+col[2]])

            
                tot_col = tuple([int(tot_col[0]/len(colors[x][y])),\
                                 int(tot_col[1]/len(colors[x][y])),\
                                 int(tot_col[2]/len(colors[x][y]))])

                pix[x,y] = tot_col
                prev_col = pix[x,y]
                if len(derp) > 0:
                    for xx,yy in derp:
                        pix[xx,yy] = tot_col
                    derp.clear()
            else:
                if prev_col != None:
                    pix[x,y] = prev_col
                else:
                    derp.append(tuple([x,y]))


def inside_ellipse(ellipse, x, y):
    """
    Tests if point (x,y) is inside the ellipse.
    ellipse (Custom Ellipse object) - The ellipse to test against.
    
    Args:
    ellipse {Custom Ellipse object} - The ellipse to check against.
    x {int} - Point X coordinate.
    y {int} - Point Y coordinate.
    """
    a = ellipse.size[0] / 2 # Half ellipse width.
    b = ellipse.size[1] / 2 # Half ellipse height.

    xx = x-ellipse.pos[0]-a # x expressed relative to ellipse center.
    yy = y-ellipse.pos[1]-b # y expressed relative to ellipse center.
        
    # Test to determine if (x,y) is inside ellipse or outside.
    test = pow(b,2) * pow(xx,2) + \
           pow(a,2) * pow(yy,2) - \
           pow(b,2) * pow(a,2)

    return test <= 0 # Point is inside ellipse if True.


def approximate_image(image_old, iters, size, gen_strat=random_ellipse):
    """
    Approximates an image through the use of a coloring strategy.
    The coloring strategy takes a group of pixels and returns 

    Args:
    image_old - PIL Image object to approximate.
    size {tuple(int,int)} - Size of ellipses to generate.
    iters {int} - Iterations to run strategy
    gen_strat {tuple(int, int)} - Approximation strategy function which takes 
    parameters image width/height.
    Returns: {PIL::Image}- The image approximation.
    """

    image_new = Image.new("RGBA", image.size, None)
    pix = image.load()

    print("Image: ["+image.size.__str__()+"]")

    # Pixel color object used for merging. (REVERSE ORDER so indexed
    # canvas[x][y] instead iof canvas[y][x].
    canvas = [ [ [] for _ in range(image.size[1]) ] for _ in range(image.size[0]) ]

    for i in range(iters):
        ellipse = random_ellipse(image.size[0], image.size[1], size)
        avg_color(ellipse, pix, canvas)

    merge_colors(image_new, canvas)

    return image_new


def printUsage():
    """ 
    Prints program usage.
    """
    print("Usage: python approx_image.py IMAGE ITERATIONS ELLIPSE_WIDTH \
    ELLIPSE_HEIGHT \n")


if __name__ == '__main__':
    if len(sys.argv) == 5:
        image = Image.open(sys.argv[1])

        width = int(sys.argv[3])
        height = int(sys.argv[4])
        size = tuple([width,height])

        new_image = approximate_image(image, int(sys.argv[2]), size)
        new_image.save("new4.png")
    else:
        printUsage()
