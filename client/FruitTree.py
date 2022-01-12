# -*- coding: gb18030 -*-
#
from bwdebug import *
from NPCObject import NPCObject
import csdefine
import csstatus
import random
import BigWorld
from gbref import rds
import csconst
import time
import event.EventCenter as ECenter
import cschannel_msgs
import Define

from config.item.FruitItems import Datas as FruitItemsDatas
MODEL_SCALE_VALUE = 2.0					# 果树模型成长完全缩放倍数
MODEL_SCALE_DEFAULT_VALUE = 1.0			# 果树默认模型倍数

class FruitTree( NPCObject ):
	"""
	魅力果树
	"""
	def __init__(self):
		"""
		@summary:	初始化
		"""
		NPCObject.__init__( self )
		self.setSelectable( True )
		self.selectable = True
		self.modelNumber = ""		# 模型编号
		self.planterName = ""		# 种植者名字
		self.fruitseedID = 0		# 果树种子ID
		self.growingTime = 0		# 果树成熟所需时间
		self.fruitTreeName = ""		# 果树名字
		self.lastTime = 0			# 果树剩余成熟时间
		self.endTime = 0			# 果树成熟时间
		self.isRipe = False			# 果树是否成熟

	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		return rds.npcModel.getModelSources( self.modelNumber )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld: return
		NPCObject.onCacheCompleted( self )
		self.cell.requestData()

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		NPCObject.leaveWorld( self )
		self.modelNumber = ""
		self.planterName = ""
		self.fruitseedID = 0
		self.growingTime = 0
		self.fruitTreeName = ""
		self.lastTime = 0
		self.endTime = 0
		self.isRipe = False

	def getName( self ):
		"""
		"""
		return self.fruitTreeName

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		"""
		pass

	def createModelBG( self ):
		"""
		"""
		rds.npcModel.createDynamicModelBG( self.modelNumber, self.onModelLoad )

	def onModelLoad( self, model ):
		"""
		模型加载完毕
		"""
		if not self.inWorld: return
		if model is None: return

		self.setModel( model, Define.MODEL_LOAD_ENTER_WORLD )
		self.model.motors = ()
		dscScale = self.model.scale.scale( MODEL_SCALE_VALUE )
		srcScale = self.model.scale.scale( MODEL_SCALE_DEFAULT_VALUE )
		self.lastTime = self.endTime - time.time()
		if self.lastTime > 0:
			self.model.scale = srcScale + srcScale * ( 1 - self.lastTime/self.growingTime )
			rds.effectMgr.scaleModel( self.model, dscScale, self.lastTime/MODEL_SCALE_VALUE )
		else:
			self.model.scale = dscScale
		self.flushAttachments_()

	def onReceiveData( self, modelNumber, planterName, fruitseedID, lastTime ):
		"""
		Define Method
		收到对方的数据
		"""
		self.modelNumber = modelNumber				# 模型编号
		self.planterName = planterName				# 种植者名字
		self.fruitseedID = fruitseedID 				# 果树种子ID
		self.lastTime = lastTime					# 果树剩余成熟时间
		if FruitItemsDatas.has_key( self.fruitseedID ):
			self.growingTime = FruitItemsDatas.get( self.fruitseedID ).get( "time" )
			self.fruitTreeName = FruitItemsDatas.get( self.fruitseedID ).get( "name" )
		if self.lastTime == 0:
			self.isRipe = True
		else:
			self.endTime = time.time() + lastTime	# 估计果树成熟时间
		self.createModelBG()
		ECenter.fireEvent( "EVT_ON_FRUITTREE_BEGIN_COUNTDOWN", self )	# 通知果树头顶名称刷新

	def onReceiveRipeNotice( self, ripeType ):
		"""
		Define Method
		收到服务器传来的果树成长完成消息
		"""
		self.isRipe = True
		if ripeType == csdefine.FRUIT_TREE_RIPE_FAST:
			rds.npcModel.createDynamicModelBG( self.modelNumber, self.onRipeModelLoad )
		ECenter.fireEvent( "EVT_ON_FRUITTREE_RIPE", self )				# 通知果树头顶名称刷新

	def onRipeModelLoad( self, model ):
		"""
		果树成熟模型创建
		"""
		if not self.inWorld: return
		if model is None: return
		if self.model:
			srcScale = self.model.scale
			self.setModel( model )
			self.model.motors = ()
			self.model.scale = srcScale
			dscScale = ( MODEL_SCALE_VALUE, MODEL_SCALE_VALUE, MODEL_SCALE_VALUE )
			rds.effectMgr.scaleModel( self.model, dscScale, 1.0 )
			self.flushAttachments_()

	def onTargetFocus( self ):
		"""
		鼠标移上调用
		"""
		if not self.inWorld: return
		ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		if self.isRipe:
			rds.ccursor.set( "pickup" )

	def onTargetBlur( self ):
		"""
		鼠标移除调用
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		rds.ccursor.set( "normal" )
