# -*- coding: gb18030 -*-
#
# $Id: FuncEnterFamilyWar.py,v 1.2 2008-08-02 09:25:48 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import csconst
import csstatus
from Resource.SkillLoader import g_skills
import csdefine

class FuncEnterFamilyWar( Function ):
	"""
	�������ս��
	"""
	def __init__( self, section ):
		"""
		param1: amount

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.map = section.readString( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.level < csconst.PK_PROTECT_LEVEL:
			player.statusMessage( csstatus.ROLE_LEVEL_LOWER_PK_ALOW_LEVEL )
			player.endGossip( talkEntity )
			return

		player.setTemp( "enterby_NPCClassID", talkEntity.className )
		player.gotoSpace( self.map, ( 0, 0, 0 ), ( 0, 0, 0 ) )
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
		buff = g_skills[ 122155001 ].getBuffLink( 0 ).getBuff()
		return len( player.findBuffsByBuffID( buff.getBuffID() ) ) <= 0


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/07/25 03:17:49  kebiao
# no message
#
#
