# -*- coding: gb18030 -*-
#
# $Id: FuncTeleport.py,v 1.16 2008-07-24 08:46:32 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import csstatus
import csdefine
import Const
import csconst
import re

s = '100 100 100 : 0 0 0'
l = eval( re.sub( "\s*:\s*|\s+", ",", s ) )
a, b = l[:3], l[3:]



class FuncTeleport( Function ):
	"""
	����
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
		try:
			posAndDir = eval( re.sub( "\s*;\s*|\s+", ",", section.readString( "param2" ) ) )
		except Exception, err:
			posAndDir = ( 0,0,0,0,0,0 )
			ERROR_MSG( "space name =", self.spaceName, "pos and dir =", section.readString( "param2" ), err )
		self.position,self.direction = posAndDir[:3],posAndDir[3:]
		self.repLevel = section.readInt( "param3" )
		self.radius = section.readFloat( "param4" )
		self.repMoney = section.readInt( "param5" )

	def calcPosition( self, hardPoint ):
		"""
		 ���㱻���͵�����λ�ã����λ���ǰ���hardPoint�̶�������뾶5�׵�һ��Բ�η�Χ
		 @param hardPoint: Բ��
		"""
		if self.radius <= 0:
			return hardPoint

		a = self.radius * random.random() #��ȡ�漴�뾶
		b = 2*math.pi * random.random() 	 # ��ȡ�漴��
		x = a * math.cos( b )
		z = a * math.sin( b )
		return ( hardPoint[0] + x, hardPoint[1], hardPoint[2] + z )

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
		# ����з�������buff
		if len( player.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		if self.repLevel > player.level:
			player.statusMessage( csstatus.ROLE_TELPORT_NOT_ENOUGH_LEVEL, self.repLevel )
			return
		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# �������Ѿ���������ô��������
			player.statusMessage( csstatus.ROLE_TELEPORT_DEAD_FORBID )
			return
			
		if self.repMoney > 0 and player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_TELEPORT, "" )
			return
		
		# ���ڳ������˰�ᣬ �ڸó��н����κδ������
		if player.tong_holdCity != player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
			if self.repMoney > 0:
				if not player.payMoney( self.repMoney, csdefine.CHANGE_MONEY_TELEPORT ):
					player.statusMessage( csstatus.ROLE_TELPORT_NOT_ENOUGH_MONEY )
					return
					
		if player.isTeamFollowing():
			player.npcTeamFollowTransport( self )
		
		if self.spaceName in csconst.COPY_REVIVE_PREVIOUS:
			player.setCurPosRevivePos()
			
		player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )

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
		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# �������Ѿ���������ô��������
			return False

		return True



