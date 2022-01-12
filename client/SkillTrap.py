# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq
from Function import Functor

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from gbref import rds
import csdefine
import Define


class SkillTrap( NPCObject, CombatUnit ):
	"""
	��������
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.selectable = False		# ����ѡ��
		self.entityList = []
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]
	
	def onCacheCompleted( self ):
		NPCObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )
		if hasattr( self, "radius" ) and self.radius > 0.0:
			self.trapID = self.addTrapExt(self.radius, self.onTransport )

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.DumbFilter()

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  ��ʼ��ģ�����
 		NPCObject.enterWorld( self )

	def leaveWorld( self ):
		"""
		it will be called, when the entity leaves the world
		"""
		NPCObject.leaveWorld( self )
		self.entityList = []
		try:
			self.delTrap( self.trapID )
		except:
			pass

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		# ��ΪһЩ��̯����Ҳ�õ����entity.�Ҹ�entity�ǲ��ɼ���,����Ӧ�����δ���entity��ģ��
		if len( self.modelNumber ) == 0: return
		# ģ�Ϳ��԰���Ӧ�Ĺ�Ч
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
		self.filter = BigWorld.AvatarFilter()

	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		if pyModel is None:
			return
		self.setModel( pyModel, event )
		am = BigWorld.ActionMatcher( self )    #����ģ��am
		self.model.motors = ( am, )
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def set_modelScale( self, oldScale ):
		"""
		����������NPCObject��set_modelScale������������ģ�ͱ��ʵ��ٶȸ�Ϊ0����˲ʱ���
		"""
		model = self.getModel()
		if model is None: return
		rds.effectMgr.scaleModel( model, ( self.modelScale, self.modelScale, self.modelScale ), 0 )

	def onTransport( self, entitiesInTrap ):
		"""
		��������ص�
		"""
		for entity in entitiesInTrap:
			if entity in self.entityList:
				continue
			else:
				self.cell.onEnterTrap( entity.id )

		for entity in self.entityList:
			if entity in entitiesInTrap:
				continue
			else:
				self.cell.onLeaveTrap( entity.id )

		self.entityList = list( entitiesInTrap )
