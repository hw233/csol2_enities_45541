# -*- coding: gb18030 -*-
#
# $Id: FuncGetFamilyNPCBuff.py,v 1.3 2008-07-25 03:17:24 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import csdefine
import csstatus

class FuncGetFamilyNPCBuff( Function ):
	"""
	��ȡ����NPC buff
	"""
	def __init__( self, section ):
		"""
		param1: amount
		
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.p1 = section.readInt( "param1" )
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.getFamilyManager().onGetContestNPCBuff( player.base, player.databaseID, self.p1  )
		player.endGossip( talkEntity )
	
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
		return player.familyNPC == talkEntity.className


#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/07/19 04:08:04  kebiao
# no message
#
#
