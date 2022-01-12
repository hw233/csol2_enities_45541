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

g_mlMgr = ModelLoaderMgr.instance()      # ΢��ģ����Դ���ع�����

class MonsterBuilding( Monster ):
	def __init__( self ):
		Monster.__init__( self )
		self.collideModel = None
		self.isCollide = False
	
	def moveToPosFC( self, pos, speed, dir ):
		"""
		define method
		������֪ͨ�ƶ���ĳ��
		"""
		pass
		
	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		# Action Match
		if not hasattr( self, "am" ) or self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# ģ�͵�RolePitchYaw��Entity����һ��
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0
			# ģ�͵�����������
			self.am.boredNotifier = self.onBored
			self.am.patience = random.random() * 6 + 6.0
			self.am.fuse = random.random() * 6 + 6.0
			self.setArmCaps()
		# ΢��ģ��Ԥ���ش���
		modelSourceList = rds.npcModel.getModelSources( self.modelNumber )
		if modelSourceList:
			modelSource = modelSourceList[0]
		if len( modelSourceList ) == 1 and "avatar" not in modelSource :
			g_mlMgr.getSource( modelSource, self.id )
		self.isLoadModel = True
		self.delayActionNames = []   #�ı�ģ���зż��ܵ�ʩ������
		self.delayCastEffects = []     #�ı�ģ���м��ܵ�ʩ����Ч
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
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
		������ײ
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
		�����Ƿ�ر���ײ
		"""
		if Flag:
			self.delModel( self.collideModel )
			self.collideModel = None
		self.isCollide = Flag
	
	def distanceBB( self, destEntity ):
		"""
		������Ŀ��entity��boundingbox�߽�֮���3D����ϵ�ľ���
		��д��Ϊ�˿��ǳ�������
		@return: float
		"""
		# ��ǰֱ����bounding box�Ŀ��һ����Ϊbounding box�����ĵ��߽�ľ���
		s1 = self.getBoundingBox().z / 2
		s2 = self.getBoundingBox().x / 2
		off_A = math.atan(s2/s1)
		off_dis = s2 / math.sin(off_A)
		d1 = destEntity.getBoundingBox().z / 2
		yaw1 = self.yaw
		yaw2 = ( self.position - destEntity.position ).yaw
		disYaw = abs( yaw1 - yaw2 )
		if disYaw + off_A >=  math.pi*2: #�ڵ�һ������ 
			disYaw = disYaw - math.pi*2
		disYaw = abs( disYaw )
		if  0 <= disYaw <= off_A or  math.pi - off_A <= disYaw <= math.pi + off_A: #����
			dis =  s1 / abs( math.cos( disYaw ) )
		else: #����
			dis =  s2 / abs( math.sin( disYaw-math.pi ) )
		if dis >= off_dis:
			dis = off_dis
		return self.position.distTo( destEntity.position ) - dis - d1