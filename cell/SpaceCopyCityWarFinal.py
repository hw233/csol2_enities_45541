# -*- coding: gb18030 -*-

import time
import Const
import csdefine
import csstatus
import cschannel_msgs
from bwdebug import *
from SpaceCopy import SpaceCopy
from TongCityWarInfos import TongCityWarInfo

CITY_WAR_BATTLE_BASE_SKILL	= { '20322222':{ 1: 1, 2: 2 },
								'20322223':{ 1: 1, 2: 2 },
								'20322224':{ 1: 1, 2: 2 },
								'20322225':{ 1: 1, 2: 2 }, }		# { ս���ݵ�className:{ ��Դ�����������ID } }
WAIT_BATTLE_FIELD_RESET_TIME		= 60 * 3								# ս������ʱ��
ROLE_DIED_ITERGRATION				= 10

class SpaceCopyCityWarFinal( SpaceCopy ):
	"""
	�����ս����
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.baseInfos = {}					# { baseType: [ mailBox:belong, ] }
		self.resetTimer = 0
		self.teleportBases = {}				# �д��͹��ܵľݵ� { mailBox:className, }
		self.initBattleField()
		self.msgs = []						# Ҫ���͵���Ϣ { "times": ������ "msg": ( msgKey, *args ), "timerID": 1 }

	def initBattleField( self ):
		"""
		��ʼ��ս������
		"""
		self.tongInfos = self.params[ "tongInfos"]	# ���в������ { "defend":[ ]}
		self.defend = self.params[ "defend" ]
		self.attack = self.params[ "attack" ]
		self.activatedBattleBase = []				# ���������ս���ݵ㣨 ս���ݵ㱻���� = ��ռ�� ��
		self.flagGuardDamageRecord = {}				# ���콫�˺�ͳ��
		self.diedFlagGuard = []						# ��ɱ���Ļ��콫
		for tongDBID in [ self.defend, self.attack ]:
			warInfo = TongCityWarInfo()
			warInfo.init( tongDBID )
			self.warInfos.infos[ tongDBID ] = warInfo

	def onEnterCommon( self, baseMailbox, params ):
		"""
		����ռ�
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Role %i enter space, params is %s " % ( baseMailbox.id, params ) )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "roleDBID" ]
		roleName = params[ "roleName" ]

		warDict = {}
		# Ϊ�˸��ýӿ�tong_onEnterCityWarSpace��left��ʾ���Ƿ���right��ʾ�سǷ�
		warDict[ "left" ] = self.defend
		warDict[ "leftTongName" ] = self.tongInfos[ "defend" ][ self.defend ][ "tongName"]
		warDict[ "right" ] = self.attack
		warDict[ "rightTongName" ] = self.tongInfos[ "attack" ][ self.attack ][ "tongName" ]
		
		dict = {}
		dict[ "left" ] = {}
		dict[ "right" ] = {}
		for key, item in self.tongInfos.iteritems():
			for tDBID in item.keys():
				if key == 'defend':
					dict[ "left" ][ tDBID ] = item[ tDBID ][ "tongName" ]
				else:
					dict[ "right" ][ tDBID ] = item[ tDBID][ "tongName" ]
		warDict[ "tongInfos" ] = dict
		baseMailbox.client.tong_onEnterCityWarSpace( int( BigWorld.globalData[ "TONG_CITY_WAR_FINAL_END_TIME" ] - time.time() ), warDict )
		
		self.warInfos.addMember( tongDBID, roleDBID, roleName, baseMailbox )
		self.addBelongBuff( tongDBID, baseMailbox )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�뿪�ռ�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "databaseID" ]
		self.warInfos.leaveMember( tongDBID, roleDBID )
		BigWorld.globalData[ "TongManager" ].cityWarFinalLeave( self.params[ "uidKey"], tongDBID, roleDBID )

	def addBelongBuff( self, tongDBID, baseMailbox ):
		"""
		���Buff������ռ���ս���ݵ㲻ͬ��Ӳ�ͬ��Buff
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Role %i, tong %i add buff on enter space." % ( baseMailbox.id, tongDBID ))
		belong = self.getTongBelong( tongDBID )
		if not belong:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: tong %i belong to None" % ( tongDBID ))
			return
		
		occupiedBattleBase = self.getOccupiedBattleBase( belong)
		if not occupiedBattleBase:
			return
		
		for className, amount in occupiedBattleBase.iteritems():
			skillID = CITY_WAR_BATTLE_BASE_SKILL[ className ][ amount ]
			baseMailbox.cell.spellTarget(  skillID, baseMailbox.id )

	def spellBuffAllPlayer( self, skillID, belong ):
		"""
		��������ʩ��һ��Buff
		"""
		for tongDBID, info in self.warInfos.infos.iteritems():
			tongBelong = self.getTongBelong( tongDBID )
			if tongBelong != belong:
				continue
			for roleDBID, member in info.members.iteritems():
				roleMB = member.mailBox
				role = BigWorld.entities.get( roleMB.id )
				if role:
					role.spellTarget( skillID, role.id )
				else:
					roleMB.cell.spellTarget( skillID, roleMB.id )

	def getTongBelong( self, tongDBID ):
		"""
		��ȡ���ID�Ĺ��������Ƿ������سǷ���
		"""
		for key, item in self.tongInfos.iteritems():
			if tongDBID in item.keys():
				if key == "defend":
					return csdefine.CITY_WAR_FINAL_FACTION_DEFEND
				if key == "attack":
					return csdefine.CITY_WAR_FINAL_FACTION_ATTACK
		return 0
	
	# ---------------------------- �ݵ㴦�� -----------------------------------------
	def onCityWarBaseCreated( self, baseMB, baseType, belong, className ):
		"""
		define method
		�ݵ㴴��
		@param mailBox: 	�ݵ�mailBox
		@param baseType:	�ݵ�����
		@param belong:		����״̬
		"""
		dict = {}
		dict[ baseMB ] = belong
		if baseType not in self.baseInfos:
			self.baseInfos[ baseType ] = []
		if baseType == csdefine.CITY_WAR_FINAL_BASE_HEROMONU:	# Ӣ�鱮ֻ�������µĴ���ʱ�����
			self.baseInfos[ baseType ] = []
		self.baseInfos[ baseType ].append( dict )
		if baseType in [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG, csdefine.CITY_WAR_FINAL_BASE_HEROMONU ]:
			if baseMB not in self.teleportBases:
				self.teleportBases[ baseMB ] = ""
			self.teleportBases[ baseMB ] = className 

	def updateBaseBelong( self, baseType, baseID, belong ):
		"""
		���¾ݵ����
		"""
		for item in self.baseInfos[ baseType ]:
			for mb in item.keys():
				if baseID == mb.id:
					item[ mb ] = belong
		
		if baseType == csdefine.CITY_WAR_FINAL_BASE_BATTLE:		# �ж��Ƿ�Ҫ��������
			if baseID not in self.activatedBattleBase:
				self.activatedBattleBase.append( baseID ) 
			if not self.queryTemp( "FLAG_ACTIVATED", False ):	# �����δ������
				if len( self.activatedBattleBase ) == len( self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_BATTLE ] ):
					self.activeFlag()
		
		if baseType in [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG, csdefine.CITY_WAR_FINAL_BASE_HEROMONU ]:	# ����ͬ��Ӫ�ݵ���Ϣ
			self.updateBaseBelongsInfo( baseID, belong )

	def spawnCityWarBase( self, type, belong ):
		"""
		ˢ��ָ�����͵ľݵ�
		"""
		params = {}
		params[ "monsterType" ] = type
		params[ "belong"] = belong
		self.base.spawnMonster( params )

	def updateBaseBelongsInfo( self, baseID, newBelong ):
		"""
		����ͬ��Ӫ�ݵ���Ϣ( ������ )
		"""
		types = [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG ]
		baseClassNames = []
		for type, item in self.baseInfos.iteritems():
			if type not in types:
				continue
			for info in item:
				for mb, belong in info.iteritems():
					if belong == newBelong:
						baseClassNames.append( self.teleportBases[ mb ] )
		
		for baseMB, className in self.teleportBases.iteritems():
			if className in baseClassNames:
				baseMB.cell.updateSameBelongs( baseClassNames )

	# ---------------------------- ��Դ�ݵ� -----------------------------------------
	def onRoleOccupyResource( self, casterID, resourceMB ):
		"""
		define method
		���ռ����Դ��( ʰȡռ�� )
		"""
		caster = BigWorld.entities.get( casterID )
		if not caster:
			return
		belong = self.getTongBelong( caster.tong_dbID )
		resourceMB.onOccupied( belong )

	def onResourceBaseOccupied( self, baseType, baseID, ownerID, belong ):
		"""
		define method
		��Դ�ݵ㱻ռ��
		"""
		self.updateBaseBelong( baseType, baseID, belong )
		
		owner = BigWorld.entities.get( ownerID )
		if not owner:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: Can't get the owner %i " % ( ownerID ) )
			return

		if not owner.belong:
			return
		amount = owner.getResourceBaseBelong( owner.belong )
		if amount > 0:
			self.onBattleSubResourceChanged( owner.className, amount, owner.belong )
			return

		if owner.getResourceBaseBelong( belong ) == 2:
			self.onBattleSubResourceChanged(  owner.className, 2, belong )

	def onBattleSubResourceChanged( self,className, amount, belong ):
		"""
		��Դ��ռ�췢���仯
		"""
		skillID = CITY_WAR_BATTLE_BASE_SKILL[ className ][ amount ]
		self.spellBuffAllPlayer( skillID, belong )

	# ---------------------------- ս���ݵ� -----------------------------------------
	def onBattleBaseOccupied( self, baseType, baseID, className, belong, amount ):
		"""
		define method
		ս���ݵ㱻ռ��
		"""
		self.updateBaseBelong( baseType, baseID, belong )
		skillID = CITY_WAR_BATTLE_BASE_SKILL[ className ][ amount ]
		self.spellBuffAllPlayer( skillID, belong )

	def getOccupiedBattleBase( self, belong ):
		"""
		��ȡ������ռ���ս���ݵ�{ �ݵ�className: ���� }
		"""
		occupiedBattleBase = {}
		if not csdefine.CITY_WAR_FINAL_BASE_BATTLE in self.baseInfos:
			return
		for item in self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_BATTLE ]:
			for mb, value in item.iteritems():
				if value == belong:
					battleBase = BigWorld.entities.get( mb.id )
					if not battleBase:
						continue
					if battleBase.className not in occupiedBattleBase.keys():
						occupiedBattleBase[ battleBase.className ] = 0
					occupiedBattleBase[ battleBase.className ] += 1
		
		return occupiedBattleBase
	
	# ----------------------------- ����㡢���콫 ----------------------------------
	def activeFlag( self ):
		"""
		��������
		"""
		self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_FLAG_ACTIVATED, "" )
		flagMB = self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG ][0].keys()[0]
		flagMB.cell.onActivated( )

	def onFlagActivated( self, baseType ):
		"""
		define method
		�����֪ͨspace�Լ��Ѿ�������,ˢ�»��콫
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base has benn activated, begin to notify base spawn flagGuard!")
		self.setTemp( "FLAG_ACTIVATED", True )
		belong = csdefine.CITY_WAR_FINAL_FACTION_NONE
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD, belong )

	def onBaseFlagOccupied( self, baseType, baseID, belong ):
		"""
		define method
		����㱻ռ��
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base has benn occupied by %i!" % belong )
		self.updateBaseBelong( baseType, baseID, belong )
		self.setTemp( "FLAG_OCCUPANT", belong )
		# ����ˢ���콫
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD, belong )
		if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
			self.activeHeroMonu()

	def recordFlagGuardDamage( self, guardID, killerID, damage ):
		"""
		define method
		��¼���콫���˺�( ֻ��Ҫ��¼ĳһ�������˺�������Ҫ��¼�����˸����콫��ɵ��˺� )
		"""
		killer = BigWorld.entities.get( killerID )
		if not killer:
			return
		belong = self.getTongBelong( killer.tong_dbID )
		
		if belong not in self.flagGuardDamageRecord:
			self.flagGuardDamageRecord[ belong ] = 0
		self.flagGuardDamageRecord[ belong ] += damage

	def onFlagGuardDied( self, guardID, integral, killerID ):
		"""
		define method
		���콫����
		"""
		self.diedFlagGuard.append( guardID )
		
		guardNum = len( self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD] )
		if len( self.diedFlagGuard ) == guardNum:
			self.onAllFlagGuardDied( killerID )
		
		killer = BigWorld.entities.get( killerID )
		if not killer:
			return

		self.addIntegral( killer.tong_dbID, integral )

	def onAllFlagGuardDied( self, killerID ):
		"""
		���л��콫�Ѿ�����
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: All flag guard has benn died!")
		self.diedFlagGuard = []
		self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD ] = []
		flagMB, belong = self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG ][0].iteritems().next() 
		
		# �����δ��ռ�죬���ݶԻ��콫��ɵ��˺�ͳ�Ƽ������
		if not belong:
			DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base is not occupied, cal top damage!")
			flagMB.cell.onOccupied( self.getTopDamageBelong() )
			return
		
		# ����㱻ռ�죬ֻ��Ҫɱ���Է����콫�Ϳ�����������
		killer = BigWorld.entities.get( killerID )
		if killer:
			newBelong = self.getTongBelong( killer.tong_dbID )
			DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base has been occupied, old belong is %i, new is %i!" % ( belong, newBelong ) )
			flagMB.cell.onOccupied( newBelong )

	def getTopDamageBelong( self ):
		"""
		��ȡ�˺���ߵİ��
		"""
		maxDamge = max( self.flagGuardDamageRecord.values() )
		for belong,damage in self.flagGuardDamageRecord.iteritems():
			if damage == maxDamge:
				return belong

	# ----------------------------- Ӣ�鱮 ------------------------------------------
	def activeHeroMonu( self ):
		"""
		����Ӣ�鱮��Ӣ�鱮�洢����ˢ�µ�baseMB��
		"""
		self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_HERO_MONU_ACTIVATED, "" )
		heroMonuMB = self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_HEROMONU ][0].keys()[0]
		heroMonuMB.cell.onActivated( )

	def onHeroMonuDied( self, monuID, killerID ):
		"""
		define method
		Ӣ�鱮����
		"""
		killer = BigWorld.entities.get( killerID )
		if not killer:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: HeroMonu %i died, but can't get killer %i " % ( monuID, killerID) )
			return
		
		belong = self.getTongBelong( killer.tong_dbID )
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: HeroMonu has been killed by %i, belong is %i" % ( killerID, belong ) )
		# ����Ӣ�鱮
		self.reviveHeroMonu( belong )
		self.onHeroMonuOccupied( csdefine.CITY_WAR_FINAL_BASE_HEROMONU, monuID, belong, killer.tongName )

	def reviveHeroMonu( self, belong ):
		"""
		����Ӣ�鱮��ָ��������
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Reveive HeroMonu , belong is %i" % belong )
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_BASE_HEROMONU, belong )

	def onHeroMonuOccupied( self, baseType, monuID, belong, tongName ):
		"""
		Ӣ�鱮��ռ��
		"""
		self.updateBaseBelong( baseType, monuID, belong )
		
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: HeroMonu has benn occupied by tong %s, belong %i, resetTimer %i" % ( tongName, belong, self.resetTimer ) )
		if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK and not self.resetTimer:
			self.onConditionChange( {} )
			self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_HERO_MONU_OCCUPIED, str( ( tongName, WAIT_BATTLE_FIELD_RESET_TIME / 60 ) ) )
			DEBUG_MSG( "TONG_CITY_WAR_FINAL:Start battle field reset timer !")
		else:
			self.baseOccupiedNotice( baseType, cschannel_msgs.CITY_WAR_FINAL_HERO_MONU, belong )

	def battleFieldReset( self ):
		"""
		Ӣ�鱮�����Ƿ�ռ�죬ս������
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Battle field reset!")
		self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_BATTLE_FIELD_RESET, "" )
		self.getHeroMonuOccupationReward() 			# ����ռ��Ӣ�鱮��õĻ��ֽ���
		BigWorld.globalData[ "TongManager" ].requestBattleFieldReset( self.params[ "uidKey" ] )	# ֪ͨ������ս������
		self.resetCityWarFinalBase()				# �������оݵ�����
		self.resetBattleField()						# ����ս������
		self.teleportPlayerToBelongBase()			# ��������Ҵ��͵�������������
		self.resetSpaceDatas()

	def getHeroMonuOccupationReward( self ):
		"""
		�ɹ�ռ��Ӣ�鱮����Ի���سǷ���ǰ���ֵ�10%������Ϊ����
		"""
		defendIntegral = 0
		for tongDBID in self.tongInfos[ "defend" ]:
			defendIntegral += self.warInfos.getIntegral( tongDBID )
		if self.attack:
			self.addIntegral( self.attack, int( defendIntegral * 0.1 ) )

	def resetBattleField( self ):
		"""
		����ս��
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: begin to reset battle field datas!")
		oldDefend= self.defend
		self.defend = self.attack
		self.attack = oldDefend
		self.getScript().resetTongInfos( self )

	def resetCityWarFinalBase( self ):
		"""
		�������оݵ�
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: begin to reset cityWarBase info!")
		for type, baseList in self.baseInfos.iteritems():
			if type in [ csdefine.CITY_WAR_FINAL_BASE_RESOURCE, csdefine.CITY_WAR_FINAL_LIGHT_WALL ]:	# ��Դ�ݵ�ͨ��ս���ݵ�ȥ֪ͨ����
				continue
			for item in baseList:
				for mb in item.keys():
					mb.cell.cityWarBaseReset()

	def teleportPlayerToBelongBase( self ):
		"""
		��������Ҵ��͵�������������
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: begin to teleport role to belong spawnPos!")
		self.getScript().teleportPlayerToBelongBase( self )

	def resetSpaceDatas( self ):
		"""
		���ÿռ�����( ���콫�����ٴ��� )
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL:  Reset space datas!")
		self.diedFlagGuard = []
		self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD ] = []
		self.resetTimer = 0

	# ----------------------------- ���ִ��� ----------------------------------------
	def addIntegral( self, tongDBID, integral, belongVal = 0 ):
		"""
		define method
		��ӻ���
		@param belongVal: ͨ��AI��ӻ��ִ������belongֵ����1��2���������ط���
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: %i add integral %i " % ( tongDBID, integral ) )
		if self.queryTemp( "BATTLE_FIELD_RESET", False ):		# ս�������ڼ䣬���������
			return
		belong = belongVal
		if tongDBID:
			belong = self.getTongBelong( tongDBID )
		
		if not belong:
			return
		
		if self.queryTemp( "FLAG_OCCUPANT", 0 ) == belong:		# ռ�����㣬���ַ���
			integral = integral * 2
		
		if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
			tongDBID = self.attack
		else:
			tongDBID = self.defend
		
		self.warInfos.addIntegral( tongDBID, integral )

	def onRoleBeKill( self, killerTongDBID, killerDBID, deaderTongDBID, deaderDBID ):
		"""
		define method
		����ұ���ɱ��ص�
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: ( Role %i, tong %i ) has been killed by ( Role %i, tong %i )" % ( deaderDBID, deaderTongDBID, killerDBID, killerTongDBID ))
		if killerDBID != 0:
			self.warInfos.addKill( killerTongDBID, killerDBID ) # ��ӻ�ɱ����
		
		self.warInfos.addDead( deaderTongDBID, deaderDBID ) # �����������
		self.addIntegral( killerTongDBID, ROLE_DIED_ITERGRATION )  # ��Ӱ�����

	def onRoleRelive( self, mailbox, tongDBID ):
		"""
		define method
		���ս������
		"""
		self.getScript().onRoleRelive( self, mailbox, tongDBID )

	def onCityWarFinalEnd( self ):
		"""
		define method
		���ս�����
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: TongManager infos to close space!")
		self.setTemp( "BATTLE_FIELD_RESET", True )		# ֹͣ�������
		self.calFinalIntegration()		# �������ջ���
		self.getScript().closeSpace( self )

	def calFinalIntegration( self ):
		"""
		�������
		"""
		integrations = []
		for tongDBID in [ self.attack, self.defend ]:
			dict = { "tongDBID" : tongDBID, "integral": self.warInfos.getIntegral( tongDBID ), "date": int(time.time()) }
			integrations.append( dict )
		
		DEBUG_MSG( "TONG_CITY_WAR_FINAL:Activity end, cal integration %s! winner %i" % ( integrations, self.warInfos.winner ) )
		BigWorld.globalData[ "TongManager" ].onGetCityWarFinalRecords( self.params[ "uidKey" ], integrations, self.warInfos.winner )

	def destroyLightWall( self ):
		"""
		���ٹ�ǽ( �����洢���ǹ�ǽ��ˢ�µ��base )
		"""
		for spawnList in  self.baseInfos[ csdefine.CITY_WAR_FINAL_LIGHT_WALL ]:
			for spMB, belong in spawnList.iteritems():
				spMB.cell.remoteCallScript( "destroySpawnMonster", [] )

	def spawnLightWall( self ):
		"""
		ˢ�¹�ǽ
		"""
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_LIGHT_WALL, 0 )

	def baseOccupiedNotice( self, baseType, baseName, belong ):
		"""
		define method
		�ݵ㱻ռ��֪ͨ
		"""
		if baseType == csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD:
			if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
				msg = csstatus.TONG_CITY_WAR_FINAL_FLAG_GUARD_DIED1
			else:
				msg = csstatus.TONG_CITY_WAR_FINAL_FLAG_GUARD_DIED2
		else:
			if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
				msg = csstatus.TONG_CITY_WAR_FINAL_BASE_OCCUPIED1
			else:
				msg = csstatus.TONG_CITY_WAR_FINAL_BASE_OCCUPIED2
		
		self.getScript().statusMessageAllPlayer( self, msg, str( ( baseName, ) ) )
