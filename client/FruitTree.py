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
MODEL_SCALE_VALUE = 2.0					# ����ģ�ͳɳ���ȫ���ű���
MODEL_SCALE_DEFAULT_VALUE = 1.0			# ����Ĭ��ģ�ͱ���

class FruitTree( NPCObject ):
	"""
	��������
	"""
	def __init__(self):
		"""
		@summary:	��ʼ��
		"""
		NPCObject.__init__( self )
		self.setSelectable( True )
		self.selectable = True
		self.modelNumber = ""		# ģ�ͱ��
		self.planterName = ""		# ��ֲ������
		self.fruitseedID = 0		# ��������ID
		self.growingTime = 0		# ������������ʱ��
		self.fruitTreeName = ""		# ��������
		self.lastTime = 0			# ����ʣ�����ʱ��
		self.endTime = 0			# ��������ʱ��
		self.isRipe = False			# �����Ƿ����

	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		return rds.npcModel.getModelSources( self.modelNumber )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
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
		ģ�ͼ������
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
		�յ��Է�������
		"""
		self.modelNumber = modelNumber				# ģ�ͱ��
		self.planterName = planterName				# ��ֲ������
		self.fruitseedID = fruitseedID 				# ��������ID
		self.lastTime = lastTime					# ����ʣ�����ʱ��
		if FruitItemsDatas.has_key( self.fruitseedID ):
			self.growingTime = FruitItemsDatas.get( self.fruitseedID ).get( "time" )
			self.fruitTreeName = FruitItemsDatas.get( self.fruitseedID ).get( "name" )
		if self.lastTime == 0:
			self.isRipe = True
		else:
			self.endTime = time.time() + lastTime	# ���ƹ�������ʱ��
		self.createModelBG()
		ECenter.fireEvent( "EVT_ON_FRUITTREE_BEGIN_COUNTDOWN", self )	# ֪ͨ����ͷ������ˢ��

	def onReceiveRipeNotice( self, ripeType ):
		"""
		Define Method
		�յ������������Ĺ����ɳ������Ϣ
		"""
		self.isRipe = True
		if ripeType == csdefine.FRUIT_TREE_RIPE_FAST:
			rds.npcModel.createDynamicModelBG( self.modelNumber, self.onRipeModelLoad )
		ECenter.fireEvent( "EVT_ON_FRUITTREE_RIPE", self )				# ֪ͨ����ͷ������ˢ��

	def onRipeModelLoad( self, model ):
		"""
		��������ģ�ʹ���
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
		������ϵ���
		"""
		if not self.inWorld: return
		ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		if self.isRipe:
			rds.ccursor.set( "pickup" )

	def onTargetBlur( self ):
		"""
		����Ƴ�����
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		rds.ccursor.set( "normal" )
