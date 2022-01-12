# -*- coding: gb18030 -*-
#
# 2008-12-11 15:22 SongPeiFang
#

from FuncTeleport import FuncTeleport
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import random
import re
import Const
import csdefine


class FuncTeleToSunBath( FuncTeleport ):
	"""
	传送至日光浴地图
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" )
		positionsAndDirection = section.readString( "param2" ).split( ';' )	# 随即坐标（一组）;方向（一个）
		if len( positionsAndDirection ) <= 1:
			# 如果分割数组不正确，一定是配置的格式错误了
			ERROR_MSG( "Config error, bad format for positions infomations!" )
		self.positions = positionsAndDirection[0].split( '|' )
		self.direction = eval( re.sub( "\s*;\s*|\s+", ",", positionsAndDirection[1] ) )	# 方向
		self.repLevel = section.readInt( "param3" )										# 移动所需等级
		self.radius = section.readFloat( "param4" )										# 移动到的位置进行随即偏移的值
		self.repMoney = section.readInt( "param5" )										# 移动所需金钱
	
	def calcPosition( self, hardPoint ):
		"""
		 计算被传送的最终位置，这个位置是按照hardPoint固定点随机半径5米的一个圆形范围
		 @param hardPoint: 圆心
		"""
		return FuncTeleport.calcPosition( self, hardPoint )
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		"""
		if player.hasMerchantItem():
			player.setGossipText( cschannel_msgs.CAIJI_SKILL_VOICE_3 )
			player.sendGossipComplete( talkEntity.id )
			return

		# 如果有法术禁咒buff
		if len( player.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# 如果玩家已经死亡，那么不允许传送
			return
			
		positionIndex = random.randint( 0, len( self.positions ) - 1 )
		self.position = eval( re.sub( "\s*;\s*|\s+", ",", self.positions[positionIndex] ) )	# 坐标
		FuncTeleport.do( self, player, talkEntity )
	
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		return True

# FuncTeleToSunBath.py