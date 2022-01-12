# -*- coding: gb18030 -*-
#
#


import BigWorld
import csconst
import csstatus
import Const
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99021( Buff_Normal ):
	"""
	"需增加BUFF099021的支持，技能使用已有的普通BUFF脚本。
	角色在存在此BUFF时死亡，会在死亡的通用复活提示之前，提示玩家“是否使用凤凰引原地复活？”选择“是”，
	BUFF消失原地复活，选择“否”，BUFF保留，显示死亡的通用复活提示。"	
	
	2	射手	322441	凤凰引	复活	给自己或队友增加一个状态，在此状态下死亡时，可就地复活，并恢复部分生命法力。状态持续10分钟
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100.0
		
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
		if not receiver.state == csdefine.ENTITY_STATE_DEAD:
			return

		receiver.setHP( receiver.HP_Max * self._p1 )
		receiver.setMP( receiver.MP_Max * self._p1 )
		receiver.changeState( csdefine.ENTITY_STATE_FREE )
		receiver.updateTopSpeed()
		