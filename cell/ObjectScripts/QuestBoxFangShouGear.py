# -*- coding: gb18030 -*-
#

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
import csdefine
from bwdebug import *
# ------------------------------------------------
# from cell
from QuestBox import QuestBox
import Const
# ------------------------------------------------

class QuestBoxFangShouGear( QuestBox ) :
	"""
	防守副本机关
	"""
	
	def __init__( self ) :
		QuestBox.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		QuestBox.initEntity( self, selfEntity )
		selfEntity.setTemp( "isStarted", False )
	
	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		法术到达的回调，由某些特殊技能调用
		
		@param spell: 技能实例
		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		# 如果此处检测不通过，则表示玩家对某个物件的动作白做了，暂时还没有好的提示方案。
		if selfEntity.queryTemp( "isStarted", False ) :
			return
		
		selfEntity.setTemp( "isStarted", True )
		currentArea = self.getCurrentFangShouArea( selfEntity.position )
		selfEntity.getCurrentSpaceBase().cell.remoteScriptCall( "onFangShouGearStarting", ( currentArea, ) )
		
		QuestBox.onReceiveSpell( self, selfEntity, caster, spell )
	
	def getCurrentFangShouArea( self, pos ) :
		"""
		获取当前所在防守副本区域
		"""
		z = pos.z
		currentArea = ""
		if z > Const.COPY_FANG_SHOU_AERA_POS_Z_FIRST :
			currentArea = Const.COPY_FANG_SHOU_AREA_FIRST
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_SECOND :
			currentArea = Const.COPY_FANG_SHOU_AREA_SECOND
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_THRID :
			currentArea = Const.COPY_FANG_SHOU_AREA_THRID
		else :
			currentArea = Const.COPY_FANG_SHOU_AREA_FORTH
		return currentArea