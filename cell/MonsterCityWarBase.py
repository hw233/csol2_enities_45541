# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
from bwdebug import *
from Monster import Monster

class MonsterCityWarBase( Monster ):
	"""
	�����ս�����ݵ㣨��Դ�ݵ㡢ս���ݵ㡢����㡢Ӣ�鱮�����콫��
	"""
	def __init__( self ):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE )
		self.ownerID = 0
		self.getScript().onCreated( self )

	def onActivated( self ):
		"""
		define method
		������
		"""
		self.getScript().onActivated( self )

	def onOccupied( self, belong ):
		"""
		define method
		��ռ��
		"""
		self.belong = belong
		self.getScript().onOccupied( self, belong )
	
	def setOwner( self, ownerID ):
		"""
		define method
		�������ˣ���Ҫ���������Դ�㣩
		@ ownerID:	ownerID, ��Դ����ս���ݵ㸽����������������ܸ���ownerID�ҵ�ս���ݵ��
		"""
		self.ownerID = ownerID
		owner = BigWorld.entities.get( ownerID )
		if not owner:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: I ( %i, %s ) can't get the owner %i " % ( self.id, self.className, ownerID ) )
			return
		owner.registerCityWarBase( self )

	def setBelong( self, belong ):
		"""
		define method
		���ù���
		"""
		self.belong = belong

	def getBelong( self ):
		"""
		define method
		��ѯ����
		"""
		return self.belong

	def registerCityWarBase( self, mailBox ):
		"""
		����Դ�ݵ�ע�ᵽ�Լ�����(��Ҫ�����ս���ݵ�)
		"""
		resourceList = self.queryTemp( "resourceList", [] )
		if mailBox:
			resourceList.append( mailBox )
			self.setTemp( "resourceList", resourceList )

	def getResourceBaseBelong( self, belong ):
		"""
		�����Դ�ݵ�Ĺ������
		��һ��ս���ݵ��������Դ�ݵ�ͬʱ���ڹ��Ƿ������سǷ���������ΪTrue
		"""
		resourceList = self.queryTemp( "resourceList", [] )
		amount = 0
		for resourceMB in resourceList:
			if resourceMB.getBelong() == belong:
				amount += 1
		
		return amount

	def provideEnergy( self ):
		"""
		define method
		��Դ�ݵ��ս���ݵ��ṩ����( ���������İ�᲻ͬ�ͷŲ�ͬ�ļ��� )
		"""
		self.spellTarget( csconst.CITY_WAR_RESOURCE_BASE_SKILL[ self.belong ], self.ownerID )

	def addEnergy( self, casterID, value ):
		"""
		ս���ݵ��������{ belong: value }
		@param value: �����ɸ�
		"""
		caster = BigWorld.entities.get( casterID )
		if not caster or not caster.belong:
			ERROR_MSG( "TONG_CITY_WAR_FINAL:Caster has no belong or I ( %i, %s ) can't get the caster %i " % ( self.id, self.className, casterID ) )
			return
		if caster.belong not in self.energy:
			self.energy[ caster.belong ] = 0
		
		energy = self.energy[ caster.belong ] + value
		self.energy[ caster.belong ] = energy if energy <= 100 else energy % 100
		self.energy = self.energy
		self.onEnergyChanged( caster.belong )

	def onEnergyChanged( self, belong ):
		"""
		δռ��״̬��ս���ݵ����������仯
		"""
		if not self.belong:
			if self.energy[ belong ] > csconst.CITY_WAR_BATTLE_BASE_ACTIVATE_LIMIT:
				self.belong = belong
				self.onOccupied( belong )
		else:
			if self.energy[ belong ] < csconst.CITY_WAR_BATTLE_BASE_ACTIVATE_LIMIT:
				self.cityWarBaseReset()

	def cityWarBaseReset( self ):
		"""
		define method
		����
		"""
		self.getScript().reset( self )

	def onReceiveSpell( self, caster, spell ):
		"""
		��������Ļص�����ĳЩ���⼼�ܵ���

		@param spell: ����ʵ��
		"""
		self.getScript().onReceiveSpell( self, caster, spell )

	def onIncreaseQuestTaskState( self, srcEntityID ):
		"""
		define method.(ֻ��cell�ϱ�����) Ϊ�˹��ü���Spell_313100002�� ���θ÷���
		"""
		pass

	def taskStatus( self, srcEntityID ):
		"""
		Exposed method.
		@param srcEntityID: �����ߵ�ID
		@type  srcEntityID: OBJECT_ID

		�������ӽ��뵽ĳ��ҵ���Ұ������������������������������ҵĹ�ϵ
		"""
		try:
			playerEntity = BigWorld.entities.get( srcEntityID )
		except KeyError:
			INFO_MSG( "TONG_CITY_WAR_FINAL:entity %i not exist in world" % srcEntityID )
			return

		if playerEntity.isReal():
			self.getScript().taskStatus( self, playerEntity )
		else:
			playerEntity.taskStatusForward( self )	#��Դ�����ҿ��ܲ���һ��cell�У�����QuestBox�Ĵ���

	def updateSameBelongs( self, classNames ):
		"""
		define method
		����ͬ�����ľݵ�className
		"""
		self.sameBelongs = classNames
		
	def getOwnerID( self ):
		"""
		����Լ����˵� id
		"""
		return self.ownerID
		
	def getRelationEntity( self ):
		"""
		��ȡ��ϵ�ж�����ʵentity
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		else:
			return owner
		
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner.queryCombatRelation( entity )
		else:
			return csdefine.RELATION_FRIEND