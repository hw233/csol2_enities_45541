# -*- coding: gb18030 -*-

"""
追捕
"""

import csconst
from Buff_Normal import Buff_Normal

class Buff_299015( Buff_Normal ):
	"""
	追捕buff
	"""
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
		if receiver.spaceType == "fu_ben_jian_yu":
			return False
			
		spaceScript = receiver.getCurrentSpaceScript()
		
		# 判断是否可抓捕罪犯的地图 不是则释放追捕buff
		if spaceScript.canArrest:
			receiver.setTemp( "gotoPrison", True )
			receiver.gotoSpace( "fu_ben_jian_yu", (0,0,0), (0,0,0) )
			return False
			
		return Buff_Normal.doLoop( self, receiver, buffData )
			