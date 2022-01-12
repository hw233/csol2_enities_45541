# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.9 2008-03-25 01:59:31 zhangyuxing Exp $

"""
NPC�Ļ���
"""
from bwdebug import *
from Monster import Monster
import csdefine

class NPC( Monster ):
	"""
	NPC�Ļ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		Monster.onLoadEntityProperties_( self, section )
		flags = self.getEntityProperty( "flags" )					#-----------------------------------------------
		flags &= ~( 1 << csdefine.ENTITY_FLAG_MONSTER_INITIATIVE ) 	#��NPC��ENTITY_FLAG_MONSTER_INITIATIVE������ε�
		self.setEntityProperty( "flags", flags )					#-----------------------------------------------
		
	def _initDefaultAI( self, selfEntity ):
		"""
		��ʼ������Ĭ�ϵ�AI
		"""
		pass #NPC��ʱû��Ĭ��AI
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		selfEntity.setLevel( selfEntity.level )
		self._initAI( selfEntity )
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_NPC )

# NPC.py
