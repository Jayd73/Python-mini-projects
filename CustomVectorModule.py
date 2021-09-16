import re
import math
import copy

class Vector:
    def __init__(self, comp):
        self.comp=comp

    def toString(self):
        vectStr=''
        for cnt in range (len(self.comp)):
            vectStr+='+('+str(round(self.comp[cnt],3))+')'+chr(117+cnt) #ascii code for 'u'
        return vectStr

    def scale(self, scalar):
        for i in range (len(self.comp)):
            self.comp[i]*=scalar
        return self

    def scale2D(self, scalarX, scalarY):
        self.comp[0]*=scalarX
        self.comp[1]*=scalarY

    def scaleX(self, scalarX):
        self.comp[0]*=scalarX

    def scaleY(self, scalarY):
        self.comp[1]*=scalarY

    def getAdd(self, vect):
        comp=[]
        for i in range(len(self.comp)):
            comp.append(self.comp[i]+vect.comp[i])

        return Vector(comp)

    def add(self, vect):
        for i in range(len(self.comp)):
            self.comp[i]+=vect.comp[i]

    def sub(self, vect):
        for i in range(len(self.comp)):
            self.comp[i]-=vect.comp[i]

    def getSub (self, vect):
        comp=[]
        for i in range(len(self.comp)):
            comp.append(self.comp[i]-vect.comp[i])

        return Vector(comp)
            
    def getDotProduct(self,vect):
        if len(self.comp)==len(vect.comp):
            prod=0
            for i in range (len(self.comp)):
                prod+=self.comp[i]*vect.comp[i]

            return prod
        else:
            print("number of dimensions are not equal")

    def getMagnitude(self):
        compSum=0
        for comp in self.comp:
            compSum+=comp**2
        return math.sqrt(compSum)

    def getDist(self, vect):
        compSum=0
        for i in range (len(self.comp)):
            compSum+=math.pow((self.comp[i]-vect.comp[i]),2)
            
        return math.sqrt(compSum)

    def getAng2D(self, vect):
        ang = math.atan2(vect.getY(), vect.getX()) - math.atan2(self.getY(), self.getX())
        return round(ang,3)

    def getRotatedBy2D(self, ang):
        ang = math.radians(ang)
        cos_ang = math.cos(ang);
        sin_ang = math.sin(ang);
        return Vector([self.getX() * cos_ang - self.getY() * sin_ang, self.getX() * sin_ang + self.getY() * cos_ang])

    def rotate2D(self, ang):
        ang = math.radians(ang)
        cos_ang = math.cos(ang);
        sin_ang = math.sin(ang);
        x = self.getX() * cos_ang - self.getY() * sin_ang;
        y = self.getX() * sin_ang + self.getY() * cos_ang;
        self.comp[0] = x
        self.comp[1] = y

    def getScaled(self, scalar):
        comp=[]
        for i in range (len(self.comp)):
            comp.append(self.comp[i]*scalar)
        return Vector(comp)

    def getProjOn(self,vect):
        dotProd = self.getDotProduct(vect)
        lenSqr = vect.getMagnitude()**2
        scalar=dotProd/lenSqr
        return Vector(vect.scale(scalar).comp)

    def getOrthogonalInSamePlane(self,vect1,vect2,scalar2=1):     
        scalar1= -scalar2*vect2.getDotProduct(vect1)/vect2.getDotProduct(vect2)
        orthogonalVect = vect1.getScaled(scalar1).getAdd(vect2.getScaled(scalar2))
        return orthogonalVect

    def normalize(self):
        mag = self.getMagnitude()
        self.scale(1/mag)
        
    def limit(self, maxMag):
        compSum=0
        for comp in self.comp:
            compSum+=comp**2
        if compSum > maxMag*maxMag:
            self.normalize()
            self.scale(maxMag)

    def getPerpendicularVect2D(self):
        return Vector([self.getY(), -self.getX()])

    def setMagnitude(self, magnitude):
        self.scale(magnitude / self.getMagnitude());

    def getClone(self):
        return Vector(copy.deepcopy(self.comp))

    def getX(self):
        return self.comp[0]

    def getY(self):
        return self.comp[1]

    def setX(self, x):
        self.comp[0] = x

    def setY(self, y):
        self.comp[1] = y

    def set2D(self, x, y):
        self.comp[0] = x
        self.comp[1] = y

    def setVect2D(self,vect):
        self.set2D(vect.getX(), vect.getY())

        