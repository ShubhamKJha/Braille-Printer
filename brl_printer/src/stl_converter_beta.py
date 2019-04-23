
import os
from itertools import product
import struct

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

except ImportError:
    print(DEPENDENCY_MSG +"Error: Requirements unsatisfied")
    exit(0)

DEPENDENCY_MSG = """
This utility has dependencies on the following modules:
* PIL
* Numpy
The unavailibility of these modules would result in termination of program.
"""



BRAILLE_FONT_RES = "../fonts/BRAILLE1.ttf"
OFFSET = 10
BACKGROUND = 255
FOREGROUND = 0
THRESHOLD = 256

ASCII_FACET ="""  facet normal  {face[0]:e}  {face[1]:e}  {face[2]:e}
    outer loop
      vertex    {face[3]:e}  {face[4]:e}  {face[5]:e}
      vertex    {face[6]:e}  {face[7]:e}  {face[8]:e}
      vertex    {face[9]:e}  {face[10]:e}  {face[11]:e}
    endloop
  endfacet"""

BINARY_HEADER = "80sI"
BINARY_FACET = "12fH"
    


def load_braille_font(font_size):
    """
    function: loads the default Braille font provided as \fonts\BRAILLE1.ttf
    input: font_size to be used (default=15)
    output: returns font(ImageFont type) if available
            returns None if font not available
    """
    try:
        fl_res = os.path.join(os.path.dirname(__file__),BRAILLE_FONT_RES)
        fnt = ImageFont.truetype(fl_res,  font_size)
    except OSError:
        print("Error: Font file not loaded")
        return None
    return fnt

def get_size(txt,fnt):
    """
    function: to check the size of text appearing in the picture
    input: text and font
    output: width of text
    """
    testImg = Image.new('L',(1,1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt,fnt)


def convert_text_to_array(txt,size_txt):
    """
    function: converts text into numpy array of size(x,y)
    input: txt => text to be converted to array
           size_txt => size of text required
    output: numpy array of text image(Braille)
    """

    # Loads font
    fnt = load_braille_font(size_txt)
    

    width, _ = get_size(txt, fnt)
    width = width + 2*OFFSET
    height = size_txt + 2*OFFSET
    
    img = Image.new('L',(width,height), color=BACKGROUND) # Creates a white image
    drw = ImageDraw.Draw(img)
    
    drw.text(
        (OFFSET,OFFSET),
        txt,
        font = fnt,
        fill = FOREGROUND)
    
    # DEBUG
    img.show()

    return np.asarray(img,dtype='int32')


def build_ascii_stl(facets):
    """
    function: creates lines for the ASCII stl file
    input: list of facets
    output: list of lines for the file
    """
    res_list = ['solid strip_braille_geom']
    
    for facet in facets:
        res_list.append(ASCII_FACET.format(face=facet))

    res_list.append('endsolid strip_braille_geom')
    
    return res_list

def create_STL_file_binary(facets,dest):
    with open(dest,'wb') as res_file:
        BINARY_HEADER = '80sI'
        BINARY_FACET = '12fH'
        cntr = 0

        # Write Header
        res_file.seek(0)
        res_file.write(struct.pack(BINARY_HEADER, b'Created by STL Converter',cntr))

        # Write Body
        for facet in facets:
            cntr+=1
            res_file.write(struct.pack(BINARY_FACET,*facet,0))
        res_file.seek(0)
        res_file.write(struct.pack(BINARY_HEADER, b'Created by STL Converter',cntr))

def create_STL_file(facets, dest ):
    """
    function: creates the STL file for Braille strip
    input: facet => list of facets, dest => destination for storing STL file
    output: None
    """

    with open(dest,'wb') as res_file:
        res_list = build_ascii_stl(facets)
        res_lines = "\n".join(res_list).encode("UTF-8")
        res_file.write(res_lines)

def numpy2stl2(A, des, rotate=True,min_thickness_percent=0.1,ascii=False):
    """
    function: text2stl => converts text to stl file
    input: text, text_size, des => destination to store file
    output: None
    """

    mask_val = THRESHOLD
    
    m,n = A.shape
    if n >= m and rotate:
        # rotate to best fit a printing platform
        A = np.rot90(A,k=3)
        m,n = n,m

    # Computation for facets
    A = -0.1*A
    facets = []
    
    for i,k in product(range(m-1),range(n-1)):

        x,y = i-m/2. , k-n/2.
        pt = [x,y,A[i,k]]
        tr_pt = [x,y+1,A[i,k+1]]
        bl_pt = [x+1,y,A[i+1,k]]
        br_pt = [x+1,y+1,A[i+1,k+1]]

        n1,n2 = [0]*3,[0]*3

        if(pt[-1]<mask_val and tr_pt[-1]<mask_val and bl_pt[-1]<mask_val):
            facet = n1+tr_pt+pt+br_pt
            facets.append(facet)

        if(pt[-1]<mask_val and br_pt[-1]<mask_val and bl_pt[-1]<mask_val):
            facet = n2+br_pt+pt+bl_pt
            facets.append(facet)
    if(ascii==True):
        create_STL_file(facets,dest)
    else:
        create_STL_file_binary(facets, des)


if __name__ == '__main__':
    import sys
    l = convert_text_to_array("SHUBHAM KUMAR JHA",120)
    numpy2stl2(l,"file1.stl")
