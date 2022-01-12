# -*- coding: gb18030 -*-
#
# $Id: PetTrainer.py,v 1.7 2008-08-01 11:19:59 wangshufeng Exp $

"""
This module implements the pet entity.

2007/07/17 : writen by huangyongwei
2007/10/24 : according to new version document, it is rewriten by huangyongwei
"""

from bwdebug import *
import csstatus
import csconst
import csdefine
import event.EventCenter as ECenter

class PetTrainer :
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		pass

	def ptn_activeCommonGem( self, index, remainTime ) :
		"""
		租用经验宝石

		@param remainTime : 客户端随机生成的租用时间,不超过24小时不小于3小时
		"""
		for gem in self.__commonGems:	# 判断相应index的宝石是否已被租用
			if gem.index == index:
				self.statusMessage( csstatus.PET_GEM_ACTIVATE_FAIL_ACTIVED )
				return
		if self.ptn_getComGemCount() + self.gem_getComGemCount() >= csconst.GEM_COUNT_UPPER:
			#self.statusMessage(),已达到所能租用的上限
			return
		self.cell.ptn_hireCommonGem( index, remainTime )


	def ptn_inactiveCommonGem( self, index ):
		"""
		中止租用经验宝石
		"""
		if not self.isPetTrainGemActive():
			return
		self.cell.ptn_inactivateCommonGem( index )


	# -------------------------------------------------
	def ptn_getTrainGem( self ) :
		return self.__trainGem

	def ptn_getCommonGems( self ) :
		gems = []
		for gem in self.__commonGems :
			gems.append( gem )
		return gems


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def ptn_onUpdateGemAttr( self, index, attrName, value ) :
		"""
		Define method.
		宝石属性更新的统一接口
		"""
		if index < 0 :
			self.__trainGem.onUpdateAttr( attrName, value )
		else :
			gem = self.ptn_getcomGemByIndex( index )
			if gem is not None:
				gem.onUpdateAttr( attrName, value )


	def ptn_loadComGem( self, index ):
		"""
		Define method.
		租用经验宝石成功通知

		index : 租用的经验宝石索引
		"""
		self.statusMessage( csstatus.GEM_LOAD_COMMON )
		ECenter.fireEvent( "EVT_ON_LOAD_PET_GEM", index )


	def ptn_offloadComGem( self, index ):
		"""
		Define method.
		卸下经验宝石的通知
		"""
		ECenter.fireEvent( "EVT_ON_OFFLOAD_PET_GEM", index )


	def ptn_getComGemCount( self ):
		"""
		public
		获得当前玩家的加成经验宝石个数
		"""
		return len( self.__commonGems )


	def isPetTrainGemActive( self ):
		"""
		判断宠物经验宝石是否激活
		"""
		return self.gemActive & csdefine.GEM_PET_ACTIVE_FLAG


	def ptn_getcomGemByIndex( self, index ):
		"""
		由index取得相应的comGem
		"""
		comGem = None
		for gem in self.__commonGems:
			if gem.index == index:
				comGem = gem
				break
		return comGem

	def getPetGemExp( self ):
		"""
		获取宝石上的经验值
		"""
		return self.__trainGem.EXP



#
# $Log: not supported by cvs2svn $
#
#
#