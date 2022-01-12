# -*- coding:gb18030 -*-

#进入渔场（开始捕鱼）：
#BigWorld.entities[BigWorld.globalData["FishingJoyMgr"].id].enterRoom( player.getName(), player, 1 )
#离开：
#BigWorld.entities[BigWorld.globalData["FishingJoyMgr"].id].leaveRoom( player.id )

import Define
import Time
import BigWorld
import math
import FishingConsole
import CamerasMgr
import FishingCamera
import FishingEngine
import FishingGround
import FishingStatus
import FishingDefine
import FishingDataMgr
from Elements import Elements
from Fish import Fish
from utils import Event
from utils import util
from utils import effect
from Cannon import Cannon
from Cannon import Cannonball
from Cannon import Battery
from Reward import Money
from Reward import Card
from gbref import rds
import event.EventCenter as ECenter

__all__ = ("testFishing",)


def replaceFish( fish ):
	if fish:
		fish.stop()
		fish._mainwin.dispose()
	reload(Elements)
	reload(Fish)
	reload(FishingConsole)
	fc = FishingConsole.FishingConsole()
	return fc

def calcToRadian( src, dst ):
	k = (dst[1] - src[1])/(dst[0] - src[0])		# 求斜率
	return math.atan(k)							# 根据斜率计算x轴到直线的角: tan(x) = (k2 - k1)/(1 + k2*k1)，x轴的斜率是零

def testCamera( cam ):
	if cam:
		cam.recoverToPreviousCamera()
	reload(CamerasMgr)
	reload(FishingCamera)
	cam = FishingCamera.FishingCamera()
	cam.init(BigWorld.PlayerMatrix(), (0, -math.pi/2.001, 0), 15)
	return cam

def testFish( fish, style ):
	if fish:
		fish.destroy()

	reload(FishingDataMgr)
	reload(Elements)
	reload(Fish)
	FishingDataMgr.FishingDataMgr.instance().loadFishData("config/client/fishing/fishes.xml")
	p = BigWorld.player()
	fish = Fish.Fish(0, style, p.spaceID, Time.Time.time(), (p.yaw,0,0), [p.position])
	return fish

def testCannon( cannon ):
	if cannon:
		cannon.destroy()
	reload(Event)
	reload(Elements)
	reload(Cannonball)
	reload(Cannon)
	p = BigWorld.player()
	cannon = Cannon.Cannon(p.spaceID, p.position, (p.yaw, p.pitch, p.roll), 1)
	return cannon

def testFishingEngine( engine ):
	if engine:
		engine.stop()
		engine.release()
	reload(FishingDataMgr)
	reload(util)
	reload(FishingDefine)
	reload(Event)
	reload(Elements)
	reload(Money)
	reload(Card)
	reload(Fish)
	reload(Cannonball)
	reload(Cannon)
	reload(Battery)
	reload(CamerasMgr)
	reload(FishingCamera)
	reload(FishingGround)
	reload(FishingConsole)
	reload(FishingEngine)
	engine = FishingEngine.FishingEngine()
	engine.init()
	engine.start()
	return engine

def testFishingStatus():
	subStatus = rds.statusMgr.statusObjs[Define.GST_IN_WORLD]._BaseStatus__subStatus
	if subStatus:
		subStatus.onLeave(None)
		rds.statusMgr.statusObjs[Define.GST_IN_WORLD]._BaseStatus__subStatus = None
	reload(FishingDataMgr)
	reload(effect)
	reload(util)
	reload(FishingDefine)
	reload(Event)
	reload(Elements)
	reload(Money)
	reload(Card)
	reload(Fish)
	reload(Cannonball)
	reload(Cannon)
	reload(Battery)
	reload(CamerasMgr)
	reload(FishingCamera)
	reload(FishingGround)
	reload(FishingConsole)
	reload(FishingEngine)
	reload(FishingStatus)
	status = FishingStatus.FishingStatus()
	rds.statusMgr.setToSubStatus(Define.GST_IN_WORLD, status)
	return status

# global fishing engine instance
g_fishing = None

def testFishing():
	global g_fishing
	g_fishing = testFishingStatus()
	ECenter.fireEvent("EVT_FISHING_ON_ADD_FISHER", BigWorld.player().id, 1)


def release():
	rds.statusMgr.leaveSubStatus(Define.GST_IN_WORLD, FishingStatus.FishingStatus)


def setBulletNumber(number):
	global g_fishing
	if g_fishing:
		g_fishing.fishingConsole._fishpond._batteries[BigWorld.player().id]._fireCounter = number


def getBulletNumber():
	global g_fishing
	if g_fishing:
		return g_fishing.fishingConsole._fishpond._batteries[BigWorld.player().id]._fireCounter
	return None


def getPlayerFishing():
	return rds.statusMgr.statusObjs[Define.GST_IN_WORLD]._BaseStatus__subStatus


def reloadPlayerFishing():
	currStatus = getPlayerFishing()
	batteries = []
	if currStatus:
		for fisherID, battery in currStatus.fishingConsole._fishpond._batteries.items():
			batteries.append((fisherID, battery.number, getattr(battery, "_fireCounter", 0)))

	global g_fishing
	g_fishing = testFishingStatus()
	player = BigWorld.player()
	from SmartReload import reloadMethod
	reloadMethod(player, "leaveFishing", "Fisher")
	reloadMethod(player, "enterFishing", "Fisher")
	reloadMethod(player, "detectToEnterFishing", "Fisher")
	reloadMethod(player, "fish_enterSpace", "Fisher")
	reloadMethod(player, "fish_leaveSpace", "Fisher")

	for fisherID, batteryNumber, fireCounter in batteries:
		ECenter.fireEvent("EVT_FISHING_ON_ADD_FISHER", fisherID, batteryNumber)
		if fisherID == player.id:
			if batteryNumber == 0 or batteryNumber == 3:
				ECenter.fireEvent("EVT_ON_ENTER_FISHING", "LEFT_STYLE")
			else:
				ECenter.fireEvent("EVT_ON_ENTER_FISHING", "RIGHT_STYLE")

			setBulletNumber(fireCounter)
