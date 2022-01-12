# -*- coding: gb18030 -*-
#
# $Id: PetTrainer.py,v 1.14 2008-09-05 01:39:51 zhangyuxing Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24: according to new version documents, it is rewriten by huangyongwei
"""

import time

import csstatus
import csdefine
import csconst
import Const
from bwdebug import *
from PetFormulas import formulas
from PetGem import CommonGem
from LevelEXP import PetLevelEXP
from MsgLogger import g_logger
import BigWorld

import ECBExtend


class PetTrainer :
	def __init__( self ) :
		self.ptn_login()


	# ----------------------------------------------------------------
	# public methods for npc dialog
	# ----------------------------------------------------------------
	def ptn_dlgAllownActivateTrainGem( self ) :
		if self.level < Const.PCG_GET_GEM_LEVEL :
			return False
		return not self.isPetTrainGemActive()

	def ptn_questActiveTrainGem( self ) :	# 任务激活宠物经验石
		if self.isPetTrainGemActive():
			#self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
			return
		self.activateGem()
		self.statusMessage( csstatus.PET_GEM_OPEN_SUCCESS )

		# 激活代练功能时给玩家加上一个小时的代练时间。
		self.roleTrainGem.charge( 3600.0, self )
		self.__trainGem.charge( 3600.0, self )

	def ptn_dlgBuyTrainGem( self, npcEntity ) :	# NPC激活宠物经验石
		if self.isPetTrainGemActive():
			#self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
			return
		cost = formulas.getTrainGemActivateCost()
		if cost > self.money :
			self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
		else :
			self.activateGem()
			self.payMoney( cost, csdefine.CHANGE_MONEY_DLGBUYTRAINGEM )
			self.statusMessage( csstatus.PET_GEM_OPEN_SUCCESS )


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def ptn_onFeedEXPResult( self, result, value ) :
		"""
		<Defined/>
		经验喂养返回
		"""
		if result == csstatus.PET_TRAIN_FEED_SUCCESS :
			self.__trainGem.subtractEXP( value, self )
			self.questPetEvent( "feed" )
		else :
			self.statusMessage( result )
		self.pcg_releaseOperating_()


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def ptn_hireCommonGem( self, srcEntityID, index, remainTime ) :
		"""
		<Exposed/>
		玩家租用宠物经验石

		@param index : 租用的宝石索引,int8
		@param remainTime : 客户端随机生成的宝石租用时间，不能超过24小时，int64
		"""
		if not self.hackVerify_( srcEntityID ) :
			return
		if self.isState( csdefine.ENTITY_STATE_DEAD ):
			self.statusMessage( csstatus.GEM_DEAD_CANT_HIRE )
			return
		if not self.isPetTrainGemActive() :
			HACK_MSG( "gems are not activated!" )
			return
		if self.ptn_getComGemCount() + self.gem_getComGemCount() >= csconst.GEM_COUNT_UPPER:
			self.statusMessage( csstatus.GEM_HIRE_FULL )
			return
		if index < csdefine.GEM_PET_COMMON_INDEX or index >= csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER:
			HACK_MSG( "gem index out of range!" )
			return

		if remainTime < 3 * 3600 or remainTime > 24 * 3600:	# 宝石的租用时间限制
			return
		if self.money < formulas.getCommonGemActicateCost() :
			self.statusMessage( csstatus.PET_GEM_ACTIVATE_FAIL_LACK_MONEY )
			return
		comGem = CommonGem( index )
		self.__commonGems.append( comGem )
		self.payMoney( formulas.getCommonGemActicateCost(), csdefine.CHANGE_MONEY_HIRECOMMONGEM )
		timerBegin = self.gem_getLimitTime( remainTime )
		timerID = self.addTimer( timerBegin, 0, ECBExtend.GEM_PET_TIME_LIMIT_CBID )
		comGem.setTimerID( timerID )
		limitTime = time.time() + timerBegin
		comGem.load( self, limitTime )

	def ptn_inactivateCommonGem( self, srcEntityID, index ) :
		"""
		<Exposed/>
		取消经验石的领取
		"""
		if not self.hackVerify_( srcEntityID ) :
			return
		if not self.isPetTrainGemActive():
			HACK_MSG( "gems are not activated!" )
			return
		if index < csdefine.GEM_PET_COMMON_INDEX or index >= csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER:
			HACK_MSG( "gem index out of range!" )
			return
		comGem = None
		for gem in self.__commonGems:
			if gem.getIndex() == index:
				comGem = gem
				break
		if comGem is None:	# 玩家并没有租用当前索引的宝石
			pass
		else:
			comGem.offload( self )
			self.cancel( comGem.getTimerID() )
			self.__commonGems.remove( gem )

		#	self.statusMessage( scstatus.PET_GEM_INACTIVATE_SUCCESS )

		#	self.statusMessage( scstatus.PET_GEM_INACTIVATE_FAIL )

	# ---------------------------------------
	def ptn_flushTrain( self, srcEntityID ) :
		"""
		<Exposed/>

		更新代练数据
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.__trainGem.flush( self )


	def ptn_trainCharge( self, gold ) :
		"""
		Define method.

		给代练宝石充值
		"""
		if not self.isPetTrainGemActive():
			HACK_MSG( "player( %s )'s gems are not activated!" % self.getName() )
			self.base.ptn_trainChargeCB( gold, False )
			return
		statusID = self.__trainGem.charge( formulas.getTrainTime( gold ), self )
		if statusID != csstatus.PET_TRAIN_CHARGE_SUCCESS:
			state = False
			self.statusMessage( statusID )
		else:
			state = True
			self.statusMessage( statusID, gold )
		self.base.ptn_trainChargeCB( gold, state )

	def ptn_stratTrain( self, srcEntityID, trainType ) :
		"""
		<Exposed/>
		开始代练
		函数单词写错:startTrain
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.isPetTrainGemActive():
			HACK_MSG( "player( %s )'s gems are not activated!" % self.getName() )
			return
		if trainType not in [ csdefine.GEM_WORK_NORMAL, csdefine.GEM_WORK_HARD ]:
			HACK_MSG( "玩家( %s )选择的代练类型( %i )不正确。" % ( self.getName(), trainType ) )
			return
		self.__trainGem.startTrain( trainType, self )
		try:
			g_logger.petStartTrainingsLog( self.databaseID, BigWorld.entities[srcEntityID].databaseID, trainType )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )


	def ptn_stopTrain( self, srcEntityID ) :
		"""
		<Exposed/>
		停止代练
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.isPetTrainGemActive():
			HACK_MSG( "player( %s )'s gems are not activated!" % self.getName() )
			return
		self.__trainGem.stopTrain( self )

	def ptn_feedPetEXP( self, srcEntityID, dbid, value ) :
		"""
		<Exposed/>
		喂养宠物
		"""
		if not self.hackVerify_( srcEntityID ) : return
		gemValue = self.__trainGem.getEXP( self )
		if gemValue < value : value = gemValue
		if value <= 0 : return														# 这种情况一般不会出现，除非客户端欺骗，因此不作回复，直接忽略
		if not self.pcg_lockOperation_() : return									# 锁住操作（注：调用的每个结束出口都要回调：ptn_onFeedEXPResult）
		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :											# 如果是喂养出战宠物
			if actPet.etype == "MAILBOX" :											# 暂时找不到出征的宠物
				self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_NOT_EXIST, value )
			else :
				entity = actPet.entity
				if self.level + Const.PET_EXP_LEVEL_LIMIT_GAP > entity.level:
					entity.absorbEXP( value )										# 注：这里必须回调：ptn_onFeedEXPResult
				elif self.level + Const.PET_EXP_LEVEL_LIMIT_GAP == entity.level :	# 刚好高于玩家等级，只吸不升
					expMax = PetLevelEXP.getEXPMax( entity.level )
					tempValue = expMax - entity.EXP
					if value > tempValue: value = tempValue
					entity.absorbEXP( value )	
					if entity.EXP >= expMax:
						self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_LEVEL_LIMIT, tempValue )
				else :			# 宠物等级高于玩家5级以上不能吸经验
					self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_LEVEL_LIMIT, value )
		else :
			if not self.pcg_petDict.has_key( dbid ):
				ERROR_MSG( "player( %s ) cannot find the pet( %i ) in pcg_petDict..." % ( self.getName(), dbid ) )
				return
			level = self.pcg_petDict.get( dbid ).level
			if self.level + Const.PET_EXP_LEVEL_LIMIT_GAP > level:		# 宠物等级高于玩家5级以上不能吸经验
				self.base.ptn_feedPetEXP( dbid, value )								# 注：这里必须回调：ptn_onFeedEXPResult
			elif self.level + Const.PET_EXP_LEVEL_LIMIT_GAP == level:
				self.base.ptn_feedPetEXPNotLevel( dbid, value )
			else :
				self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_LEVEL_LIMIT, value )

	def isPetTrainGemActive( self ):
		"""
		判断宠物经验石是否激活
		"""
		return self.gemActive & csdefine.GEM_PET_ACTIVE_FLAG

	def activateGem( self ):
		"""
		激活经验石
		"""
		self.gemActive |= csdefine.GEM_PET_ACTIVE_FLAG
		self.gemActive |= csdefine.GEM_ROLE_ACTIVE_FLAG
		self.statusMessage( csstatus.GEM_LOAD_COMMON ) #放在这里是为了避免产生两次同样的提示

	def ptn_getComGemCount( self ):
		"""
		public
		获得当前玩家领取的经验加成宝石个数
		"""
		return len( self.__commonGems )

	def onPetGemTimeLimit( self, controllerID, userData ):
		"""
		玩家租用宠物经验石，timer回调
		"""
		for gem in self.__commonGems:
			if gem.getTimerID() == controllerID:
				gem.offload( self )
				self.__commonGems.remove( gem )
				break

	def ptn_onLevelUp( self ):
		"""
		宠物宝石系统角色升级通知
		"""
		self.__trainGem.onRoleLevelUp( self )


	def ptn_login( self ):
		"""
		玩家登录
		"""
		if not self.isPetTrainGemActive():
			return
		if self.__trainGem.isInTrain():
			self.__trainGem.flush( self )
