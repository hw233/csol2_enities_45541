# -*- coding: gb18030 -*-
#
# $Id: FuncRegRevivePoint.py,v 1.2 2008-04-25 08:35:47 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import csstatus
import utils

class FuncRegRevivePoint( Function ):
	"""
	��¼�����
	"""
	def __init__( self, section ):
		"""
		param1: spaceName
		param2: x, y, z
		param3: d1, d2, d3
		param4: radius
		
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" )
		self.position = None
		self.direction = None
	
		position = section.readString( "param2" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param2 " % ( self.__class__.__name__, position ) )
		else:
			self.position = pos
		
		direction = section.readString( "param3" )
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param3 " % ( self.__class__.__name__, direction ) )
		else:
			self.direction = dir

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.statusMessage( csstatus.ROLE_REGISTER_REVIVE_POINT )
		player.setRevivePos( self.spaceName, self.position, self.direction )
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return len( self.spaceName ) > 0


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/04/25 01:50:47  kebiao
# ��¼�����
#
#
