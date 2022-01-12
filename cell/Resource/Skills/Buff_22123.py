# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import csdefine
import time
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import Const

class Buff_22123( Buff_Normal ):
	"""
	增加跳舞积分buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

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
		if not receiver.wallow_getLucreRate(): # 如果收益为0，则不奖励
			return Buff_Normal.doLoop( self, receiver, buffData )

		if not receiver.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# 判断角色是否在舞厅中
			return Buff_Normal.doLoop( self, receiver, buffData )

		if receiver.dancePointDailyRecord.getDegree() >= Const.JING_WU_SHI_KE_MAX_POINT_ONE_DAY:	# 如果角色达到一天最大累积量
			return
		if receiver.dancePoint < Const.JING_WU_SHI_KE_MAX_POINT:		# 如果角色跳舞积分没有达到最大累积量
			receiver.dancePoint += 1
			receiver.dancePointDailyRecord.incrDegree()
			receiver.statusMessage( csstatus.JING_WU_SHI_KE_GET_POINT )

		return Buff_Normal.doLoop( self, receiver, buffData )
