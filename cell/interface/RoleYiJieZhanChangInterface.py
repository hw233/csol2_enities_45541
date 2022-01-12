# -*- coding: gb18030 -*-
#bigworld
import BigWorld
#cell
from ObjectScripts.GameObjectFactory import g_objFactory
#common
import csdefine
import csconst
#locale_default
import csstatus

SPACE_CLASS_NAME = "fu_ben_yi_jie_zhan_chang"

YI_JIE_NPC_INFOS = ( "fengming", ( 119.5, 12.1, 137.5 ), ( 0, 0, 3.0 ) )

class RoleYiJieZhanChangInterface:
	"""
	异界战场
	"""
	def __init__( self ):
		self.yiJieFaction = 0    # 战场阵营
		self.yiJieAlliance = 0
	
	def yiJieCloseActivity( self, roleInfos ):
		"""
		<define method>
		活动结束
		"""
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.yiJieLeaveSpace()
		self.client.yiJieReceiveDatas( roleInfos )
	
	def yiJieLeaveSpace( self ) :
		"""
		<define method>
		离开战场,异界战场禁止传送，离开战场只能通过调用此接口
		"""
		self.yiJieFaction = 0
		self.yiJieAlliance = 0
		self.setSysPKMode( 0 )
		self.yiJieFactionEnrage( False )
		self.yiJieMaxRage( False )
		self.client.yiJieOnExit()
		self.setTemp( "leaveYiJieZhanChang", True )
		self.gotoForetime()
	
	def yiJieGetRevivePosition( self, spaceLabel ):
		"""
		取得复活位置
		"""
		objScript = g_objFactory.getObject( spaceLabel )
		pos = objScript.getFactionEnterPos( self.yiJieFaction )
		return  pos
	
	def yiJieSetAlliance( self, faction ) :
		"""
		<define method>
		设置战场同盟
		"""
		self.yiJieAlliance = faction
	
	def yiJieFactionEnrage( self, isTrue ) :
		"""
		<define method>
		激活/撤销 阵营激怒
		"""
		if isTrue and not self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID ) :
			self.systemCastSpell( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_SKILL_ID )
		elif not isTrue and self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID ) :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] ) 
	
	def yiJieMaxRage( self, isTrue ) :
		"""
		<define method>
		激活/撤销 玩家满怒(无双技怒气点满)
		"""
		if isTrue and not self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID ) :
			self.spellTarget( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_SKILL_ID, self.id )
		elif not isTrue and self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID ) :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] ) 
	
	def yiJieOnEnterAgain( self, faction, alliance ) :
		"""
		<define method>
		下线后重上再次进入战场回调
		"""
		self.yiJieFaction = faction
		self.yiJieAlliance = alliance
		if self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID ) :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] )
	
	def yiJieCheckShowSignUp( self ) :
		"""
		<define method>
		检查是否显示报名界面
		"""
		objScript = g_objFactory.getObject( SPACE_CLASS_NAME )
		if self.level > objScript.minLevel :
			self.client.yiJieShowSignUp()
	
	def addYiJieZhanChangScore( self, addValue ) :
		"""
		<define method>
		增加异界战场积分
		"""
		self.yiJieZhanChangScore += addValue
	
	def onQueryNeedShowYiJieScore( self, roleInfos ) :
		"""
		<define method>
		查询是否显示积分榜界面回调
		"""
		self.client.yiJieReceiveDatas( roleInfos )
		for roleInfo in roleInfos :
			if roleInfo.roleName == self.playerName :
				self.yiJieZhanChangScore += roleInfo.score
				return
	
	def canPk( self, entity ) :
		"""
		能否与 entity 进行 pk
		"""
		if self.yiJieFaction == entity.yiJieFaction or self.yiJieAlliance == entity.yiJieFaction :
			return False
		else :
			return True
	
	def onDestroy( self ) :
		"""
		当销毁的时候做点事情
		注意，此时self.isDestroyed依然是False
		"""
		self.set( "YiJieZhanChang_offlinePlayer", 1 )
	
	def onCellReady( self ) :
		"""
		当cell生成后，可以再此做一些操作.
		譬如主动发一些数据给客户端
		"""
		if self.query( "YiJieZhanChang_offlinePlayer" ) :
			BigWorld.globalData["YiJieZhanChangMgr"].queryNeedShowYiJieScore( self.databaseID, self )
			self.remove( "YiJieZhanChang_offlinePlayer" )
	
	def yiJieOnUniqueSpellArrive( self ) :
		"""
		无双技抵达目标回调
		"""
		self.getCurrentSpaceBase().cell.onPlayerUseUniqueSpell( self.databaseID )
		if self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID ) is not None :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] )
	
	def yiJieRequestExit( self ):
		"""
		玩家主动离开战场
		"""
		self.setSysPKMode( 0 )
		self.systemCastSpell( csconst.YI_JIE_ZHAN_CHANG_DESERTER_SKILL_ID )	# 加逃兵 buff
		self.getCurrentSpaceBase().cell.playerExit( self.databaseID )
		self.yiJieLeaveSpace()

#******************************************************
# exposed method
#******************************************************
	def yiJieRequestEnter( self, srcEntityID ) :
		"""
		<exposed method>
		报名界面确认进入后，请求传送至活动NPC
		"""
		if not self.hackVerify_( srcEntityID ) : return
		
		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# 死亡
			self.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_IS_DEAD, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# 战斗
			self.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_IS_FIGHT, "" )
			return
		
		spaceName, position, direction = YI_JIE_NPC_INFOS
		self.gotoSpace( spaceName, position, direction )
		self.client.yiJieCancelSignUp()
	
	def yiJieUniqueSpellRequest( self, srcEntityID ) :
		"""
		<exposed method>
		申请释放无双技
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.getCurrentSpaceBase().cell.onPlayerRequestUniqueSpell( self.databaseID )
	
