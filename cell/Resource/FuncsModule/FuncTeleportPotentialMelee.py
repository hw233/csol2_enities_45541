# -*- coding: gb18030 -*-
#
# $Id: FuncTeleport.py,v 1.16 2008-07-24 08:46:32 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import csdefine
import csstatus
import time
import csconst
import re
import BigWorld

class FuncTeleportPotentialMelee( Function ):
	"""
	��������ý�
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
		self.level = section.readInt( "param1" )		#����ȼ�

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

		if player.level < self.level:
			player.statusMessage( csstatus.POTENTIAL_MELEE_INVALID_LEVEL, self.level )
			return
		elif not player.isInTeam():
			player.statusMessage( csstatus.POTENTIAL_MELEE_INVALID_TEAM )
			return

		spaceLevel = player.level
		player.setTemp( "currentSpaceName", player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		player.setTemp( "enterPosition", tuple( player.position ) )
		player.setTemp( "enterDirection", tuple( player.direction ) )

		if BigWorld.globalData.has_key( 'potentialMelee_%i' % player.getTeamMailbox().id ):
			#��ҵĶ���ӵ��һ��Ǳ���Ҷ�����
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU ):
				player.statusMessage( csstatus.POTENTIAL_HAS_ENTER )
				return

			player.setTemp( "enterSpaceID", player.teamMailbox.id )
			player.gotoSpace( "fu_ben_xuan_tian_huan_jie", ( 0, 0, 0 ), ( 0, 0, 0 ) )
			player.addActivityCount( csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU )
			return
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			members = player.getAllMemberInRange( 30 )
			if len( members ) != 3 :
				player.statusMessage( csstatus.POTENTIAL_MELEE_ENOUGH_MEMBER )
				return

			potentialMeleeEnterFlag = False
			for i in members:
				if i.level < self.level:
					player.statusMessage( csstatus.POTENTIAL_MELEE_MEMBER_NOT_LEVEL, self.level )
					return

				if i.isActivityCanNotJoin( csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU ):
					player.statusMessage( csstatus.POTENTIAL_MELEE_MEMBER_HAS_ENTER, i.getName() )
					potentialMeleeEnterFlag = True

			if potentialMeleeEnterFlag : return

			for i in members:
				i.setTemp( "enterSpaceID", player.teamMailbox.id )
				i.setTemp( "pspaceLevel", spaceLevel )
				i.gotoSpace( "fu_ben_xuan_tian_huan_jie", ( 0, 0, 0 ), ( 0, 0, 0 ) )
				i.addActivityCount( csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU )

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
		return BigWorld.globalData.has_key( "AS_PotentialMelee" )

#
# $Log: not supported by cvs2svn $
#
