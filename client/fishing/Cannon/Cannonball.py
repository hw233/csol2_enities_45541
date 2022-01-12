# -*- coding:gb18030 -*-

import Math
import BigWorld
from bwdebug import *
from Function import Functor
from ..Elements.Elements import MovableElement
from ..utils import effect
from ..utils.Event import Event
from ..FishingDataMgr import FishingDataMgr

NORMAL_CANNONBALL = 1

CANNONBALL_STYLE = {
	NORMAL_CANNONBALL : {"model":"gw7239", "scale":2.0, "speed":30.0, "normalRange":3, "explodeRange":4.0},
	}

DEFAULT_MODEL = "particles/model/111126_model.model"
DEFAULT_EXPLODE_MODEL = "monster/ty_yuwang/ty_yuwang.model"


class Cannonball( MovableElement ):

	def __init__( self, uid, level, spaceID, firePos, destination ):
		yaw = (destination - firePos).yaw
		cannonballData = FishingDataMgr.instance().getCannonballDataByLevel(level)
		MovableElement.__init__(self, "NPCObject", spaceID, firePos, (yaw, 0, 0),\
			cannonballData["model"], cannonballData["scale"], "cannonball", cannonballData["speed"])
		self._uid = uid
		self._level = level

		self._normalRange = cannonballData["normalRange"]
		self._normalTrapID = 0

		self._exploding = False
		self._normalTravel = destination - firePos
		self._destination = Math.Vector3(destination)

		self.setAutoMove(False)

		if cannonballData["model"] == "":
			self._initDefaultModel()

	@property
	def uid( self ):
		"""��ȡuid"""
		return self._uid

	@property
	def level(self):
		return self._level

	def _initEntity( self, entity ):
		"""��ʼ��entity"""
		MovableElement._initEntity(self, entity)

		cannonballData = FishingDataMgr.instance().getCannonballDataByLevel(self._level)
		eid = cannonballData.get("moveEffect")

		if eid:
			effect.applyEffect(entity.model, eid)

	def _initDefaultModel( self ):
		"""��ʼ��ģ�� For test currently"""
		global DEFAULT_MODEL
		self._loadModelBG(DEFAULT_MODEL, self._onNormalModelLoaded)

	def _loadModelBG( self, model_path, callback ):
		"""���̼߳���ģ��"""
		BigWorld.fetchModel(model_path, Functor(callback, model_path))

	def _onNormalModelLoaded( self, model_path, model ):
		"""��ͨģ�ͼ������"""
		if self.ready() or self.isDestroyed():
			DEBUG_MSG("Load model for Cannonball %i finished, but it is ready or destroyed!" % self._id)
			return

		if model is None:
			ERROR_MSG("Load model for Cannonball %i fail!" % self._id)
			return

		entity = BigWorld.entities.get(self._id)
		if entity:
			entity.model = model
		else:
			self._loadModelBG(model_path, self._onNormalModelLoaded)

	def _onExplosionModelLoaded(self, model_path, model):
		"""��ըģ�ͼ������"""
		if self.isDestroyed():
			DEBUG_MSG("Load model for exploding Cannonball %i finished, but it is destroyed!" % self._id)
			return

		if not self.ready():
			DEBUG_MSG("Load model for exploding of Cannonball %i finished, but it is not ready!" % self._id)
			return

		if model is None:
			ERROR_MSG("Load model for Cannonball %i fail!" % self._id)
			return

		#model.scale = (4,)*3       # ����������Ч��Ҫ��ģ�Ͱ󶨵�entity֮��������
		entity = BigWorld.entities.get(self._id)
		if entity:
			oldModel = entity.model
			entity.model = model
			entity.addModel(oldModel)			# �þ�ģ�ͱ�����inWorld״̬��ȷ����Ч����ͻȻ����

			explodeRange = FishingDataMgr.instance().getCannonballDataByLevel(self._level)["explodeRange"]
			entity.model.scale = (explodeRange,) * 3
			self.flatToPosition(BigWorld.camera().position)
			self.playAction("play1", self.destroy)
		else:
			self._loadModelBG(model_path, self._onExplosionModelLoaded)

	def _reportArrival(self):
		"""���浱ǰλ�� For test"""
		distance = self._destination - self.position()
		if distance.yaw - self._normalTravel.yaw <= 0.001:
			print "--->>> %.3f meters before goal!" % distance.length
		else:
			print "--->>> %.3f meters after goal!" % distance.length
		print "--->>> Nearby to goal: %s" % self._reachGoal()

	def _reachGoal( self ):
		"""�Ƿ񵽴�Ŀ��λ��"""
		return self.position().distTo(self._destination) <= 1.0

	def _firstReachGoal( self ):
		"""�Ƿ��״ε���Ŀ��λ��"""
		return self._normalTrapID == 0 and self._reachGoal()

	def _onMoveOver( self, success ):
		"""�ƶ������ص�"""
		if success:
			# This should never be reach.
			assert 0
		else:
			# �ƶ�ʧ�ܻص���������ֻ��һ��ԭ���趨���ƶ���ʱ����
			# �������
			#self._reportArrival()
			self.normalDetect()

	def _transformFish(self, entity):
		"""���Խ�entityתΪ��"""
		if getattr(entity, "className", "") != "fish":
			return None
		fish = getattr(entity, "script", None)
		if fish is None:
			return None
		if fish.isDead() or fish.isDestroyed() or not fish.ready():
			return None
		return fish

	def _onNormalCollision( self, entities ):
		"""δ��ը֮ǰ����ײ"""
		collideFish = False

		for ent in entities:
			if self._transformFish(ent):
				collideFish = True
				break

		if collideFish:
			self.explode()								# ײ�����˾ͱ�ը
			self._ent.delTrap( self._normalTrapID )

	def moveToDestination(self):
		"""��Ŀ��λ���ƶ�"""
		direction = Math.Vector3(self._normalTravel)
		direction.normalise()
		faceTo = direction.yaw
		forward = self._ent.position + direction * 100000
		timeout = self._normalTravel.length / self._speed

		physics = self._ent.physics
		physics.velocity = direction * self._speed
		physics.setSeekCallBackFn( None )
		physics.seek(tuple(forward) + (faceTo,), timeout, 1000, self._onMoveOver)

	def normalDetect( self ):
		"""��ͨ��ײ���"""
		if self._normalTrapID == 0:
			self._normalTrapID = self._ent.addTrapExt(self._normalRange, self._onNormalCollision)

	def setUid( self, uid ):
		"""����uid"""
		self._uid = uid

	def moving( self ):
		"""�Ƿ������ƶ�"""
		if not self.ready():
			return False
		elif self._ent.physics.seeking:
			return True
		else:
			velocity = self._ent.physics.velocity
			return velocity.x != 0.0 or velocity.y != 0.0 or velocity.z != 0.0

	def exploding(self):
		"""�Ƿ����ڱ�ը"""
		return self._exploding

	def explode( self ):
		"""��ը"""
		if self.isDestroyed() or self.exploding():
			return

		global DEFAULT_EXPLODE_MODEL
		self._exploding = True
		self.setAutoMove(False)

		if self.ready():
			effect.fadeOutModel(self._ent.model, 1.0)
			self.stopMoving()
			self._loadModelBG(DEFAULT_EXPLODE_MODEL, self._onExplosionModelLoaded)
		else:
			DEBUG_MSG("Cannonball %s is not ready when exploding." % self.uid)
			self.destroy()

	def onTick( self, dt ):
		"""Every fishing tick"""
		MovableElement.onTick(self, dt)

		if not self.ready() or self.isDestroyed():
			return

		if self._firstReachGoal():
			#print "----->>> First reach goal!"
			#self._reportArrival()
			self.normalDetect()

		if self._exploding:
			self.flatToPosition(BigWorld.camera().position)
		elif not self.moving():
			self.moveToDestination()


class PassiveCannonball(Cannonball):

	def __init__( self, uid, level, spaceID, firePos, destination ):
		Cannonball.__init__(self, uid, level, spaceID, firePos, destination)
		# ����һ������Զ���λ����ΪĿ��λ�ã����ڵ�һֱ�ɹ�ȥ��ֱ����ը���߷ɳ��泡
		direction = Math.Vector3(self._normalTravel)
		direction.normalise()
		forward = firePos + direction * 10000
		self.setPath((forward,))

	def _onMoveOver( self, success ):
		"""�ƶ������ص�"""
		Cannonball._onMoveOver(self, success)
		print "------>>> passive cannonball move over, result:", success


class ActiveCannonball(Cannonball):

	def __init__( self, uid, level, spaceID, firePos, destination ):
		Cannonball.__init__(self, uid, level, spaceID, firePos, destination)
		cannonballData = FishingDataMgr.instance().getCannonballDataByLevel(level)
		self._explodeRange = cannonballData["explodeRange"]
		self._explodeTrapID = 0
		self._explosionEvent = Event("Explosion")

	@property
	def explosionEvent( self ):
		"""�������¼�"""
		return self._explosionEvent

	def _onExplodeCollision( self, entities ):
		"""��ըʱ����ײ"""
		self._ent.delTrap( self._explodeTrapID )

		fishes = []
		for ent in entities:
			fish = self._transformFish(ent)
			if fish is not None:
				fishes.append(fish)

		self._explosionEvent.trigger(self, fishes)

	def explosionDetect( self ):
		"""��ը��ײ���"""
		if self._explodeTrapID == 0:
			self._explodeTrapID = self._ent.addTrapExt(self._explodeRange, self._onExplodeCollision)
			#print "----->>> %i start explision detection..." % self._id

	def explode( self ):
		"""��ը"""
		if self.isDestroyed() or self.exploding():
			return
		Cannonball.explode( self )
		self.explosionDetect()
