# -*- coding: gb18030 -*-
#
# $Id: RoleGem.py,v 1.1 2008-08-01 11:22:25 wangshufeng Exp $

"""
角色经验宝石系统，15:31 2008-7-21，wsf
"""

import time
import csdefine
import csstatus
import csconst
import Const
from bwdebug import *
import random
import ECBExtend
from LevelEXP import RoleLevelEXP as RLevelEXP
from ExpGem import CommonExpGem


class RoleGem:
	def __init__( self ):
		self.gem_login()
		# self.gemActive,玩家经验宝石系统是否被激活的标志，右边第1位表示玩家经验宝石，第2位表示玩家宠物经验宝石


	def gem_canActivateGem( self ):
		"""
		判断是否能够激活经验宝石系统
		"""
		if self.level < Const.PCG_GET_GEM_LEVEL:
			DEBUG_MSG( "玩家( %s )级别小于PCG_GET_GEM_LEVEL，不能激活经验宝石。" % ( self.getName() ) )
			return False
		return True


	def gem_activateGem( self, entityID ):
		"""
		激活经验宝石系统

		@param entityID : npc的id
		@type entityID : OBJECT_ID
		"""
		if self.isRoleTrainGemActive():
		#	self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
			return

		if self.money < csconst.GEM_ACTIVATE_COST:
			self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
		else :
			self.gemActive |= csdefine.GEM_ROLE_ACTIVE_FLAG


	def gem_charge( self, gold ):
		"""
		Define method.
		给代练宝石充值

		@param value : 元宝
		@type value : UINT32
		"""
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活，不能充值代练宝石。" % ( self.getName() ) )
			self.base.gem_chargeCB( gold, False )
			return
		statusID = self.roleTrainGem.charge( gold * 180, self )	# 目前20个元宝可以买1个小时
		if statusID != csstatus.PET_TRAIN_CHARGE_SUCCESS:
			state = False
			self.statusMessage( statusID )
		else:
			state = True
			self.statusMessage( statusID, gold )
		self.base.gem_chargeCB( gold, state )

	def gem_startTrain( self, srcEntityID, trainType ):
		"""
		Exposed method.
		开始代练，两种模式：普通代练，刻苦代练。

		@param trainType : 代练模式
		@type trainType : UINT8
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		if trainType not in [ csdefine.GEM_WORK_NORMAL, csdefine.GEM_WORK_HARD ]:
			HACK_MSG( "玩家( %s )选择的代练类型( %i )不正确。" % ( self.getName(), trainType ) )
			return

		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活，不能开始代练。" % ( self.getName() ) )
			return
		self.roleTrainGem.startTrain( trainType, self )


	def gem_stopTrain( self, srcEntityID ):
		"""
		Exposed method.
		停止代练。
		开始代练后，此函数会被玩家主动调用或者在client时限到期后调用。
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活，不需停止代练。" % ( self.getName() ) )
			return
		self.roleTrainGem.update( self )
		self.roleTrainGem.stopTrain( self )


	def isRoleTrainGemActive( self ):
		"""
		判断玩家经验宝石是否激活
		"""
		return self.gemActive & csdefine.GEM_ROLE_ACTIVE_FLAG


	def gem_onLevelUp( self ):
		"""
		玩家升级通知，通知代练宝石
		"""
		self.roleTrainGem.onRoleLevelUp( self )
		self.absorbableEXPLevelValue = 0


	def gem_derive( self, srcEntityID ):
		"""
		Exposed method.
		从宝石汲取经验
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活，不可汲取经验。" % ( self.getName() ) )
			return
		if self.roleTrainGem.isInTrain():
			DEBUG_MSG( "玩家( %s )正在代练中，不能汲取经验" % self.getName() )
			return
			
		# 代练吸取的经验不能超过等级所需经验10% by 姜毅
		value = self.roleTrainGem.exp
		absorbLevelMax = RLevelEXP.getEXPMax( self.level ) / 10
		if self.absorbableEXPLevelValue >= absorbLevelMax:
			self.statusMessage( csstatus.GEM_ROLE_LEVEL_EXP_MAX )
			return
		limitValue = absorbLevelMax - self.absorbableEXPLevelValue
		if value > limitValue: value = limitValue
		
		self.absorbableEXPLevelValue += value
		
		self.roleTrainGem.giveExp( self, value )


	def gem_hire( self, srcEntityID, index, remainTime ):
		"""
		Exposd method.

		租用玩家经验宝石

		@param index : 租用的宝石索引,int8
		@param remainTime : 客户端随机生成的宝石租用时间，int64
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if self.isState( csdefine.ENTITY_STATE_DEAD ):
			self.statusMessage( csstatus.GEM_DEAD_CANT_HIRE )
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活，不可租用经验宝石。" % ( self.getName() ) )
			return
		if self.ptn_getComGemCount() + self.gem_getComGemCount() >= csconst.GEM_COUNT_UPPER:	# 目前最多仅能领取5颗
			self.statusMessage( csstatus.GEM_HIRE_FULL )
			return
		if index < csdefine.GEM_ROLE_COMMON_INDEX or index >= csdefine.GEM_ROLE_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER:
			return
		if remainTime < 3 * 3600 or remainTime > 24 * 3600:	# 宝石的租用时间限制
			return
		if not self.payMoney( csconst.GEM_HIRE_PAY, csdefine.CHANGE_MONEY_GEM_HIRE ):
			DEBUG_MSG( "领取经验宝石的花费不够" )
			return
		comGem = CommonExpGem( index )
		timerBegin = self.gem_getLimitTime( remainTime )
		comGem.timerID = self.addTimer( timerBegin, 0, ECBExtend.GEM_ROLE_TIME_LIMIT_CBID )
		limitTime = time.time() + timerBegin
		comGem.load( self, limitTime )

	def gem_endHire( self, srcEntityID, index ):
		"""
		Exposed method.
		中止领取
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活。" % ( self.getName() ) )
			return
		comGem = None
		for gem in self.roleCommonGem:
			if gem.index == index:
				comGem = gem
				break
		if comGem is None:	# 玩家并没有租用当前索引的宝石
			pass
		else:
			comGem.offload( self )


	def gem_updateTrain( self, srcEntitiID ):
		"""
		Exposed method.

		客户端请求更新代练数据
		"""
		if not self.roleTrainGem.isInTrain():
			return
		self.roleTrainGem.update( self )


	def gem_getLimitTime( self, remainTime ):
		"""
		计算得出限制时间。

		当这颗宝石已经领取的时间达到该宝石总时间的30%时，有50%的几率会自动终止，
		并不再以剩下的时间出现在左边的未领取列表中。如果没有判断为终止，那么在30%后，
		每累计增加10%的时间的那一刻，有50%的几率会自动终止。有剩余时间为0后，立刻终止领取。
		"""
		limitTime = remainTime * 0.3
		restTime = remainTime * 0.1
		count = 7	# 每累计增加10%的时间的那一刻，有50%的几率会自动终止
		while restTime > 0 and count > 0:
			count -= 1
			restTime *= random.random() > 0.5 and 1 or 0
			limitTime += restTime
		return limitTime


	def onRoleGemTimeLimit( self, controllerID, userData ):
		"""
		timer
		"""
		for gem in self.roleCommonGem:
			if gem.timerID == controllerID:
				gem.offload( self )
				break


	def gem_login( self ):
		"""
		玩家登录
		"""
		if not self.isRoleTrainGemActive():
			return
		if self.roleTrainGem.isInTrain():
			self.roleTrainGem.update( self )


	def gem_getComGemCount( self ):
		"""
		获得玩家当前领取的经验宝石数量
		"""
		return len( self.roleCommonGem )

#
# $Log: not supported by cvs2svn $
#