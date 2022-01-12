# -*- coding: gb18030 -*-
#
# $Id: Buff_2008.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

"""
此buff结束之后将会把玩家传送到指定位置而且仅限于同一空间内 by mushuang
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import get3DVectorFromStr
from math import radians

class Buff_22129( Buff_Normal ):
	"""
	example:
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
		self._position = ( 0.0, 0.0, 0.0 ) # 玩家需要被传送到的位置（注意这个数据是每个buff独立的，需要克隆处理）
		self._yaw = 0.0 # 传送之后玩家的方向
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		# Param1 中配置玩家要被传送到的位置，x,y,z三个分量请使用空格分开，如：1.0 2.0 3.0
		# Param2 中配置玩家传送之后围绕y轴的旋转量，即地编中的yaw值
		
		Buff_Normal.init( self, dict )
		self._position = get3DVectorFromStr( dict[ "Param1" ] )
		
		self._yaw = radians( float( dict[ "Param2" ] ) ) # 将策划地编中看到的是角度，这里必须要转换成弧度才能在teleport函数中使用
	
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# 记录此buff加到玩家身上时玩家所在的sapceID, 主要是用来验证在传送时是否仍然处于同一空间，
		# 防止出现玩家走出空间之后再被传送而卡死的情况。
		receiver.setTemp( "Buff_22129_Space_ID", receiver.spaceID )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# 记录玩家所在空间
		receiver.setTemp( "Buff_22129_Space_ID", receiver.spaceID )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		spaceID = receiver.popTemp( "Buff_22129_Space_ID", -1 )
		
		if spaceID == receiver.spaceID:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				# 传送时不应该有掉落伤害,所以将“开始掉落的高度”重置为要传送到的位置的高度
				receiver.fallDownHeight = self._position[ 1 ]
				# 如果接受者是玩家，那么必须通知客户端同步yaw信息，否则yaw参数不会起作用，原因见unifyYaw的注释。
				receiver.client.unifyYaw() 
			receiver.teleport( None, self._position, ( 0.0, 0.0, self._yaw ) )
		else:
			ERROR_MSG( "Incorrect use of this buff, check the instructions at the beginning of the module please!" )
			
