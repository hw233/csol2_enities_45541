# -*- coding: gb18030 -*-

from Monster import Monster
import csdefine
from bwdebug import *
import Define
from gbref import rds
from Function import Functor
import Const
import Math
import utils
import random
import math
from ModelLoaderMgr import ModelLoaderMgr

g_mlMgr = ModelLoaderMgr.instance()      # 微端模型资源下载管理器

class MonsterBuilding( Monster ):
	def __init__( self ):
		Monster.__init__( self )
		self.collideModel = None
		self.isCollide = False
	
	def moveToPosFC( self, pos, speed, dir ):
		"""
		define method
		服务器通知移动到某点
		"""
		pass
		
	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型
		继承 NPCObject.createModel
		"""
		# Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# 模型的RolePitchYaw和Entity保持一致
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			# 模型的随机动作相关
			self.am.boredNotifier = self.onBored
			self.am.patience = random.random() * 6 + 6.0
			self.am.fuse = random.random() * 6 + 6.0
			self.setArmCaps()
		# 微端模型预加载处理
		modelSourceList = rds.npcModel.getModelSources( self.modelNumber )
		if modelSourceList:
			modelSource = modelSourceList[0]
		if len( modelSourceList ) == 1 and "avatar" not in modelSource :
			g_mlMgr.getSource( modelSource, self.id )
		self.isLoadModel = True
		self.delayActionNames = []   #改变模型中放技能的施法动作
		self.delayCastEffects = []     #改变模型中技能的施法光效
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.setModel( model, event )
		self.updateVisibility()
		self.flushAttachments_()
		self.isLoadModel = False
		if self.firstHide:
			self.playStandbyAction()
		if self.delayActionNames:
			rds.actionMgr.playActions( self.getModel(), self.delayActionNames )
		for cb in self.delayCastEffects:
			if callable( cb ):
				cb()
		self.openCollide(  )
	
	def openCollide( self ):
		"""
		开启碰撞
		"""
		if self.isCollide: return
		if self.collideModel:
			self.delModel( self.collideModel )
		model = self.getModel()
		if not model: return
		pyStaticModel = rds.npcModel.createStaticModel( self.modelNumber, model.matrix, True )
		pyStaticModel.visible = False
		self.addModel( pyStaticModel )
		self.collideModel = pyStaticModel
	
	def isCloseCollide( self, Flag ):
		"""
		设置是否关闭碰撞
		"""
		if Flag:
			self.delModel( self.collideModel )
			self.collideModel = None
		self.isCollide = Flag
	
	def distanceBB( self, destEntity ):
		"""
		计算与目标entity的boundingbox边界之间的3D坐标系的距离
		重写是为了考虑朝向因素
		@return: float
		"""
		# 当前直接以bounding box的宽的一半作为bounding box的中心到边界的距离
		s1 = self.getBoundingBox().z / 2
		s2 = self.getBoundingBox().x / 2
		off_A = math.atan(s2/s1)
		off_dis = s2 / math.sin(off_A)
		d1 = destEntity.getBoundingBox().z / 2
		yaw1 = self.yaw
		yaw2 = ( self.position - destEntity.position ).yaw
		disYaw = abs( yaw1 - yaw2 )
		if disYaw + off_A >=  math.pi*2: #在第一象限内 
			disYaw = disYaw - math.pi*2
		disYaw = abs( disYaw )
		if  0 <= disYaw <= off_A or  math.pi - off_A <= disYaw <= math.pi + off_A: #正面
			dis =  s1 / abs( math.cos( disYaw ) )
		else: #侧面
			dis =  s2 / abs( math.sin( disYaw-math.pi ) )
		if dis >= off_dis:
			dis = off_dis
		return self.position.distTo( destEntity.position ) - dis - d1