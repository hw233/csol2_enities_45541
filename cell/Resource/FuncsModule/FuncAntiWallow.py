# -*- coding: gb18030 -*-
#
# $Id: FuncWarehouse.py,v 1.12 2008-01-15 06:06:34 phw Exp $

"""
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
import csdefine
import items
import Const
import ItemTypeEnum
import sys

class FuncCheckUsedWallow( Function ):
	"""
	�Ƿ��ܷ�����ϵͳ����
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
	
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
		return not player.wallow_isEffected()