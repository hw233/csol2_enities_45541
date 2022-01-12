# -*- coding: gb18030 -*-
#

import random
import BigWorld
from NPCObject import NPCObject
import csdefine
import csstatus
import Const
import items
import ECBExtend
import csconst
from bwdebug import *
from MsgLogger import *
from LivingConfigMgr import LivingConfigMgr


g_items = items.instance()

# ���������ӵ���ʾ������
SLE_UP_MSG_MAP = {
	25:csstatus.LIVING_SKILL_SLE_UP_MSG_1,
	50:csstatus.LIVING_SKILL_SLE_UP_MSG_2,
	75:csstatus.LIVING_SKILL_SLE_UP_MSG_3,
	100:csstatus.LIVING_SKILL_SLE_UP_MSG_4,
	150:csstatus.LIVING_SKILL_SLE_UP_MSG_5,
	200:csstatus.LIVING_SKILL_SLE_UP_MSG_6,
	350:csstatus.LIVING_SKILL_SLE_UP_MSG_7,
	500:csstatus.LIVING_SKILL_SLE_UP_MSG_8,
}

class CollectPoint( NPCObject ):
	"""
	QuestBox������
	"""

	def __init__( self ):
		"""
		"""

		NPCObject.__init__( self )
		self.questID = 0				# ��ص�������
		self.taskIndex = 0				# �����еĴ��Ŀ������
		self.questItemID = ""

		self.effectName = ""			# ������ʱ���ŵĹ�Ч����
		self.spellID = 0				# ������ʱ�����ʩչ�Ķ���
		self.spellIntoneTime = 0.0		# ����ʩչʱ������ʱ��
		self.destroyTime = 0			# ����ʱ��
		self.param1 = None				# ����ĸ��Ӳ���
		self.param2 = None
		self.param3 = None
		self.param4 = None
		self.param5 = None
		self.param6 = None
		self.param7 = None
		self.param8 = None
		self.param9 = None
		self.param10 = None

	# ----------------------------------------------------------------
	# overrite method / protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, sect ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initializes.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" file
		@ptype			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		NPCObject.onLoadEntityProperties_( self, sect )
		# ע����������Բ���Ҫ��ȡ���ڴ�����ʱ���ɳ���������ֱ�Ӵ�����
		#self.setEntityProperty( "rediviousTime", sect.readFloat( "rediviousTime" ) )	# ��������һ��ʱ���ָ���ʾ

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		selfEntity.removeFlag( 0 )

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		NPCObject.load( self, section )
		self.effectName = section.readString( "effectName" )			# ������ʱ���ŵĶ���
		self.spellID = section.readInt( "spellID" )						# ������ʱ�����ʩչ�Ķ���
		self.spellIntoneTime = section.readFloat( "spellIntoneTime" )	# ����ʩչʱ������ʱ��
		self.destroyTime = section.readFloat( "destroyTime" )			# ����ʱ��
		self.param1 = int( section.readString( "param1" ) )			# �ɼ�������(�ɼ�����ID)
		self.param2 = int( section.readString( "param2" ) )			# �ɼ�������������
		self.param3 = section.readString( "param3" )				# �ɻ����ƷID���伸��
		self.param4 = section.readString( "param4" )				# ��Ҫƾ֤��ƷID
		self.param5 = int( section.readString( "param5" ) )			# ����������
		self.param6 = int( section.readString( "param6" ) )			# ���Ļ���ֵ
		self.param7 = int( section.readString( "param7" ) )			# ˢ��ʱ��
		self.param8 = int( section.readString( "param8" ) )			# �����������ȵ�����
		self.param9 = section.readString( "param9" )				# ˢ�����ã��ɿգ���ʽ��{odd:monsterID, odd:monsterID, ...}
		self.param10 = section.readString( "param10" )
		self.skillName = ""
		if self.param1 == 0:
			return
		if not ( self.param9 is None or self.param9 == "" ):
			self.param9 = eval( self.param9 )
		else:
			self.param9 = {}

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
		if self.skillName == "":
			from Love3 import g_skills
			skillInstance = g_skills[self.param1]
			if skillInstance is None:
				ERROR_MSG( "Living skill %s is None."%(self.param1) )
				return
			self.skillName = skillInstance.getName()

		return NPCObject.createEntity( self, spaceID, position, direction, param )


	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		playerEntity.endGossip( selfEntity.id )
		if dlgKey != "Talk":
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( False )
			return
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onCollectStatus( 0 )
			return
		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# ������0��ʾ�Ѿ����������ˣ��ȴ�ɾ����
			playerEntity.clientEntity( selfEntity.id ).onCollectStatus( False )
			return
		# if self.param1 or self.param2 or self.param4 or self.param6 is None: return
		if not self.talkAbleCheck( playerEntity ):		# ��ͨ/����ɼ��������������
			return
		#����CSOL-776��Ҫ�� ���ж�ȡ�� by wuxo
		#ids = self.param4.split("|")
		#useItem = None
		#for id in ids:
		#	nItem = playerEntity.findItemFromNKCK_( int( id ) )
		#	if nItem is not None:
		#		useItem = nItem
		#		break
		#if useItem is None:	# ����û��ƾ֤����
		#	playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_ITEM )
		#	return
		#if playerEntity.iskitbagsLocked() :
		#	playerEntity.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
		#	return
		## �ж���Ʒ�Ƿ񶳽�
		#if useItem.isFrozen():
		#	playerEntity.statusMessage( csstatus.CIB_MSG_FROZEN )
		#	return
		#selfEntity.setTemp( str( playerEntity.id ), useItem.uid )
		playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# ������ʱ���������������ȷ��������
		playerEntity.spellTarget( self.spellID, selfEntity.id )
		
		try:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( playerEntity.spaceID , csconst.SPACE_SPACEDATA_KEY )
			g_logger.collectLog( playerEntity.databaseID, playerEntity.getName(), spaceLabel, selfEntity.className )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		��������Ļص�����ĳЩ���⼼�ܵ���

		@param spell: ����ʵ��
		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		# ����˴���ⲻͨ�������ʾ��Ҷ�ĳ������Ķ��������ˣ���ʱ��û�кõ���ʾ������
		if not selfEntity.isReal():
			caster.clientEntity( selfEntity.id ).onCollectStatus( 0 )
			return
			
		# ȥ����ʱ��־
		caster.removeTemp( "quest_box_intone_time" )
		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# ������0��ʾ�Ѿ����������ˣ��ȴ�ɾ����
			caster.clientEntity( selfEntity.id ).onCollectStatus( False )
			caster.statusMessage( csstatus.LIVING_COLLECT_POINT_BUSY )
			return
			
		# ָʾ�ͻ��˲��Ź�Ч����
		selfEntity.playEffect = self.effectName
		# һ��ʱ���ɵ��Լ�
		if self.destroyTime > 0.0:
			selfEntity.addFlag( 0 )	# ����ר�ã����ܻ���FLAG_*��ͻ�������û������ԭ��Ӧ��û������
		elif self.destroyTime == 0.0:
			# ����ʱ��=0�������ؿͻ���ģ��
			selfEntity.addFlag( 1 )	# �ͻ��˲�����ģ��
		selfEntity.setTemp( "quest_box_destroyed", 1 )
		caster.clientEntity( selfEntity.id ).onCollectStatus( 0 )
		
		#����CSOL-776��Ҫ�� ���ж�ȡ�� by wuxo
		
		# ����ƾ֤��Ʒ	 ������ߵ�ʹ�ô�����-1��,����ʱ��ʧ֮
		#useItemUID = selfEntity.queryTemp( str( caster.id ), 0 )
		#if useItemUID is None or useItemUID == 0:
		#	return
		#	
		#useItem = caster.getItemByUid_( useItemUID )
		#if useItem is None:
		#	caster.statusMessage( csstatus.LIVING_SKILL_NOT_ITEM )
		#	return
		#	
		## �ж���Ʒ�Ƿ񶳽�
		#if useItem.isFrozen():
		#	caster.statusMessage( csstatus.CIB_MSG_FROZEN )
		#	return
		#if caster.iskitbagsLocked():
		#	caster.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
		#	return
		#useDegree = useItem.getUseDegree() - 1
		#if useDegree <= 0:
		#	caster.removeItem_( useItem.getOrder(), reason = csdefine.DELETE_ITEM_COLLECT_POINT )
		#else:
		#	useItem.setUseDegree( useDegree, caster )
		
		# ���������� ������ܵȼ����ڲɼ���ȼ�������
		sel = caster.getSleight( self.param1 )
		if not caster.isSleightLevelMax( self.param1 ) and ( sel in xrange( self.param2, self.param8 ) ):
			caster.addSleight( self.param1, self.param5 )
			now_sle = caster.getSleight( self.param1 )
			now_sle_Max = caster.getSleightMax( self.param1 )
			caster.statusMessage( csstatus.LIVING_SKILL_SLE_UP, self.skillName, now_sle, now_sle_Max )
			if SLE_UP_MSG_MAP.has_key( now_sle ):
				caster.statusMessage( SLE_UP_MSG_MAP[now_sle], self.skillName )
		else:
			caster.statusMessage( csstatus.LIVING_SKILL_SLE_UP_FAILED )
		# ���Ļ���ֵ
		if self.param6:
			caster.consumeVim( self.param6 )
		# �Ѳɼ��õ�����Ʒװ�� ���Ҫ��Ҫ��������
		if self.param3 is None: return
		itemIDs = self.param3.split("|")
		collectDict = {}
		for itemID in itemIDs:
			if itemID.find(":") <= 0:
				collectDict[int(itemID)] = 1
			else:
				itemInfo = itemID.split(":")
				odd = random.randint(1,100)	# ������ÿһ�ζ�Ҫ��� 0:itemID��1:���ʣ�2:����
				if odd > int( itemInfo[1] ):
					continue
				collectDict[int( itemInfo[0] )] = int( itemInfo[2] )
		selfEntity.removeTemp( str( caster.id ) )
		
		# �ɼ�����ˢ��
		isSpawn = False #�Ƿ��Ѿ�ˢ������
		if selfEntity.spawnMB and len(selfEntity.monsterDatas) > 0 or len(self.param9) > 0:
			spawnMonsterDatas = eval( selfEntity.monsterDatas ) if len(selfEntity.monsterDatas) > 0 else self.param9
			for odd, monsterID in spawnMonsterDatas.iteritems():
				if random.randint(1, 100) < int(odd*100):
					selfEntity.spawnMB.cell.spawnMonster( str( monsterID ), collectDict )
					isSpawn = True
					break
		
		if isSpawn == False:
			caster.setTemp( "collectItems", collectDict )		# Ϊ��ֹcellʵ����ͬ���ýű����ѻ��Ʒʵ���ع鵽�������
			caster.clientEntity( selfEntity.id ).pickUpCollectPointItems( collectDict )
			
		# issueID:CSOL-943 ��Դ����ʧ��Ӧ������ˢ��,������Ƿ�ʰȡ�޹�
		selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

	def corpseDelay( self, selfEntity ):
		"""
		����������ġ�������֮������Щ����
		��������ˢ�¡�����ˢ�¡����Ǹ����Ͳ�ˢ�µ�

		��ͬ�Ľű����ͬ�Ĵ���
		��������Ĵ���ʽ�ǣ��򿪳������֮������ģ��
		������selfEntity.rediviousTime��ʱ���ȥ������ˢһ������������ʾģ�ͣ�
		"""
		# collectPoint����ʱ����destroy�Լ�������������ģ�Ͷ���
		if selfEntity.rediviousTime >= 0:
			selfEntity.addTimer( self.param7, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )

	def addQuestTask( self, questID, taskIndex ):
		"""
		@param questID: ����ID
		@type  questID: INT32
		@param taskIndex: ������Ŀ������
		@type  taskIndex: INT32
		"""
		pass

	def collectStatus( self, selfEntity, playerEntity ):
		"""
		�ͻ�����������������������״̬
		"""
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onCollectStatus( 0 )
			return
		playerEntity.clientEntity( selfEntity.id ).onCollectStatus( selfEntity.queryTemp( "quest_box_destroyed", 0 ) == 0 )
		playerEntity.clientEntity( selfEntity.id ).onCollectDatas( self.param1, self.param2, self.param8 )

	def onPickUpItemByIndex( self, selfEntity, playerEntity, index ):
		"""
		������Ҳɼ���Ʒ
		"""
		collectDict = playerEntity.queryTemp( "collectItems", {} )
		# ȥ����ʱ��־
		if len( collectDict ) <= 0:
			playerEntity.removeTemp( "collectItems" )
			return
		if index > len( collectDict ) - 1: return
		itemID = collectDict.keys()[index]
		if itemID == 0: return
		amount = collectDict[itemID]
		if amount == 0: return
		item = g_items.createDynamicItem( itemID )
		if item is None: return
		item.setAmount( amount )
		if not playerEntity.addItemAndNotify_( item, csdefine.ADD_ITEM_COLLECT_POINT ):
			playerEntity.statusMessage( csstatus.CIB_MSG_ITEM_NOT_YOUR )
			return
		collectDict[itemID] = 0
		playerEntity.setTemp( "collectItems", collectDict )
		playerEntity.clientEntity( selfEntity.id ).pickUpItemByIndexBC( index )

	def talkAbleCheck( self, playerEntity ):
		"""
		�ɼ���ļ��
		"""
		vim = playerEntity.getVim()
		if vim <= 0 or vim - self.param6 <= 0:	# ����ֵ����
			playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_VIM )
			return False
		livSkillsSleight = playerEntity.getSleight( self.param1 )
		if livSkillsSleight < 0: 		# û�ж�Ӧ���� �ȼ�����
			playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_SKILL, self.skillName  )
			return False
		if livSkillsSleight < self.param2:	# �����Ȳ���
			playerEntity.statusMessage( csstatus.LIVING_SKILL_NOT_LEVEL, self.skillName  )
			return False
		return True