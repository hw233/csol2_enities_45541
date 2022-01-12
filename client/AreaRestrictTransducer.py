# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from gbref import rds
import csdefine
import Define
from Function import Functor


class AreaRestrictTransducer( NPCObject, CombatUnit ):
	"""
	�������ƴ�������
	���ã��Խ�������뿪���������ҽ���ĳЩ�������ƣ����̯���ƣ�PK����
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.selectable = False		# ����ѡ��
		self.modelScale = 1.0
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  ��ʼ��ģ�����
 		NPCObject.enterWorld( self )

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		# ��ΪһЩ��̯����Ҳ�õ����entity.�Ҹ�entity�ǲ��ɼ���,����Ӧ�����δ���entity��ģ��
		if len( self.modelNumber ) == 0: return
		rds.npcModel.createDynamicModelBG( self.modelNumber, Functor( self.__onModelLoad, event ) )
		
	def __onModelLoad( self, event, model):
		"""
		ģ�ͼ������
		"""
		if model is None:
			return
		self.setModel( model, event )
		self.model.motors = ( )
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def set_modelScale( self, oldScale ):
		"""
		����������NPCObject��set_modelScale������������ģ�ͱ��ʵ��ٶȸ�Ϊ0����˲ʱ���
		"""
		model = self.getModel()
		if model is None: return
		rds.effectMgr.scaleModel( model, ( self.modelScale, self.modelScale, self.modelScale ), 0 )
