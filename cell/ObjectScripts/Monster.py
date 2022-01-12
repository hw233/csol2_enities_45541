# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.64 2008-09-04 07:45:07 kebiao Exp $

"""
����NPC����
"""
import math
import Math
from NPCObject import NPCObject
import Language
from bwdebug import *
import LostItemDistr
import items
import random
import ItemTypeEnum
import csdefine
import csconst
import BigWorld
import time
import csstatus
import Resource.AIData
import ECBExtend
import Const
from NPCBaseAttrLoader import NPCBaseAttrLoader					# ��������������Լ�����
from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader	# NPC�����������Ʒ���ñ�
from MonsterIntensifyPropertyData import MonsterIntensifyPropertyData
from ItemSystemExp import ItemTypeAmendExp
from Resource.BigWorldLevelMaps import BigWorldLevelMaps
from MonsterDropManager import MonsterDropManager
from LevelEXP import AmendExp
from DaohengLoader import DaohengLoader
from MsgLogger import g_logger
from Domain_Fight import g_fightMgr
from Resource.AI.AIBase import AIBase
from ObjectScripts.GameObjectFactory import g_objFactory
from interface.CombatUnit import CombatUnit

g_items = items.instance()
g_npcQuestDroppedItems = NPCQuestDroppedItemLoader.instance()
g_aiDatas = Resource.AIData.aiData_instance()
g_npcaiDatas = Resource.AIData.NPCAI_instance()
g_monsterIntensifyAttr = MonsterIntensifyPropertyData.instance()
g_produceMin = 3	# ����Ʒ��С���ܴ���
g_produceMax = 5	# ����Ʒ�����ܴ���
g_BigWorldLevelMaps = BigWorldLevelMaps.instance()		# �����ͼ��Ӧ�Ĺ��Ｖ����Ϣ
g_monsterdropmanager = MonsterDropManager.instance()	# �������
g_daoheng = DaohengLoader.instance()			# ����

ITEMS_BOX_ID = 40301001
class Monster(NPCObject):
	"""
	����NPC��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )
		# �洢������������ͬ��ʶ����ʵ�������ڴ���entityʱ�Ӵ��б������ѡ����Ҫ������
		# key == level; value == instance of Monster
		self.equips = {}						# �����װ���б�key == order, value == itemID
		self.aiData	= {}						# �����AI���ݱ�
		self._expRate = 0.0						# ���ﾭ����ʵļ���
		self._daohengRate = 0.0                 # �����ɱ���н������ʵļ���
		self._campMoraleRate = 0.0				# ��Ӫʿ���������ʵļ���
		self._daohengAtt = 0.0                  # ����������Ա��ʵļ���
		self.callList = []						# ����ͬ��� [npcid,...]
		self.attrAIDefLevel = 0					# �����Ĭ��AI�ȼ�
		self.prestige = []						# ��ɱ�������ǿɻ�õ�����ֵ��[ (id, value), ...]; id == ����������value == ���ӵ�����
		self.hasPreAction = 0					# ����ĳ������� Ĭ����0
		self.isMovedAction = 0					# �����Ƿ��λ�Ƴ���
		self.preActionTime = 0					# ���������������ʱ��
		self.jumpPoint = None
		self.jumpPointType = 0
		self.comboAITable = {}					# ����AI
		self.comboAIActivate = 0				# ����AIִ�и���
		self.isComboAILoaded = 0				# ����AI�Ƿ����

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPCObject.onLoadEntityProperties_( self, section )

		# �Ա�ְҵ�����塢����
		raceclass = 0
		#raceclass += section.readInt( "gender" )			# ��ʱ���Դ˹��ܣ�ȫ��Ĭ��Ϊ�У���Ϊ�߻��ⲿ����ʱû����
		raceclass |= section.readInt( "class" ) << 4
		raceclass |= section.readInt( "race" ) << 8
		raceclass |= section.readInt( "faction" ) << 12
		raceclass |= section.readInt( "camp" ) << 20
		self.setEntityProperty( "raceclass", raceclass )
		self.setEntityProperty( "level", section.readInt( "level" ) )
		self._expRate = section.readFloat( "expRate" )
		self._accumRate = section.readFloat( "accumRate" )		# ����ֵ����
		self._potentialRate = section.readFloat( "potentialRate" )
		self.setEntityProperty( "baseAtt", section.readFloat( "baseAtt" ) )
		self.setEntityProperty( "excAtt", section.readFloat( "excAtt" ) )
		#���õ���ֵ
		self._daohengAtt = section.readFloat( "daohengAtt" )
		self._daohengRate = section.readFloat( "daohengRate" )
		
		if section.has_key( "campMoraleRate" ):
			self._campMoraleRate = section.readFloat( "campMoraleRate" )
		
		# AI
		#self.setEntityProperty( "attackSkill",				section.readInt("attackSkill") )				# �������ܣ��޴˼���ʱΪ������
		if section.has_key( "walkPath" ):
			self.setEntityProperty( "walkPath",				eval(section.readString("walkPath")) )			# Ѳ��·��
		if section.has_key( "initiativeRange" ):
			self.setEntityProperty( "initiativeRange",		section["initiativeRange"].asInt )				# ����������Χ
		#self.setEntityProperty( "range_base",				int( section["range_base"].asFloat * csconst.FLOAT_ZIP_PERCENT ) )					# �����������ֵ
		self.setEntityProperty( "viewRange",				section["viewRange"].asInt )					# ��Ұ��Χ������������Χ��
		self.setEntityProperty( "territory",				section["territory"].asInt )					# ����Χ��׷����Χ��
		if section.has_key( "petName" ):
			self.setEntityProperty( "petName",				section["petName"].asString )					# ��������
		if section.has_key( "callRange" ):
			self.setEntityProperty( "callRange",			section["callRange"].asInt )					# ����ͬ�鷶Χ
		self.attrAIDefLevel = section.readInt("attrAIDefLevel")
		
		if section.has_key( "battleCamp" ):
			self.setEntityProperty( "battleCamp",			section["battleCamp"].asInt )					# ��Ӫ
		if section.has_key( "hasPreAction" ):
			self.hasPreAction = section.readInt( "hasPreAction" )										# �볡����
		if section.has_key( "isMovedAction" ):
			self.isMovedAction = section.readInt( "isMovedAction" )										# �볡�����Ƿ���λ��
		if section.has_key( "preActionTime" ):
			self.preActionTime = section.readFloat("preActionTime")										# �볡��������ʱ��
		if section.has_key( "jumpPointType" ):
			self.jumpPointType = section.readInt( "jumpPointType" )										# ��ص�����
		if section.has_key( "jumpPoint" ):
			self.jumpPoint = section.readString("jumpPoint") 											# ��ص�Ϊ�̶�λ��ʱ�������
			
		#if section.has_key( "accumPoint" ):
		#	self.setEntityProperty( "accumPoint",			section["accumPoint"].asInt )					# ����ֵ
			
		#self.setEntityProperty( "randomWalkRange",			section["randomWalkRange"].asFloat )			# ������߷�Χ
		#self.setEntityProperty( "fleePercent",				section["fleePercent"].asInt )					# ���ܻ��ʷ�Χ

		# phw: ����AI���д�Ķ������ڲ��Բ�������д������ݣ����ֻ��ʹ��Ĭ��ֵ��
		#self.setEntityProperty( "attackSkill",				1 )				# �������ܣ��޴˼���ʱΪ��������2 Ϊ�������ͨ������
		#self.setEntityProperty( "range_base",				2.0 )			# �����������ֵ
		#self.setEntityProperty( "viewRange",				50.0 )			# ��Ұ��Χ������������Χ��
		#self.setEntityProperty( "territory",				30.0 )			# ����Χ��׷����Χ��
		#self.setEntityProperty( "callRange",				0.0 )			# ����ͬ�鷶Χ
		#self.setEntityProperty( "randomWalkRange",			3.0 )			# ������߷�Χ
		#self.setEntityProperty( "initiativeRange",			0.0 )			# ����������Χ
		#self.setEntityProperty( "fleePercent",				0 )				# ���ܻ��ʷ�Χ

		# ����ģ����ʾ���
		"""
		modelNumber = section.readString( "lefthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "lefthandNumber", modelNumber )

		modelNumber = section.readString( "righthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "righthandNumber", modelNumber )
		"""
		self._lefthandNumbers = []
		self._righthandNumbers = []
		if section.has_key( "lefthandNumber" ):
			self._lefthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["lefthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "righthandNumber" ):
			self._righthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["righthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "callList" ):
			for item in section[ "callList" ].values():
				self.callList.append( item.asString )
		if section.has_key( "isNotifyDie" ):
			self.setEntityProperty( "isNotifyDie",			section["isNotifyDie"].asInt )					# ֪ͨ��������ʱ����
			
		if section.has_key( "relationMode" ):
			self.setEntityProperty( "relationMode", section[ "relationMode" ].asInt )					# ս����ϵģʽ
		else:
			self.setEntityProperty( "relationMode", 0 )					# ս����ϵģʽ
			
		if section.has_key( "isUseCombatCamp" ):
			self.setEntityProperty( "isUseCombatCamp", section[ "isUseCombatCamp" ].asInt )					# �Ƿ�����ս����Ӫ
		else:
			self.setEntityProperty( "isUseCombatCamp", 0 )
			
		if section.has_key( "combatCamp" ):
			self.setEntityProperty( "combatCamp", section[ "combatCamp" ].asInt )							# ս����Ӫ
		
		# ��¼��С�����ȼ�������ʱ������С�����ȼ��������
		self.minLv = section.readInt("minLv")
		self.maxLv = section.readInt("maxLv")

		self.mapPetID = section.readString( "petID" )
		self.takeLevel = section.readInt( "takeLevel" )
		
		self.petInbornSkills = []
		self.petInbornSkillRate = 0.0
		petInbornSkills = section.readString( "petInbornSkills" )
		if petInbornSkills != "":
			self.petInbornSkills = [int( skillID ) for skillID in petInbornSkills.split( ";" )]
			# ���ÿһ�����＼�ܵĸ��ʣ����ԭ����1000����������һ������ȫ�츳���ܣ��������������츳���ܵ�
			# ����Ϊ1/1000������ÿһ���츳���ܵĸ�����0.001 ** ( 1.0/�����츳���ܸ��� )
			self.petInbornSkillRate = csconst.PET_HAS_ALL_INBORN_SKILL_RATE ** ( 1.0/len(self.petInbornSkills) )
			
		flags = self.getEntityProperty( "flags" )
		inaRng = self.getEntityProperty( "initiativeRange" )
		if inaRng > 0 :													# �������������Χ���� 0
			if flags is None :											# �򣬸��������һ������������ǣ�hyw--09.03.03��
				flags = 1 << csdefine.ENTITY_FLAG_MONSTER_INITIATIVE
			else :
				flags |= 1 << csdefine.ENTITY_FLAG_MONSTER_INITIATIVE
			self.setEntityProperty( "flags", flags )
		if self.mapPetID != "":
			if flags is None:
				flags = 1 << csdefine.ENTITY_FLAG_CAN_CATCH
			else:
				flags |= 1 << csdefine.ENTITY_FLAG_CAN_CATCH
			self.setEntityProperty( "flags", flags )

		#-------------������أ����ｫ�������õ����ﱾ����ʽΪ index:odds
		if section.has_key( "drops" ):
			dropInfos = []
			drops = section["drops"]
			for value in drops.values():
				Infos = {}
				temp = value.asString
				if not temp:
					continue
				dropType,amount,dropOdds = temp.split(':')
				Infos["dropType"] = int(dropType)
				Infos["dropOdds"] = eval(dropOdds) / 100.0
				Infos["dropAmount"] = int(amount)
				dropInfos.append(Infos)
			self.setEntityProperty( "drops", dropInfos)
		if section.has_key( "luckyDropOdds" ):
			luckyDropOdds = section["luckyDropOdds"].asInt
			self.setEntityProperty( "luckyDropOdds", luckyDropOdds)

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		NPCObject.load( self, section )
		# ������������
		if section["prestige"] is not None:
			for e in section["prestige"].readVector2s( "item" ):
				self.prestige.append( ( int( e[0] ), int( e[1] ) ) )		# ����ת������

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		# ��ʼ���������ݷ���ǰͷ
		selfEntity.setLevel( selfEntity.level )
		self._initAI( selfEntity )
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_MONSTER )

	def _initDefaultAI( self, selfEntity ):
		"""
		��ʼ������Ĭ�ϵ�AI
		"""
		# û������AI�����Ĭ��AI
		selfEntity.addAI( 0, g_aiDatas[ 1 ], csdefine.AI_TYPE_GENERIC_ATTACK )  			  # ��⹥��������Ч��
		selfEntity.addAI( 0, g_aiDatas[ 0 ], csdefine.AI_TYPE_SPECIAL )		  				  # ��ͨ����
		# ��entity��������ʱ ���¼��µ�����AI������
		selfEntity.addEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP, 0, g_aiDatas[ 2 ] ) 	  	  # �Խ��������entity��ӵ���
		selfEntity.addEventAI( csdefine.AI_EVENT_ENEMY_LIST_CHANGED, 0, g_aiDatas[ 3 ] )	  # ������б�ı��ʱ�� ���״̬Ϊ��Ϣ �򹥻���Ŀ��
		selfEntity.addEventAI( csdefine.AI_EVENT_ENEMY_LIST_CHANGED, 0, g_aiDatas[ 4 ] ) 	  # ������б�ı��ʱ�� �������ս��״̬ �ҵ����б�û�е����� ����Ϊ����״̬ ���״̬Ҳ�ص��»���
		selfEntity.addEventAI( csdefine.AI_EVENT_ATTACKER_ON_REMOVE, 0, g_aiDatas[ 5 ] )	  # Ĭ�Ϲ���ս��AI   ����: ������б�ı��ʱ�� ��ʧ����ɾ��һ�����ڹ�����Ŀ��ʱ Ѱ����һ��Ŀ��
		#selfEntity.addEventAI( csdefine.AI_EVENT_DAMAGE_LIST_CHANGED, 0, g_aiDatas[ 6 ] )	  # Ĭ�Ϲ���ս��AI   ����: ���˺��б�ı��ʱ�� �жϵ�ǰ������Ŀ���Ƿ���һ��������ҵ�Ŀ���Ƿ���һ��role, �Ǿ�ת�򹥻�role

	def _initAI( self, selfEntity ):
		"""
		��ʼ�������AI
		"""
		if not g_npcaiDatas.has( self.className ):
			self._initDefaultAI( selfEntity )
			return

		aiData = g_npcaiDatas[ self.className ]
		for type, dataList in aiData.iteritems():
			if type not in [ csdefine.AI_TYPE_EVENT, csdefine.AI_TYPE_COMBO, csdefine.AI_TYPE_COMBO_ACTIVERATE ]:
				for d in dataList:
					selfEntity.addAI( d["level"], d["data"], d["type"] )
			elif type == csdefine.AI_TYPE_EVENT:
				for d in dataList:
					selfEntity.addEventAI( d["eventID"], d["level"], d["data"] )
			elif type == csdefine.AI_TYPE_COMBO:
				if self.isComboAILoaded:
					continue
				for d in dataList:
					self.addComboAI( d[ "level" ], d[ "comboID"], d[ "activeRate" ], d[ "data" ] )
			elif type == csdefine.AI_TYPE_COMBO_ACTIVERATE:
				if self.isComboAILoaded:
					continue
				self.comboActiveRate = dataList

		self.isComboAILoaded = True			# ֻ����һ��

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
		"""
		if selfEntity.getCamp() !=0 and selfEntity.getCamp() != playerEntity.getCamp():
			playerEntity.client.onStatusMessage( csstatus.CAMP_NPC_DIFFERENT, "" )
			return 

		NPCObject.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def getDropItems( self, selfInstance ):
		"""
		virtual method
		��ù���������Ʒ
		@param selfInstance: ��ȫ�����ݶ�Ӧ�ļ̳���Monster��real Monster entityʵ��
		@type  selfInstance: Monster
		@return :array of tuple, tuple like as  [(itemKeyName, {...}, owners) ,...]
		"""
		return g_monsterdropmanager.getDropItems( self, selfInstance )

	def dropItemBox( self, selfEntity, bootyOwner ):
		"""
		��������
		"""
		pos = selfEntity.position
		spaceID = selfEntity.spaceID
		direction = selfEntity.direction

		x, y, z = pos
		collide = BigWorld.collide( selfEntity.spaceID, ( x, y + 4, z ), ( x, y - 10, z ) )
		if collide != None:
			# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
			y = collide[0].y

		tempList = []
		itemsList = []
		drop_configed_items_info = selfEntity.popTemp( "drop_configed" )	# ��̬���õ�����Ϣ
		if drop_configed_items_info is not None:
			for itemID, amount in drop_configed_items_info.iteritems():
				item = g_items.createDynamicItem( itemID )
				item.setAmount( amount )
				itemsList.append( item )
		else:
			itemsList = self.getDropItems( BigWorld.entities.get(bootyOwner[0], None) )

		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperName" : selfEntity.getName() }
		itemBox = BigWorld.createEntity( "DroppedBox", spaceID, (x, y+2, z), direction, params )

		if bootyOwner[1] != 0:
			players = [ e for e in selfEntity.entitiesInRangeExt( 30.0, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == bootyOwner[1] ]
			if len(players) == 0:
				return
			multDrop = players[0].queryTemp( "MULT_DROP", 0 )
			if multDrop > 0:		# ���䷭��
				for item in itemsList:
					item.setAmount( item.amount *( 1 + multDrop ) )
			
			itemBox.init( bootyOwner, itemsList )
			players[0].addTeamMembersTasksItem(  itemBox.id, self.className )
		else:
			entity = BigWorld.entities.get( bootyOwner[0], None )
			if entity:
				player = None
				if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					player = entity
				elif entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
					owner = BigWorld.entities.get( entity.ownerID, None )
					if owner:
						player = owner
				if player:
					multDrop = player.queryTemp( "MULT_DROP", 0 )
					if multDrop > 0:		# ���䷭��
						for item in itemsList:
							item.setAmount( item.amount *( 1 + multDrop ) )
					
					itemBox.init( bootyOwner, itemsList )
					player.addTasksItem(  itemBox.id, self.className )

	def getBootyOwner( self, selfEntity ):
		"""
		���ս��Ʒ��ӵ���ߣ�
		�����֪�����ص�ӵ�����Ƿ��ж��飬��Ҫ�Լ�ȥ����ӵ���ߵĶ��������
		�������0���ʾû��ӵ���ߣ�������ز���0���Լ�ӵ�ж��飬��ô����ֵӦ����ָ��ӳ���teamMailbox's entityID��

		@return: tuple of Entity ID --> (ӵ����ID, ӵ���߶ӳ�ID)������ֻ�����һ��,ӵ����ID���ȣ�����Ϊ0��ʾ�����˶����Լ�
		@rtype:  TUPLE OF OBJECT_ID
		"""
		if len( selfEntity.bootyOwner ):
			return selfEntity.bootyOwner
		return (0,0)

	def queryRelation( self, selfEntity, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ
		ע��: ��Ϊ���������ʹ��Ƶ�ʼ���ĸߣ�Ϊ��Ч�ʣ����ֵĴ������ߺ������õķ�ʽ
		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		#if selfEntity.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not selfEntity.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if selfEntity.isUseCombatCamp and entity.isUseCombatCamp:
			entity = entity.getRelationEntity()
			if entity:
				combatConstraint = self.queryGlobalCombatConstraint( selfEntity, entity )
				if combatConstraint != csdefine.RELATION_NONE:
					return combatConstraint
				else:
					return selfEntity.queryCombatRelation( entity )
			else:
				return csdefine.RELATION_FRIEND
			
		def commonRelationCheck( selfEntity, entity ):
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_MONSTER ): # ���ܱ����﹥����־
				return csdefine.RELATION_NOFIGHT
			
			if entity.state in [csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME, csdefine.ENTITY_STATE_DEAD]:
				return csdefine.RELATION_NOFIGHT

			# ȫ����ս�ж�
			if selfEntity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
				entity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
					return csdefine.RELATION_NOFIGHT
			
			return csdefine.RELATION_ANTAGONIZE
		
		# it's a pet
		if entity.utype == csdefine.ENTITY_TYPE_PET:
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_NOFIGHT
			# �ѳ���ĵжԱȽ�ת�޸���������
			# ��Ȼ�˹�ϵδ�����ܻ���ݲ�ͬ��״̬��buff���¹�ϵ�ĸı䣬����ǰ��û�д�����
			entity = owner.entity

		if entity.utype == csdefine.ENTITY_TYPE_ROLE:

			bootyOwner = selfEntity.queryTemp( "ToxinFrog_bootyOwner", () )
			if bootyOwner:
				getTeam = getattr( entity, "getTeamMailbox", None )
				if getTeam and getTeam():
					if getTeam().id != bootyOwner[1]:
						return csdefine.RELATION_NOFIGHT
				else:
					if entity.id != bootyOwner[0]:
						return csdefine.RELATION_NOFIGHT

			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT

			# GM�۲���ģʽ
			if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT

			if selfEntity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE	 ):
				return csdefine.RELATION_NOFIGHT

			# �Ѻ���Ӫ�б��ж�
			return selfEntity.queryCampRelation( entity )


		if entity.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_CONVOY_MONSTER ]:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT
			
			if ( selfEntity.battleCamp != 0 or entity.battleCamp !=0 ):
				if selfEntity.battleCamp == entity.battleCamp:			# �����������Ӫֵ��Ŀ���ǹ����Ҹ��Լ�����ͬһ����Ӫ
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE

			if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ) or selfEntity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ):
				return csdefine.RELATION_ANTAGONIZE

			# �Ѻ���Ӫ�б��ж�
			return selfEntity.queryCampRelation( entity )


		if entity.utype in [csdefine.ENTITY_TYPE_SLAVE_MONSTER, csdefine.ENTITY_TYPE_VEHICLE_DART, csdefine.ENTITY_TYPE_PANGU_NAGUAL]:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:

				return csdefine.RELATION_NOFIGHT

			if selfEntity.queryTemp( 'is_dart_banditti', False ) == True:
				# ����ǽٷ˲������ˣ����ڳ������ڿ϶��ǵжԵ�
				return csdefine.RELATION_ANTAGONIZE
			ownerID = entity.ownerID
			if ownerID is 0:
				return csdefine.RELATION_ANTAGONIZE
			if BigWorld.entities.has_key( ownerID ):	#�ж��������˵ĵжԹ�ϵ
				return selfEntity.queryRelation( BigWorld.entities[ownerID] )
			return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_YAYU:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT

			if ( selfEntity.battleCamp != 0 or entity.battleCamp !=0 ):
				if selfEntity.battleCamp == entity.battleCamp:			# �����������Ӫֵ��Ŀ���ǹ����Ҹ��Լ�����ͬһ����Ӫ
					return csdefine.RELATION_FRIEND

			return csdefine.RELATION_ANTAGONIZE

		if entity.utype == csdefine.ENTITY_TYPE_CALL_MONSTER:
			if commonRelationCheck( selfEntity, entity ) == csdefine.RELATION_NOFIGHT:
				return csdefine.RELATION_NOFIGHT

			return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND

	def queryGlobalCombatConstraint( self, selfEntity, entity ):
		"""
		��ѯȫ��ս��Լ��
		"""
		#if not isinstance( entity, CombatUnit ):
		#	return csdefine.RELATION_FRIEND

		if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_MONSTER ): # ���ܱ����﹥����־
			return csdefine.RELATION_NOFIGHT
			
		if entity.state in [csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME, csdefine.ENTITY_STATE_DEAD]:
			return csdefine.RELATION_NOFIGHT
			
		# ȫ����ս�ж�
		if selfEntity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT or \
			entity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT
		
		if entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# ���entity����Ǳ��Ч��״̬
			return csdefine.RELATION_NOFIGHT
		
		# GM�۲���ģʽ
		if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
			return csdefine.RELATION_NOFIGHT
			
		if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			return csdefine.RELATION_NOFIGHT
			
		if entity.utype == csdefine.ENTITY_TYPE_ROLE:
			if selfEntity.flags & ( 1 << csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				return csdefine.RELATION_NOFIGHT
				
		if entity.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_CONVOY_MONSTER ]:
			if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ) or selfEntity.hasFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ):
				return csdefine.RELATION_ANTAGONIZE
				
		return csdefine.RELATION_NONE


	def dieNotify( self, selfEntity, killerID ):
		"""
		virtual method
		����֪ͨ
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase :
			spaceKey = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			spaceScript = g_objFactory.getObject( spaceKey )
			spaceScript.copyTemplate_onMonsterDie( spaceBase, selfEntity.id, selfEntity.className, killerID )		# �¸����ṹ�µĹ�������֪ͨ
		
		if selfEntity.isNotifyDie:							#�����Ƿ�֪ͨ��������
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				spaceEntity.getScript().onOneTypeMonsterDie( spaceEntity, selfEntity.id, selfEntity.className )
			elif spaceBase:
				spaceBase.cell.remoteScriptCall( "onOneTypeMonsterDie", ( selfEntity.id, selfEntity.className ) )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		virtual method
		����������ش���
		"""
		self.dieNotify( selfEntity, killerID )
		selfEntity.calculateBootyOwner()							# ���������������������˭ӵ��
		killers = []
		# ����ӵ����
		bootyOwner = selfEntity.getBootyOwner()
		if bootyOwner[1] != 0:		#���ж��Ƿ�����ӣ�Ȼ�����ж��Ƿ��Ǹ��� hd
			# ��ȡ��Ӿ���
			killers = selfEntity.searchTeamMember( bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			if len( killers ) == 1:
				# �����Ȼֻ����һ���˻�þ��飬�߻�ȡ����ɱ�־���·��
				killers = selfEntity.gainSingleReward( killers[0].id )
			else:
				# ��ȡ��Ӿ���
				selfEntity.gainTeamReward( killers)
				for entity in killers:
					entity.base.addTeamFriendlyValue( [e.databaseID for e in killers if e.databaseID != entity.databaseID] )

		elif bootyOwner[0] != 0:
			# ��õ���ɱ�־���
			killers = selfEntity.gainSingleReward( bootyOwner[0] )
		else:
			INFO_MSG( "%s(%i): I died, but no booty owner." % ( selfEntity.className, selfEntity.id ) )
			return

		self.dropItemBox( selfEntity, bootyOwner )
		# ����ʱ��������ж�
		for entity in killers:
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				entity.questMonsterKilled( selfEntity )
		
		# ��������
		killer = BigWorld.entities.get( killerID )
		if killer is None:
			return
				
		if killer.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or killer.isEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER ):
			killer = killer.getOwner()
			if killer is None: return
		elif killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity

		for prestigeItem in self.prestige:
			if not killer.isReal():
				killer.remoteCall( "addPrestige", ( prestigeItem[ 0 ], prestigeItem[ 1 ] ) )
			else:
				killer.addPrestige( prestigeItem[ 0 ], prestigeItem[ 1 ] )

	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		����һ��NPCʵ���ڵ�ͼ��
		@param   spaceID: ��ͼID��
		@type    spaceID: INT32
		@param  position: entity�ĳ���λ��
		@type   position: VECTOR3
		@param direction: entity�ĳ�������
		@type  direction: VECTOR3
		@param      param: �ò���Ĭ��ֵΪNone������ʵ�������
		@type    	param: dict
		@return:          һ���µ�NPC Entity
		@rtype:           Entity
		"""
		if param is None:
			param = {}
		if param.has_key( 'level' ):
			tempLevel = min( param["level"], self.maxLv )
			param["level"] = max( tempLevel, self.minLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		#���õ���ֵ
		dh_l = g_daoheng.get( param["level"] )
		dh = self._daohengAtt * dh_l
		dh = max( 1, dh )
		param["daoheng"] = dh 
		return NPCObject.createEntity( self, spaceID, position, direction, param )

	def doGoBack( self, selfEntity ):
		"""
		"""
		return selfEntity.gotoPosition( selfEntity.spawnPos )

	def getScriptName( self ):
		"""
		��ȡ�Լ��Ľű����֣������ֿ����ֲ�ͬ�Ĺ�������
		"""
		return self.__class__.__name__

	def antiIndulgenceFilter( self, itemsData, player ):
		"""
		������ϵͳ���˸��˵�����Ʒ����Ӳ��ܵĵ��䲻��Ӱ�죬Ӱ����Ƿ��䣩
		"""
		if player != None:
			gameYield = player.wallow_getLucreRate()
			print "------->>>>>gameYield = ", gameYield
			newData = []
			if gameYield == 1.0:
				return itemsData
			elif itemsData == 0:
				return newData
			else:
				for i in itemsData:
					if random.random() <= gameYield:
						newData.append( i )
				return newData
		return itemsData

	def getExpAmendRate( self, levelFall ):
		"""
		���ݵȼ����þ�������ֵ

		@param levelFall : ��Һ͹���ĵȼ���
		"""
		return AmendExp.instance().getLevelRate( levelFall )

	def getInbornSkillsCount( self ):
		"""
		��ô�������츳���ܵĸ���
		"""
		return len( self.petInbornSkills )
		
	def getInbornSkills( self ):
		"""
		��ô���monster���츳�����б�
		"""
		return self.petInbornSkills
		
	def getAccumAmemdRate( self, levelFall ):
		"""
		���ݵȼ�������������ֵ
		@param levelFall : ��Һ͹���ĵȼ���
		"""
		if  -5 <= levelFall < 150:
			return 1.0
		elif -10 <= levelFall < -5:
			return 0.85
		elif -20 <= levelFall < -10:
			return 0.7
		else:
			return 0.5
	
	def onHPChanged( self, selfEntity ):
		"""
		Ѫ�������ı�
		"""
		pass
		
	def onWitnessed( self, selfEntity, isWitnessed ):
		"""
		This method is called when the state of this entity being witnessed changes.
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		pass
		
	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		virtual method
		��������
		"""
		guardTrapID = selfEntity.queryTemp( "guardProximityID", 0 )
		if guardTrapID != 0 and guardTrapID == controllerID:
			return
		state = selfEntity.getState()
		if state == csdefine.ENTITY_STATE_FIGHT or state == csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT:						# ��Ϣ״̬.....�ƺ�û���õ�
			# ��ս��״̬��ʱ��ȡ���ݾ�
			if selfEntity.queryTemp( "proximityID", -1 ) == -1:
				return
			selfEntity.cancel( controllerID )
			selfEntity.removeTemp( "proximityID" )
			selfEntity.removeTemp( "test_Proximity" )
			return

		if selfEntity.checkEnterTrapEntityType( entity ):	# �����ҽ����ҵ���Ұ
			DEBUG_MSG( "%s(%i): %s into my initiativeRange." % ( selfEntity.getName(), selfEntity.id, entity.getName() ) )
			DEBUG_MSG( "my position =", selfEntity.position, "role position =", entity.position, "distance =", entity.position.distTo( selfEntity.position ), "my initiativeRange =", selfEntity.initiativeRange, "range =", range )
			selfEntity.aiTargetID = entity.id
			selfEntity.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
			selfEntity.aiTargetID = 0
		
	def onStateChanged( self, selfEntity, old, new ):
		"""
		virtual method
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		pass

	def addComboAI( self, level, comboID, activeRate, ai ):
		"""
		define method.
		���entity���comboAI,����ִ��
		@param ai   : ai of instance
		@param event: �¼�
		@param level: �趨��AI�����м���, �� AIϵͳ�ڴ˼���ʱ�Ż����и�AI
		"""
		if isinstance( ai, AIBase ):
			if self.comboAITable.has_key( level ):
				if self.comboAITable[ level ].has_key( comboID ):
					self.comboAITable[ level ][ comboID ]["aiDatas"].append( ai )
					self.comboAITable[ level ][ comboID ]["activeRate"] = activeRate
				else:
					self.comboAITable[ level ][ comboID ] = { "aiDatas": [ ai ], "activeRate": activeRate }
			else:
				self.comboAITable[ level ] = { comboID : { "aiDatas":[ ai ], "activeRate": activeRate } }
		else:
			ERROR_MSG( "addComboAI only receive an AIBase of instance." )
	
	def onChangeTarget( self, selfEntity, oldEnemyID ):
		"""
		virtual method
		"""
		pass
		
	def receiveDamage( self, selfEntity, casterID, skillID, damageType, damage ):
		"""
		virtual method
		"""
		pass
		
	def canThink( self, selfEntity ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		if selfEntity.state == csdefine.ENTITY_STATE_DEAD or selfEntity.isDestroyed: 		# ������ֹͣthink
			return False

		if selfEntity.subState == csdefine.M_SUB_STATE_GOBACK: 						# ���Ŀǰû����ҿ����һ����ڻ��ߣ���ô�ҽ�ֹͣthink
			return False

		if selfEntity.hasFlag( csdefine.ENTITY_FLAG_MONSTER_THINK ):					# ���۹����Ƿ���ҿ�������think(����40�����鸱��)
			return True

		if not selfEntity.isWitnessed and selfEntity.patrolList is None:
			return False

		return True
		
	def afterDie( self, selfEntity, killerID ):
		"""
		virtual method.
		"""
		g_fightMgr.breakGroupEnemyRelationByIDs( selfEntity, selfEntity.enemyList.keys() )

		selfEntity.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		# ���´���������Ϣͳ�� 10:08 2008-7-21 yk
		k = BigWorld.entities.get( killerID )
		if k is None: return
		if k.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = k.getOwner()
			if owner.etype == "MAILBOX" :
				return
			k = owner.entity
		if k.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			LOG_MSG("NPCClass(%s), NPCName(%s), NPCLevel(%i),databaseID(%i), playerName(%s), playerClass(%i), playerLevel(%i), killTime(%i)"\
				%( selfEntity.className, selfEntity.getName(), selfEntity.level, k.databaseID, k.getName(), k.getClass(), k.level, int( time.time() - selfEntity.fightStartTime ) ) )
			
			try:
				g_logger.actMonsterDieLog( selfEntity.className, k.databaseID, k.getName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def onGetNonRepeatedPatrolGraphID( self, selfEntity, patrolGraphID ) :
		"""
		�¸���ģ�� CopyTemplate �µ� getNonRepeatedPatrolGraphID �����ص�,���� AIAction300
		���� Monster ��û����д����ű���ԭ��
		��� AIAction300 ��Ϊ���ù�������������һ�����ﰴѲ��·��������Ŀǰ�����ⷽ��û�кܺõ�֧�֣��ʼ������������������Ҳ�����ô� AIAction
		"""
		selfEntity.setTemp( "AIAction300_patrolGraphID", patrolGraphID )
		patrolList = BigWorld.PatrolPath( patrolGraphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked in %s. it's not ready or not have such patrolGraphID!"%(patrolGraphID, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )) )
		else:
			patrolPathNode, position = patrolList.nearestNode( selfEntity.position )
			selfEntity.doPatrol( patrolPathNode, patrolList  )

	def getOwner( self, selfEntity ):
		"""
		virtual method
		���������
		"""
		return None
		
	def getOwnerID( self, selfEntity ):
		"""
		virtual method
		���������ID
		"""
		return 0
		
	def setOwner( self, selfEntity, owner ):
		"""
		����������
		virtual method
		"""
		pass