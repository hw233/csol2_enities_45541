# -*- coding: gb18030 -*-

# from common
import csdefine

# from cell
import Const
import ECBExtend

CONST_ACTIVITY_PICK_ANIMA_SKILLID = 721038001

class RoleCopyInterface:
	def __init__( self ):
		pass
	
	#---------------------------------------------------
	# 拾取灵气玩法
	#---------------------------------------------------
	def pickAnima_reqStart( self, exposed ):
		"""
		exposed method.
		客户端请求游戏开始
		"""
		if not self.hackVerify_( exposed ):
			return
		
		self.removeAllBuffsBySkillID( Const.ACTIVITY_STOP_MOVE_SKILL, [ csdefine.BUFF_INTERRUPT_NONE, ] )
		self.systemCastSpell( CONST_ACTIVITY_PICK_ANIMA_SKILLID )
	
	def pickAnima_onEnd( self ):
		"""
		define method
		玩法结束
		"""
		spaceCell = self.getCurrentSpaceCell()
		
		if spaceCell:
			spaceCell.onGameOver( self.planesID, self )

		self.removeAllBuffsBySkillID( CONST_ACTIVITY_PICK_ANIMA_SKILLID, [ csdefine.BUFF_INTERRUPT_NONE, ] )
		self.systemCastSpell( Const.ACTIVITY_STOP_MOVE_SKILL ) #定身，不给移动
	
	def pickAnima_confirmQuitSpace( self, exposed ):
		"""
		exposed method.
		客户端请求退出活动面位
		"""
		if not self.hackVerify_( exposed ):
			return
		
		self.removeAllBuffByID( CONST_ACTIVITY_PICK_ANIMA_SKILLID, [ csdefine.BUFF_INTERRUPT_NONE, ] ) #防止错误，进行一次BUFF删除
		self.removeAllBuffsBySkillID( Const.ACTIVITY_STOP_MOVE_SKILL, [ csdefine.BUFF_INTERRUPT_NONE, ] ) #移除定身BUFF
		self.enterPlane( "fu_ben_hai_dao_001" )

	#---------------------------------------------------
	# 防守副本
	#---------------------------------------------------
	def fangShou_addAreaGearStartMark( self, areaName ) :
		"""
		<define method>
		防守副本添加区域机关开启标记
		"""
		self.setTemp( areaName, True )
		self.fangShou_addAreaBuff( areaName )
	
	def fangShou_onEnterCopy( self ) :
		"""
		<define method>
		进入副本
		"""
		checkPosTimer = self.addTimer( 0, Const.COPY_FANG_SHOU_CHECK_POSITION_CYCLE, ECBExtend.COPY_FANG_SHOU_CHECK_ROLE_POSITION_CBID )		# 添加防守副本检测玩家位置 timer
		self.setTemp( "fangShou_checkRolePosTimer", checkPosTimer )
		currentArea = self.fangShou_getCurrentArea()
		self.setTemp( "lastFangShouArea", currentArea )
		for spellID in Const.COPY_FANG_SHOU_BUFF_SPELLS[ Const.COPY_FANG_SHOU_AREA_FORTH ] :
			self.spellTarget( spellID, self.id )						# 进入副本，先添加一个潜能加 100% 的Buff
	
	def fangShou_onLeaveCopy( self ) :
		"""
		<define method>
		离开副本
		"""
		checkPosTimer = self.queryTemp( "fangShou_checkRolePosTimer" ) 
		if checkPosTimer :
			self.cancel( checkPosTimer )													# 撤销防守副本检测玩家位置 timer
		
		for itemID in Const.COPY_FANG_SHOU_SPECAIL_ITEMS :
			count = self.countItemTotal_( itemID )
			self.removeItemTotal( itemID, count, csdefine.DELETE_ITEM_NORMAL )				# 清除此次副本中拾取的特殊道具
		
		for skillID in Const.COPY_FANG_SHOU_CLEAR_BUFF_SPELLS :
			self.spellTarget( skillID, self.id )											# 清空副本增益 Buff
		
		# 移除可能存在的 tempMapping
		for areaName in Const.COPY_FANG_SHOU_BUFF_SPELLS :
			self.removeTemp( areaName )
		self.removeTemp( "fangShou_checkRolePosTimer" )
		self.removeTemp( "lastFangShouArea" )
	
	def onTimer_FangShouCheckRolePos( self, timerID, cbID ) :
		"""
		防守副本检测玩家位置timer回调
		"""
		currentArea = self.fangShou_getCurrentArea()
		if self.queryTemp( "lastFangShouArea" ) == currentArea :
			return
		if self.fangShou_AreaGearStartCheck( currentArea ) :
			self.fangShou_addAreaBuff( currentArea )						# 有区域机关且开启的加上当前区域的 buff
		else :
			self.fangShou_addAreaBuff( Const.COPY_FANG_SHOU_AREA_FORTH )	# 没有区域机关或区域机关未开启的全加上第四区域的 buff
		
		self.setTemp( "lastFangShouArea", currentArea )
	
	def fangShou_getCurrentArea( self ) :
		"""
		获取当前所在防守副本区域
		"""
		z = self.position.z
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
	
	def fangShou_addAreaBuff( self, areaName ) :
		"""
		添加防守区域buff
		"""
		if areaName == Const.COPY_FANG_SHOU_AREA_FORTH :					# 第四区域，需先清空buff
			for spellID in Const.COPY_FANG_SHOU_CLEAR_BUFF_SPELLS :
				self.spellTarget( spellID, self.id )
		
		for spellID in Const.COPY_FANG_SHOU_BUFF_SPELLS[ areaName ] :
			self.spellTarget( spellID, self.id )
	
	def fangShou_AreaGearStartCheck( self, areaName ) :
		"""
		防守副本区域机关是否开启检测
		"""
		return self.queryTemp( areaName, False )
	
	def fangShou_onDestroy( self ) :
		"""
		当销毁的时候做点事情
		注意，此时self.isDestroyed依然是False
		"""
		self.fangShou_onLeaveCopy()