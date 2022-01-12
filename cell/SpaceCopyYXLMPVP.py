# -*- coding: gb18030 -*-


from bwdebug import *
import BigWorld
import csconst
import Const
from SpaceCopy import SpaceCopy
import csdefine

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10

class SpaceCopyYXLMPVP( SpaceCopy ):
	"""
	Ӣ�����˸���
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.getScript().initPatrolInfo( self )

	def monster_choosePatrolList( self, monsterEntityID ):
		"""
		define method
		ΪNPCѡ��Ѳ��·��
		"""
		patrolListInfo = self.queryTemp( "spacePatrolLists",[] )
		patrolNpcList = self.queryTemp( "spacePatrolNpcList", [] )
		if len( patrolListInfo ) == 0:
			 DEBUG_MSG( "Hero Alliance has no patrolList for NPC( className : %s ) to choose !"% str( monsterEntity.className ) )
			 return
		monsterEntity = BigWorld.entities.get( monsterEntityID )
		if not monsterEntity:
			return
		for e in patrolNpcList:
			if e == monsterEntity.className:
				try:
					patrolList = patrolListInfo[ patrolNpcList.index( e ) ]
				except IndexError :
					ERROR_MSG( "Hero alliance patrolList index %d out of range"%e.index )
					return
				self.beginPatrol( monsterEntity, patrolList )
				break

	def beginPatrol( self, entity, graphID ):
		"""
		���￪ʼѲ��
		"""
		patrolList = BigWorld.PatrolPath( graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Hero alliance patrolList (%s) is not ready or not have such graphID!"%graphID )
			return
		else:
			patrolPathNode, position = patrolList.nearestNode( entity.position )
			entity.patrolPathNode = patrolPathNode
			entity.patrolList = patrolList
			entity.doPatrol( entity.patrolPathNode, entity.patrolList  )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			player.client.onShowYXLMCopyNPCSign( spaceLabel )
		self.recoverPlayerEquips( baseMailbox, params["playerDBID"] )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.client.onCloseYXLMCopyNPCSign()
		self.removePlayerEquips( baseMailbox, params["playerDBID"] )
		if len( self._players ) == 0:					# �رո���
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )

	def onYXLMCopyBossCreated( self, id, className, spawnPos, signType ):
		"""
		Boss������ʱ��,֪ͨ�ͻ������Boss���
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				player.client.onShowYXLMCopyBossSign( id, className, spawnPos, relation, signType )
			except:
				continue

	def onYXLMCopyBossDied( self, id, className, spawnPos, diedPos ):
		"""
		Boss����ʱ��֪ͨ�ͻ��˸���Boss���
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				player.client.onYXLMCopyBossDied( id, className, spawnPos, diedPos, relation )
			except:
				continue

	def updateYXLMCopyBossPos( self, id, className, pos ):
		"""
		����Bossλ����Ϣ
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				player.client.onUpdateYXLMCopyBossPos( id, className, pos, relation )
			except:
				continue
	
	def onYXLMMonsterGetDamage( self, id, flashTime ):
		"""
		�������������ܵ�һ���˺�ʱͼ����˸
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				if relation == csdefine.RELATION_FRIEND:
					player.client.onYXLMMonsterGetDamage( id, flashTime )
			except:
				continue

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
		]
		"""
		return [ 0 ]

	# ----------------------------------------------------------------
	# NPCװ�����ף�����ҹ��򵽵�װ�����ڸ������д洢
	# ���˼���ǣ�
	# 1����ҴӸ����ڵ�NPC����װ��ʱ�����˽�װ������������ϣ�����װ��
	#	�洢������
	# 2��������˳�����ʱ���Ὣװ������������Ƴ������ǲ��Ӹ����Ƴ�
	# 3������ҵ���ʱ��������ϵ�װ�����ᱣ�浽���ݿ⣬��������ڸ�����
	#	���µ�¼ʱ���������ǰ�����װ������װ�����·��͸����
	# 4����������ʱ��װ�����Զ���ʧ
	# ˵����������ϵ�װ�����������ݿ��ԭ���ǣ�����ٴ�������Ҫ�жϸ���
	# �Ƿ��Ѿ����٣�Ȼ���������������½�װ�����ϻ��ǽ�װ���������ڴ���
	# ʵ����û���������ַ�ʽ��ô����
	# ----------------------------------------------------------------
	def onPlayerAddEquip( self, playerDBID, equipItem ) :
		"""
		<Define method>
		��һ��Ӣ�����˵�װ���󣬽�װ�����浽������Ա��ٴε�¼����ʱ�ָ�
		@type	playerDBID : DATABASE_ID
		@param	playerDBID : ��ҵ����ݿ�ID
		@type	equipItem : ITEM
		@param	equipItem : �̳���CItemBase����Ʒʵ��
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID, True )
		equipBag[equipItem.uid] = equipItem

	def onPlayerRemoveEquip( self, playerDBID, equipUid ) :
		"""
		<Define method>
		����Ƴ�Ӣ�����˸�����װ��
		@type	playerDBID : DATABASE_ID
		@param	playerDBID : ��ҵ����ݿ�ID
		@type	equipUid : UID
		@param	equipUid : ��Ʒʵ����UID
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID )
		if equipBag and equipUid in equipBag :
			del equipBag[equipUid]

	def recoverPlayerEquips( self, playerBase, playerDBID ) :
		"""
		�ָ�����ѹ����Ӣ�����˸���װ��
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID )
		if equipBag :
			for equipItem in equipBag.itervalues() :
				playerBase.cell.addYXLMEquip( equipItem )

	def removePlayerEquips( self, playerBase, playerDBID ) :
		"""
		�Ƴ���������ѹ����Ӣ�����˸���װ��
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID )
		if equipBag :
			for equipUid in equipBag.iterkeys() :
				playerBase.cell.removeYXLMEquip( equipUid )

	def getEquipBagOfPlayer( self, playerDBID, createIfNotExist=False ) :
		"""
		"""
		bags = self.queryTemp( "YXLM_EQUIP_BAGS" )
		if bags :
			if playerDBID in bags :
				return bags[playerDBID]
			elif createIfNotExist :
				bags[playerDBID] = {}
				return bags[playerDBID]
		elif createIfNotExist :
			bags = {}
			bags[playerDBID] = {}
			self.setTemp( "YXLM_EQUIP_BAGS", bags )
			return bags[playerDBID]
		return None
	
	def closeYXLMSpace( self ):
		"""
		define method.
		�رյ�ǰ����
		"""
		self.getScript().contents[ -1 ].onContent( self )
	
	def registMonster( self, className, m ):
		"""
		define method.
		ע��һ������
		"""
		self.monsterInfos.add( className, m )
	
	def unRegistMonster( self, className, m ):
		"""
		define method.
		ɾ��һ������
		"""
		self.monsterInfos.remove( className, m )
	
	def sendSAICommand( self, recvIDs, type, sid, sendEntity ):
		"""
		define mthod.
		��ָ����entity����sai
		"""
		for className in recvIDs:
			for m in self.monsterInfos.get( className ):
				m.mailbox.recvSAICommand( type, sid, sendEntity )
