# -*- coding: gb18030 -*-

"""
吹风流
"""
from Buff_Normal import Buff_Normal
import Math
import csdefine

class Buff_208003( Buff_Normal ):
	"""
	example:
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
		self.height = float( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		if not receiver.queryTemp("upHeight",False) and receiver.getEntityType() == csdefine.ENTITY_TYPE_MONSTER:
			receiver.setTemp("upHeight",True)
			receiver.openVolatileInfo()
			receiver.position += Math.Vector3( 0, self.height, 0 )
		return Buff_Normal.doLoop( self, receiver, buffData )
	
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
		receiver.removeTemp( "upHeight" )
 