# -*- coding: gb18030 -*-
#
# $Id: RoleGem.py,v 1.1 2008-08-01 11:17:09 wangshufeng Exp $

"""
角色经验宝石系统，15:31 2008-7-21，wsf
"""

import time
import csdefine
import csstatus
import csconst
from bwdebug import *
import BigWorld

import event.EventCenter as ECenter

class RoleGem:
	"""
	玩家经验宝石系统
	"""
	def __init__( self ):
		"""
		玩家代练宝石：
		玩家开始代练，界面上5分钟更新一次宝石经验值数据、宝石充值的剩余时间.
		而在玩家停止代练、或剩余时间到期时才通知服务器计算所获经验值并停止代练，且更新到客户端，
		在玩家重上线时，如果还在代练期间则服务器端计算所获经验值并做相关处理，同时通知到客户端。

		玩家领取的宝石：
		玩家领取宝石后，客户端随机获得玩家能够使用宝石的时间，并通知服务器计算出实际能够使用的时间。
		服务器加timer，在timer到期后做宝石到期的处理。客户端表现与服务器无关。
		"""
		pass
		# self.gemActive,玩家经验宝石系统是否被激活的标志，右边第1位表示玩家经验宝石，第2位表示玩家宠物经验宝石


	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if self.roleTrainGem.inTraining():
			self.roleTrainGem.startUpdateTimer()


	def onUpdateRoleGem( self, index, attrName, value ):
		"""
		Define method.
		玩家代练经验宝石更新
		"""
		if index < 0:	# 代练宝石
			self.roleTrainGem.onUpdateAttr( attrName, value )
		else:			# 领取经验宝石，index在csdefine中定义
			gem = self.gem_getcomGemByIndex( index )
			if gem is not None:
				gem.onUpdateAttr( attrName, value )


	def isRoleTrainGemActive( self ):
		"""
		判断玩家代练经验宝石是否激活
		"""
		return self.gemActive & csdefine.GEM_ROLE_ACTIVE_FLAG


	def gem_derive( self ):
		"""
		从宝石汲取经验
		"""
		if not self.isRoleTrainGemActive():
			ERROR_MSG( "玩家( %s )经验宝石还没激活，不可汲取经验。" % ( self.getName() ) )
		else :
			self.cell.gem_derive()

	def gem_hire( self, index, remainTime ):
		"""
		租用经验宝石
		"""
		self.cell.gem_hire( index, remainTime )


	def gem_stopTrain( self ):
		"""
		停止代练。
		"""
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活，不需停止代练。" % ( self.getName() ) )
			return
		if not self.roleTrainGem.inTraining():
			self.statusMessage( csstatus.PET_TRAIN_STOP_FAIL_NOT_IN_TRAIN )
			return
		self.cell.gem_stopTrain()


	def gem_startTrain( self, trainType ):
		"""
		开始代练。
		"""
		if not self.isRoleTrainGemActive():
			HACK_MSG( "玩家( %s )经验宝石还没激活。" % ( self.getName() ) )
			return
		self.cell.gem_startTrain( trainType )


	def gem_offload( self, index ):
		"""
		Define method.
		卸下宝石
		"""
		self.statusMessage( csstatus.GEM_OFFLOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_OFFLOAD_ROLE_GEM", index )

	def gem_loadComGem( self, index ):
		"""
		Define method.
		租用经验宝石成功通知
		index : 租用的经验宝石索引
		"""
		self.statusMessage( csstatus.GEM_LOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_LOAD_ROLE_GEM", index )

	def gem_getComGemCount( self ):
		"""
		获得玩家当前领取的经验宝石数量
		"""
		return len( self.roleCommonGem )


	def gem_getcomGemByIndex( self, index ):
		"""
		由index取得相应的comGem
		"""
		comGem = None
		for gem in self.roleCommonGem:
			if gem.index == index:
				comGem = gem
				break
		return comGem


	def set_gemActive( self, oldValue ):
		"""
		"""
	#	self.statusMessage( csstatus.GEM_LOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_EXP_GEM_ACRIVATED" )
		BigWorld.callback( 1, self.showGemPanel )


	def showGemPanel( self ):
		ECenter.fireEvent("EVT_ON_EXP_GEM_SHOW")
#
# $log:v$
#