import math
import struct


class Generator:

    
    def __init__(self,name):
        self.BINARY_HEADER = "80sI"
        self.BINARY_FACET = "12fH"
        self.ASCII_FACET = """facet normal  {face[0]:e}  {face[1]:e}  {face[2]:e}
            outer loop
              vertex    {face[3]:e}  {face[4]:e}  {face[5]:e}
              vertex    {face[6]:e}  {face[7]:e}  {face[8]:e}
              vertex    {face[9]:e}  {face[10]:e}  {face[11]:e}
            endloop
          endfacet"""
        self.name = name
        self.faces = []
        self.HEADER = 'solid ' + self.name
        self.FOOTER = 'endsolid ' + self.name
        self.BIN_HEADER_VALUE = b'Created by STL_Writer:( name:'+bytes(self.name,'utf-8')+b' )'
        self.direcs = {
            'Z':(0.,0.,1.),
            '_Z':(0.,0.,-1.),
            'X':(1.,0.,0.),
            '_X':(-1.,0.,0.),
            'Y':(0.,1.,0.),
            '_Y':(0.,-1.,0.),
        }
    

    def _open(self,des,mode='wb'):
        self.des = des
        self.stream = open(self.des, mode)

    def _add_face(self,x,y,z,n):
        n = self.direcs.get(n,n)
        facet = [*n,*x,*y,*z]
        self.faces.append(facet)


    def add_face(self, a, b, c):
        '''
        Creates a face in the form ABC
        use right-hand-thumb rule for finding the normal to the plane
        :param a: the coordinates of point A
        :param b: the coordinates of point B
        :param c: the coordinates of point C
        :return: nothing
        '''
        AB = tuple(i-j for i,j in zip(b,a))
        AC = tuple(i-j for i,j in zip(c,a))
        ABxAC = (AB[1]*AC[2]-AC[1]*AB[2], -AB[0]*AC[2]+AC[0]*AB[2], AB[0]*AC[1]-AC[0]*AB[1])
        modABxAC = math.sqrt(sum([i**2 for i in ABxAC]))
        if(modABxAC==0):
            print(a, b, c)
        n = tuple(i/modABxAC for i in ABxAC)

        self._add_face(a,b,c,n)

    def add_poly_face(self, a, b, c, *args):
        self.add_face(a, b, c)
        l = c
        for i in args:
            self.add_face(l, i, a)
            l = i

    def _close(self):
        self.stream.close()

    def finish(self,ASCII=False):
        if(ASCII==False):
            self.write_STL_binary()
        self._close()

    def write_STL_binary(self):
        cntr = 0

        # Write Header
        self.stream.seek(0)
        self.stream.write(
            struct.pack(self.BINARY_HEADER,self.BIN_HEADER_VALUE,cntr)
        )

        # Write Body
        for facet in self.faces:
            cntr += 1
            self.stream.write(
                struct.pack(self.BINARY_FACET,*facet,0)
            )

        # finishing
        self.stream.seek(0)
        self.stream.write(
            struct.pack(self.BINARY_HEADER,self.BIN_HEADER_VALUE,cntr)
        )


if __name__ == "__main__":
    gen = Generator('cube')
    gen._open('..\models\cube2.stl')

    A = (0., 0., 1.)
    B = (1., 0., 1.)
    C = (1., 0., 0.)
    D = (0., 0., 0.)
    E = (1., 1., 0.)
    F = (1., 1., 1.)
    G = (0., 1., 0.)
    H = (0., 1., 1.)

    gen.add_poly_face(B, A, D, C)
    gen.add_poly_face(E, F, B, C)
    gen.add_poly_face(F, H, A, B)
    gen.add_poly_face(G, E, C, D)
    gen.add_poly_face(H, F, E, G)
    gen.add_poly_face(H, G, D, A)

    gen.finish()

    gen = Generator('difficult_shape')
    gen._open('..\models\difficult_shape.stl')
    A = (3., 0., 0.)
    B = (3., 10., 0.)
    C = (1.5, 12.0, 0.)
    D = (0., 10.0, 0.)
    E = (0., 0., 0.)
    F = (3., 0., 2.)
    G = (3., 10., 2.)
    H = (1.5, 12.0, 2.)
    I = (0., 10.0, 2.)
    J = (0., 0., 2.)

    gen.add_poly_face(J, E, A, F)
    gen.add_poly_face(G, F, A, B)
    gen.add_poly_face(H, G, B, C)
    gen.add_poly_face(I, H, C, D)
    gen.add_poly_face(J, I, D, E)
    gen.add_poly_face(I, J, F, G, H)
    gen.add_poly_face(A, E, D, C, B)

    gen.finish()

