from tkinter import *
import time
import random

class Parking:
    def __init__(self,pos,length,breadth,cvs):
        self.rect=cvs.create_rectangle(pos[0]-length/2,pos[1]-breadth/2,pos[0]+length/2,pos[1]+breadth/2,fill="light grey")
        self.pos=pos
        self.cvs=cvs
        self.length=length
        self.breadth=breadth
        self.symbol=None
        self.vParking=None

    def addSensor(self,sensorSide):
        length=self.length
        breadth=self.breadth
        pos=self.pos
        sensorWidth=length/10
        sensorHt=breadth/4
        if sensorSide=="left":
            self.sensor=self.cvs.create_rectangle(pos[0]-length/2,pos[1]-sensorHt,pos[0]-length/2+sensorWidth,pos[1]+sensorHt,fill="green")
        elif sensorSide=="right":
            self.sensor=self.cvs.create_rectangle(pos[0]+length/2-sensorWidth,pos[1]-sensorHt,pos[0]+length/2,pos[1]+sensorHt,fill="green")
        self.parkingSide=sensorSide
        
    def sensorOn(self):
        self.cvs.itemconfig(self.sensor,fill="red")
        self.makeNotAvailable(self.vParking)

    def sensorOff(self):
        self.cvs.itemconfig(self.sensor,fill="green")
        self.makeAvailable(self.vParking)

    def setParkingColor(self,color):
        self.cvs.itemconfig(self.rect,fill=color)

    def makeNotAvailable(self,parking=None):
        if parking is None:
            parking=self
        parking.symbol=NotAvailableSymbol(parking.pos,parking.breadth/3,parking.cvs)

    def makeAvailable(self,parking=None):
        if parking is None:
            parking=self
        parking.symbol.delete()


class Car:
    def __init__(self,pos,rad,cvs):
        self.rad=rad
        self.pos=pos
        self.spawningPt=[pos[0],pos[1]]
        self.cvs=cvs
        self.color="blue"
        self.isParked=False
        self.movingIn=True
        self.drawCircle()

    sleepVal=0.02
    stepSize=20
    
    def drawCircle(self):
        self.circle=self.cvs.create_oval(self.pos[0]-self.rad, self.pos[1]-self.rad, self.pos[0]+self.rad,self.pos[1]+self.rad, fill=self.color)
        
    def setFill(self,color):
        self.color=color
        self.cvs.itemconfig(self.circle,fill=color)

    def setParking(self,parking):
        self.parking=parking
        if parking.pos[0]-self.spawningPt[0] < 0:
            self.stepSize*=-1

    def moveIn(self):
        x=self.parking.pos[0]
        y=self.parking.pos[1]
            
        while self.pos[1]>y:
            self.cvs.delete(self.circle)
            self.pos[1]+=-abs(self.stepSize)
            self.drawCircle()
            time.sleep(self.sleepVal)
            root.update()

        isSensorOn=False
        if self.stepSize>0:
            while self.pos[0]<x:
                if abs(self.parking.pos[0]-self.pos[0])<=abs(self.stepSize*3) and not isSensorOn:
                    self.parking.sensorOn()
                    isSensorOn=True
                self.cvs.delete(self.circle)
                self.pos[0]+=self.stepSize
                self.drawCircle()
                time.sleep(self.sleepVal)
                root.update()
        else:
            while self.pos[0]>x:
                if abs(self.parking.pos[0]-self.pos[0])<=abs(self.stepSize*3) and not isSensorOn:
                    self.parking.sensorOn()
                    isSensorOn=True
                self.cvs.delete(self.circle)
                self.pos[0]+=self.stepSize
                self.drawCircle()
                time.sleep(self.sleepVal)
                root.update()

    def moveOut(self):
        self.isParked=False
        x=self.spawningPt[0]
        y=self.spawningPt[1]

        self.stepSize*=-1
        if self.stepSize<0:
            while self.pos[0]>=x:
                if self.pos[0]!=self.parking.pos[0]:
                    self.parking.sensorOff()
                self.cvs.delete(self.circle)
                self.pos[0]+=self.stepSize
                self.drawCircle()
                time.sleep(self.sleepVal)
                root.update()
        else:
            while self.pos[0]<=x:
                if self.pos[0]!=self.parking.pos[0]:
                    self.parking.sensorOff()
                self.cvs.delete(self.circle)
                self.pos[0]+=self.stepSize
                self.drawCircle()
                time.sleep(self.sleepVal)
                root.update()

        while self.pos[1]<=y+self.rad*2:
            self.cvs.delete(self.circle)
            self.pos[1]+=abs(self.stepSize)
            self.drawCircle()
            time.sleep(self.sleepVal)
            root.update()
        

class ParkingLot:
    def __init__(self,x1,y1,x2,y2,cvs,phone=None):
        self.cvs=cvs
        self.cvs.focus_set()
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.cvs.create_rectangle(x1,y1,x2,y2,fill="#b3afaf")
        self.gapWidth=10
        self.rows=5
        self.parkings=[] #stores available spots
        self.carsParked=[]

        self.phone=phone
        if phone is not None:
            self.inflatePhone()

    def inflatePhone(self):
        self.phone.pLot.fillWithParkings(toAddSensor=False)
        self.phone.displayAvailable(self.phone.pLot.availableSpots)
            
    def fillWithParkings(self, toAddSensor=True):
        lotLen=self.y2-self.y1
        parkingWidth=(self.x2-self.x1)/3
        parkingHt=(lotLen-(self.rows+1)*self.gapWidth)/self.rows
        x=self.x1+parkingWidth/2
        sensorSide="left"
        counter=0
        for i in range (2):
            for j in range(self.rows):
                y=self.y1+(parkingHt+self.gapWidth)*j+self.gapWidth+(parkingHt/2)
                p=Parking((x,y),parkingWidth,parkingHt,self.cvs)
                if toAddSensor:
                    p.addSensor(sensorSide)
                if self.phone is not None:
                    p.vParking=self.phone.pLot.parkings[counter]
                self.parkings.append(p)
                counter+=1
            x=self.x2-parkingWidth/2
            sensorSide="right"

        self.availableSpots=len(self.parkings)

    def setParkingsColor(self,color):
        for p in self.parkings:
            p.setParkingColor(color)
        
    def bringInCar(self):
        x=self.x1+(self.x2-self.x1)/2
        y=self.y2+10
        if len(self.parkings)!=0:
            p=random.choice(self.parkings)
        else:
            return -1
        car = Car([x,y],self.parkings[0].breadth/3,self.cvs)
        car.setParking(p)
        car.moveIn()
        self.availableSpots-=1
        if self.phone is not None:
            self.phone.displayAvailable(self.availableSpots)
        self.carsParked.append(car)
        self.parkings.remove(p)

    def takeOutCar(self):
        if len(self.carsParked)!=0:
            car=random.choice(self.carsParked)
        else:
            return -1

        self.availableSpots+=1
        if self.phone is not None:
            self.phone.displayAvailable(self.availableSpots)
            
        car.moveOut()
        self.parkings.append(car.parking)
        self.carsParked.remove(car)
        self.cvs.delete(car)

    def startSimulation(self):
        choices=["bringIn","takeOut"]
        while True:
            choice=random.choice(choices)
            if choice=="bringIn":
                status=self.bringInCar()
                if status==-1:
                    time.sleep(random.randrange(2))
                    for i in range(random.randrange(1,len(self.carsParked)+1)):
                        self.takeOutCar()
            elif choice=="takeOut":
                status=self.takeOutCar()
                if status==-1:
                    time.sleep(random.randrange(2))
                    for i in range(random.randrange(1,len(self.parkings)+1)):
                        self.bringInCar()
        
            
class Phone:
    def __init__(self,root):
        self.height=450
        self.width=250
        self.cvs=Canvas(root,bg="white",height=self.height,width=self.width)
        self.cvs.pack(side=RIGHT,padx=100)
        
        notificationBarHt=self.height/17
        self.cvs.create_rectangle(0,0,self.width+10,notificationBarHt,fill="black")
        self.pLot=ParkingLot(self.width/10,notificationBarHt+20,9*self.width/10,4*self.height/5,self.cvs)
        
        now  = time.localtime()
        self.cvs.create_text(9*self.width/10,notificationBarHt/2+2,font="Roboto 10 bold",text=str(now.tm_hour)+":"+str(now.tm_min),fill="white")
        navHt=self.height-(self.height-25)
        nav=self.cvs.create_rectangle(0,self.height-navHt,self.width,self.height,fill="black")
        centrePt=[2.4*self.width/3,self.height-navHt/2]
        side=5
        self.cvs.create_rectangle(centrePt[0]-side,centrePt[1]-side,centrePt[0]+side,centrePt[1]+side,outline="white")
        centrePt=[self.width/2,self.height-navHt/2]
        self.cvs.create_oval(centrePt[0]-side,centrePt[1]-side,centrePt[0]+side,centrePt[1]+side,outline="white")
        centrePt=[self.width/6,self.height-navHt/2]
        polyPts=[centrePt[0]+side,centrePt[1]-side,centrePt[0]-side,centrePt[1],centrePt[0]+side,centrePt[1]+side]
        self.cvs.create_polygon(polyPts,outline="white")
        

    def displayAvailable(self,num):
        self.cvs.delete("availableText")
        self.cvs.create_text(self.width/2,4*self.height/5+30,font="Roboto 20",text="Available : "+str(num),tag="availableText")
        root.update()

class NotAvailableSymbol:
    def __init__(self,pos,rad,cvs):
        self.cvs=cvs
        self.circle=cvs.create_oval(pos[0]-rad,pos[1]-rad,pos[0]+rad,pos[1]+rad,width=2)
        self.line=cvs.create_line(pos[0]-rad,pos[1]-rad,pos[0]+rad,pos[1]+rad, width=2)
        
    def delete(self):
        self.cvs.delete(self.circle)
        self.cvs.delete(self.line)
        root.update() 
        
root=Tk()
ht=550
wdth=800
ground=Canvas(root,bg="white",height=ht,width=wdth)
ground.pack(side=LEFT)
phone=Phone(root)
parkingLot=ParkingLot(0,0,wdth,ht,ground,phone)
#parkingLot=ParkingLot(100,50,700,450,ground,phone)
parkingLot.fillWithParkings()
parkingLot.startSimulation()
root.update()
