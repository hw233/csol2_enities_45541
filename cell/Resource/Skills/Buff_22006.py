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

class Buff_22006( Buff_Normal ):
	"""
	日光浴buff，不断增加经验（当然，指的是有效时间内）
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
		self._p1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 					# 增加经验的公式
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 					# 每天最多可以晒多长时间（ 单位是秒 ）
		self._p3 = int( dict[ "LoopSpeed" ] if dict[ "LoopSpeed" ] > 0 else 0 ) 					# 增加经验相隔的时间
		self._hpVal = int( self._p1[ 3:len( self._p1 ) ] )	# 增加的经验值
		self._hpOpt = self._p1[ 2:3 ]						# 操作符

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
		actPet = receiver.pcg_getActPet()
		if actPet :													# 如果玩家携带有出征宠物
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )	# 则收回之
		Buff_Normal.doBegin( self, receiver, buffData )
		date = time.localtime()[2]
		if receiver.sunBathDailyRecord.date != date:
			receiver.sunBathDailyRecord.date = date
			receiver.sunBathDailyRecord.sunBathCount = 0
			receiver.sunBathDailyRecord.prayCount = 0

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
		actPet = receiver.pcg_getActPet()
		if actPet :													# 如果玩家携带有出征宠物
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )	# 则收回之
		date = time.localtime()[2]
		if receiver.sunBathDailyRecord.date != date:
			receiver.sunBathDailyRecord.date = date
			receiver.sunBathDailyRecord.sunBathCount = 0

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
		increaseEXP = self.getIncreaseEXP( receiver.level, self._hpOpt, self._hpVal )
		if receiver.queryTemp( "clean_sun_bath_exp", 0 ) != increaseEXP:
			# 记录玩家的纯净日光浴经验，一进地图的时候就设置一次了，这里还要设置一次，以防止玩家级别改变
			receiver.setTemp( "clean_sun_bath_exp", increaseEXP )

		# 判断角色是否在合法日光浴时间
		if receiver.isSunBathing() and receiver.sunBathDailyRecord.sunBathCount < self._p2:

			if receiver.queryTemp("btxy_exp_percent", 0.0) > 0:	# 如果角色有波涛汹涌buff
				increaseEXP = int( increaseEXP * (1 - ( receiver.queryTemp("btxy_exp_percent", 0.0) )/100) )

			gainedExp = 0
			#receiver.updateSunBathCount( self._p3 )	# 循环多长时间加一次，就加多少时间

			if receiver.queryTemp( "has_cleanlily_drink", 0 ) == 1:	# 如果有清爽饮料
				expRate = receiver.queryTemp( "drink_exp_rate", 0.0 )
				gainedExp = int( increaseEXP * expRate )			# 变成双倍经验（或其他倍数，具体要看给清爽饮料的配置了多少倍）

			if receiver.queryTemp( "sxym_exp_rate", 0.0 ) > 0:	# 如果有赏心悦目buff
				gainedExp += int( increaseEXP * receiver.queryTemp( "sxym_exp_rate", 0.0 ) )

			if receiver.queryTemp( "lwxl_exp_rate", 0.0 ) > 0:	# 如果有龙王显灵buff
				gainedExp += int( increaseEXP * receiver.queryTemp( "lwxl_exp_rate", 0.0 ) )

			if receiver.queryTemp( "scyy_exp_rate", 0.0 ) > 0:	# 如果有神采熠熠buff
				gainedExp += int( increaseEXP * receiver.queryTemp( "scyy_exp_rate", 0.0 ) )

			if receiver.queryTemp( "has_sun_bath_vip", 0 ) == 1:	# 如果是海滨VIP
				expRate = receiver.queryTemp( "vip_exp_rate", 0.0 )
				gainedExp += int( increaseEXP * expRate )			# 加上vip导致的经验翻倍（具体倍数同样要看给VIP卡的配置了多少倍）

			if gainedExp == 0:										# 说明什么经验翻倍的道具都没有用
				gainedExp = increaseEXP

			if receiver.queryTemp( "hssl_exp_stop", 0 ) != 1:	# 如果角色有海市蜃楼buff则不获得经验
				receiver.addExp ( gainedExp, csdefine.CHANGE_EXP_SUN_BATH )

			if receiver.queryTemp( "hsch_gain_potential", 0 ) == 1:	# 如果角色有海神赐福buff，则获得和经验值相同的潜能
				receiver.addPotential( gainedExp )
		else:
			receiver.statusMessage( csstatus.SKILL_NO_SUN_BATH_TIME_EXP )

		return Buff_Normal.doLoop( self, receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "sun_bath_area_count" )	# 清除掉记录玩家身上有几个区域的标记

	def getIncreaseEXP( self, level, opration, value ):
		"""
		根据公式获得增加的Exp
		"""
		return level + value