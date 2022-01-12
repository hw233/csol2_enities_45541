# -*- coding: gb18030 -*-
#
# $Id: SpaceTransport.py,v 1.8 2007-06-14 09:55:30 huangyongwei Exp $

"""
�����ʵ�塣
"""

import BigWorld
import Love3
from bwdebug import *
from NPCObject import NPCObject
import csdefine
import cschannel_msgs

class SpaceTransport( NPCObject ):
	"""
	�����ʵ�壬�ṩ��ҽ�ɫ�л������Ĳ�����
		@ivar uid:			����ڱ�ʶ
		@type uid:			string
		@ivar destspace:	Ŀ�곡����ʶ
		@type destspace:	string
		@ivar destpos:		Ŀ�������
		@type destpos:		vector3
	"""
	def __init__(self):
		"""
		���캯����
		"""
		NPCObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_TRANSPORT )

	def isInteractionRange( self, entity ):
		"""
		�ж�һ��entity�Ƿ����Լ��Ľ�����Χ��
		"""
		return self.position.flatDistTo( entity.position ) < self.range + 1 # ������ʱ�����ڷ�Χ����Ӵ�1��

# SpaceTransport.py
