# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCopyTemp.py,v 1.1 2007-10-07 07:13:39 phw Exp $

"""
"""

import Language
import BigWorld
from SpaceItem import SpaceItem
from bwdebug import *
from SpaceDomain import SpaceDomain
import csdefine

# ������
class SpaceDomainCopyTemp(SpaceDomain):
	"""
	��ʱ������������cell��NPC��entity����ͨ��requestCreateSpace()�ӿ�����ȡ�¸���ʵ����
	���˸������ṩͨ����׼�Ľӿڽ���ķ�ʽ��
	ʹ�ô�����ʱ��������"waitingCycle"����Ӧ����������1���ʱ�䣬�Լ������ั��ʵ��������
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COPY_TEMP
		

	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		raise RuntimeError, "I can't implement the functional."
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""
		raise RuntimeError, "I can't implement the functional."

#
# $Log: not supported by cvs2svn $
#