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
	���ս��
	"""
	def __init__( self ):
		self.yiJieFaction = 0    # ս����Ӫ
		self.yiJieAlliance = 0
	
	def yiJieCloseActivity( self, roleInfos ):
		"""
		<define method>
		�����
		"""
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.yiJieLeaveSpace()
		self.client.yiJieReceiveDatas( roleInfos )
	
	def yiJieLeaveSpace( self ) :
		"""
		<define method>
		�뿪ս��,���ս����ֹ���ͣ��뿪ս��ֻ��ͨ�����ô˽ӿ�
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
		ȡ�ø���λ��
		"""
		objScript = g_objFactory.getObject( spaceLabel )
		pos = objScript.getFactionEnterPos( self.yiJieFaction )
		return  pos
	
	def yiJieSetAlliance( self, faction ) :
		"""
		<define method>
		����ս��ͬ��
		"""
		self.yiJieAlliance = faction
	
	def yiJieFactionEnrage( self, isTrue ) :
		"""
		<define method>
		����/���� ��Ӫ��ŭ
		"""
		if isTrue and not self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID ) :
			self.systemCastSpell( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_SKILL_ID )
		elif not isTrue and self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID ) :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_ENRAGE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] ) 
	
	def yiJieMaxRage( self, isTrue ) :
		"""
		<define method>
		����/���� �����ŭ(��˫��ŭ������)
		"""
		if isTrue and not self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID ) :
			self.spellTarget( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_SKILL_ID, self.id )
		elif not isTrue and self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID ) :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] ) 
	
	def yiJieOnEnterAgain( self, faction, alliance ) :
		"""
		<define method>
		���ߺ������ٴν���ս���ص�
		"""
		self.yiJieFaction = faction
		self.yiJieAlliance = alliance
		if self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID ) :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] )
	
	def yiJieCheckShowSignUp( self ) :
		"""
		<define method>
		����Ƿ���ʾ��������
		"""
		objScript = g_objFactory.getObject( SPACE_CLASS_NAME )
		if self.level > objScript.minLevel :
			self.client.yiJieShowSignUp()
	
	def addYiJieZhanChangScore( self, addValue ) :
		"""
		<define method>
		�������ս������
		"""
		self.yiJieZhanChangScore += addValue
	
	def onQueryNeedShowYiJieScore( self, roleInfos ) :
		"""
		<define method>
		��ѯ�Ƿ���ʾ���ְ����ص�
		"""
		self.client.yiJieReceiveDatas( roleInfos )
		for roleInfo in roleInfos :
			if roleInfo.roleName == self.playerName :
				self.yiJieZhanChangScore += roleInfo.score
				return
	
	def canPk( self, entity ) :
		"""
		�ܷ��� entity ���� pk
		"""
		if self.yiJieFaction == entity.yiJieFaction or self.yiJieAlliance == entity.yiJieFaction :
			return False
		else :
			return True
	
	def onDestroy( self ) :
		"""
		�����ٵ�ʱ����������
		ע�⣬��ʱself.isDestroyed��Ȼ��False
		"""
		self.set( "YiJieZhanChang_offlinePlayer", 1 )
	
	def onCellReady( self ) :
		"""
		��cell���ɺ󣬿����ٴ���һЩ����.
		Ʃ��������һЩ���ݸ��ͻ���
		"""
		if self.query( "YiJieZhanChang_offlinePlayer" ) :
			BigWorld.globalData["YiJieZhanChangMgr"].queryNeedShowYiJieScore( self.databaseID, self )
			self.remove( "YiJieZhanChang_offlinePlayer" )
	
	def yiJieOnUniqueSpellArrive( self ) :
		"""
		��˫���ִ�Ŀ��ص�
		"""
		self.getCurrentSpaceBase().cell.onPlayerUseUniqueSpell( self.databaseID )
		if self.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID ) is not None :
			self.removeBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_MAX_RAGE_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE, ] )
	
	def yiJieRequestExit( self ):
		"""
		��������뿪ս��
		"""
		self.setSysPKMode( 0 )
		self.systemCastSpell( csconst.YI_JIE_ZHAN_CHANG_DESERTER_SKILL_ID )	# ���ӱ� buff
		self.getCurrentSpaceBase().cell.playerExit( self.databaseID )
		self.yiJieLeaveSpace()

#******************************************************
# exposed method
#******************************************************
	def yiJieRequestEnter( self, srcEntityID ) :
		"""
		<exposed method>
		��������ȷ�Ͻ�������������NPC
		"""
		if not self.hackVerify_( srcEntityID ) : return
		
		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			# ����
			self.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_IS_DEAD, "" )
			return

		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			# ս��
			self.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_IS_FIGHT, "" )
			return
		
		spaceName, position, direction = YI_JIE_NPC_INFOS
		self.gotoSpace( spaceName, position, direction )
		self.client.yiJieCancelSignUp()
	
	def yiJieUniqueSpellRequest( self, srcEntityID ) :
		"""
		<exposed method>
		�����ͷ���˫��
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.getCurrentSpaceBase().cell.onPlayerRequestUniqueSpell( self.databaseID )
	
