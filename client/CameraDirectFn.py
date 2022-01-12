from bwdebug import *
import BigWorld
import Math
import time
import copy
import math
import ResMgr
import Define
import pickle
import csol
import CamerasMgr
import CameraEventMgr
import csarithmetic
import SkillTargetObjImpl
from gbref import rds
from Function import Functor
import event.EventCenter as ECenter
from guis.ScreenViewer import ScreenViewer

def SetFreeCamera(pos, direct):
    dpos = Math.Vector3(pos)
    ddir = Math.Vector3(direct)
    camera = BigWorld.FreeCamera()
    ma = Math.Matrix()
    ma.setTranslate(dpos * -1.0)
    camera.set(ma)
    BigWorld.camera(camera)
def ResetPlayerCamera():
    rds.worldCamHandler.use()

def GetFlyCameraShellPitch(yaw, pitch, pos):
    camera = CamerasMgr.FlyCameraShell()
    camera.camera.positionAcceleration = 0.0
    camera.camera.trackingAcceleration = 0.0
    #camera._FlyCameraShell__actualRadius = 0.001
    ma = Math.Matrix()
    ma.setTranslate(pos)
    camera.setMatrixTarget(ma)
    camera.setYaw(yaw, True)
    
    tpitch = 0.0
    tl = {}
    il = []
    ra = 480
    ft = float(ra)/5.0
    for i in range(ra):
        tpitch = 0.0
        tpitch = tpitch +  i * 0.314/ft
        camera.setPitch( math.pi - tpitch, True)
        camera.camera.update(1)
        ret2 = Math.Matrix(camera.camera_.matrix).pitch
        tl[ret2] = tpitch
        il.append(ret2)
    for i in range(ra):
        tpitch = 0.0
        tpitch = tpitch -  i * 0.314/ft
        camera.setPitch( math.pi - tpitch, True)
        camera.camera.update(1)
        ret2 = Math.Matrix(camera.camera_.matrix).pitch
        tl[ret2] = tpitch
        il.append(ret2)
    il.sort()
    for i in range(len(il)):
        if i == 0:
            continue
        if il[i] > pitch and il[i - 1]  < pitch:
            return  tl[il[i - 1]]
    return pitch

def GetFlyCameraShellYaw():
    yaw   =  Math.Matrix(BigWorld.camera().matrix).yaw
    pitch =  Math.Matrix(BigWorld.camera().matrix).pitch
    camera = CamerasMgr.FlyCameraShell()
    camera.camera.positionAcceleration = 0.0
    camera.camera.trackingAcceleration = 0.0
    ma = Math.Matrix()
    camera.setMatrixTarget(ma)
    camera.setYaw(math.pi-yaw, True)
    camera.setPitch(pitch, True)
    camera.camera.update(90)
    return yaw,Math.Matrix(camera.camera.matrix).yaw

def GetFlyCameraShellPosition():
    yaw   =  Math.Matrix(BigWorld.camera().matrix).yaw
    pitch =  Math.Matrix(BigWorld.camera().matrix).pitch
    pos   =  BigWorld.camera().position
    pitch1 = GetFlyCameraShellPitch(yaw, pitch, pos)
   
    camera = CamerasMgr.FlyCameraShell()
    camera.camera.positionAcceleration = 0.0
    camera.camera.trackingAcceleration = 0.0

    ma = Math.Matrix()
    camera.setMatrixTarget(ma)
    camera.setYaw(math.pi-yaw, True)
    camera.setPitch(pitch1, True)
    camera.camera.update(90)

    pos1 = pos - camera.camera.position
    ma.setTranslate(pos - camera.camera.position)
    camera.camera.update(90), math.pi-yaw, pitch1
    return "%.4f,%.4f,%.4f,%.4f,%.4f" % (pos1[0], pos1[1], pos1[2], yaw, pitch1)

def SaveFlyPoint(path = ""):
    cfile = rds.cameraFlyMgr.confpath
    if path != "":
        cfile = path
    sec = ResMgr.openSection(cfile, 1)
    for key in sec.keys():
        sec.deleteSection(key)
    for datas in rds.cameraFlyMgr.posDatas:
        row  = sec.createSection('row')
        row.writeVector3("firstPos", datas[0])
        row.writeVector3("controlPos1", datas[1])
        row.writeVector3("controlPos2", datas[2])
        row.writeVector3("endPos", datas[3])
        row.writeVector3("firstRotate", datas[6])
        row.writeVector3("endRotate", datas[7])
        row.writeFloat("startTime", datas[4])
        row.writeFloat("startRunTime", datas[8])
        row.writeFloat("endTime", datas[5])
    
    for item in rds.cameraFlyMgr.eventInfo:
        row = sec.child(0).createSection('events')
        row.writeFloat("startTime", item[0])
        row.writeString("param", str(item[1])[1:-1].replace(",", ";"))
    sec.save()

def PickleGetEventDatas():
    return pickle.dumps(rds.cameraFlyMgr.eventInfo)

def PickleSetEventDatas(data):
    ldata = pickle.loads(data)
    for item in ldata:
        item.append(0)
    rds.cameraFlyMgr.eventInfo = ldata

def ClearFlyCcourse():
    csol.DCameraClearPoint()

def DrawrFlyCcourse():
    csol.DCameraClearPoint()
    for data in rds.cameraFlyMgr.posDatas:
        csol.DCameraAddPoint(data[0])
    csol.DCameraAddPoint(rds.cameraFlyMgr.posDatas[-1][3])

def DrawrFlyCtrlCcourse():
    csol.DCameraClearPoint()
    for data in rds.cameraFlyMgr.posDatas:
        csol.DCameraAddPoint(data[1])
        csol.DCameraAddPoint(data[2])

def PickleGetDatas():
    poslist = []
    for items in rds.cameraFlyMgr.posDatas:
        datas = []
        for data in items:
            if isinstance(data, Math.Vector3):
                datas.append(tuple(data))
            else:
                datas.append(data)
        poslist.append(datas)

    return pickle.dumps(poslist)

def PickleSetDatas(data):
    lists   = pickle.loads(data)
    poslist = []
    for items in lists:
        datas = []
        for data in items:
            if isinstance(data, tuple):
                datas.append(Math.Vector3(data))
            else:
                datas.append(data)
        poslist.append(datas)
    rds.cameraFlyMgr.posDatas = poslist
