# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from NPCObject import NPCObject
import csdefine
import items
import ECBExtend

g_items = items.instance()

class QuestBox( NPCObject ):
	"""
	QuestBox������
	"""
	
	def __init__( self ):
		"""
		"""
		
		NPCObject.__init__( self )
		self.questData = {}
		#self.questID = []				# ��ص�������
		#self.taskIndex = []				# �����еĴ��Ŀ������
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
		self.param1 = section.readString( "param1" )					# ����ĸ��Ӳ���
		self.param2 = section.readString( "param2" )
		self.param3 = section.readString( "param3" )
		self.param4 = section.readString( "param4" )
		self.param5 = section.readString( "param5" )
		self.param6 = section.readString( "param6" )
		self.param7 = section.readString( "param7" )
		self.param8 = section.readString( "param8" )
		self.param9 = section.readString( "param9" )
		self.param10 = section.readString( "param10" )
	
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
		return NPCObject.createEntity( self, spaceID, position, direction, param )
		
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		�ж���Һ����ӵ�����״̬
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus�� state )
		state == True :  ��ʾ��������״̬�������������ӿ��Ա�ѡ��
		����: û��������״̬�����ܱ�ѡ��
		""" 
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
			
		if len( self.questData ) <= 0:
			if self.spellID <= 0:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			else:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( selfEntity.queryTemp( "quest_box_destroyed", 0 ) == 0 )
			return
			
		findQuest = False
		for id in self.questData.keys():
			quest = self.getQuest( id )
			if quest != None:
				findQuest = True
				break
		if not findQuest:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# ������0��ʾ�Ѿ����������ˣ��ȴ�ɾ����
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		indexTaskState = False
		for questID, taskIndex in self.questData.iteritems():
			if not playerEntity.taskIsCompleted( questID, taskIndex ):
				indexTaskState = True
				break
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( indexTaskState )

	def onIncreaseQuestTaskState( self, selfEntity, playerEntity ):
		"""
		֪ͨ������������ĳ������λ���ϵ�����Ŀ���Ѿ������
		@param selfEntity: ����������
		@type  selfEntity: entity
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		@param index: Ҫ�趨��ɵ�����Ŀ�������λ��
		@type  index: INT16
		"""
		if len( self.questData ) > 0:
			for questID, taskIndex in self.questData.iteritems():
				playerEntity.questTaskIncreaseState( questID, taskIndex )
		
	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# ������0��ʾ�Ѿ����������ˣ��ȴ�ɾ����
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return
			
		if len( self.questData ) > 0:
			allCompleted = True
			for questID, taskIndex in self.questData.iteritems():
				if not playerEntity.taskIsCompleted( questID, taskIndex ):		# �������ָ���������Ŀ��û�����
					allCompleted = False
					break
			if not allCompleted:
				playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# ������ʱ���������������ȷ��������
				playerEntity.spellTarget( self.spellID, selfEntity.id )
				#entity = g_items.createEntity( self.questItemID, selfEntity.spaceID, selfEntity.position, selfEntity.direction)
				#entity.addPickupID( playerEntity.id )
				#selfEntity.destroy( )
		else:
			playerEntity.setTemp( "quest_box_intone_time", self.spellIntoneTime )	# ������ʱ���������������ȷ��������
			playerEntity.spellTarget( self.spellID, selfEntity.id )
	
	def addQuestTask( self, questID, taskIndex ):
		"""
		@param questID: ����ID
		@type  questID: INT32
		@param taskIndex: ������Ŀ������
		@type  taskIndex: INT32		
		"""
		if self.questData.get( questID ):
			return
		self.questData[ questID ] = taskIndex

	def onReceiveSpell( self, selfEntity, caster, spell ):
		"""
		��������Ļص�����ĳЩ���⼼�ܵ���
		
		@param spell: ����ʵ��
		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		# ����˴���ⲻͨ�������ʾ��Ҷ�ĳ������Ķ��������ˣ���ʱ��û�кõ���ʾ������
		if not selfEntity.isReal():
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		# ȥ����ʱ��־
		caster.removeTemp( "quest_box_intone_time" )
		# ָʾ�ͻ��˲��Ź�Ч����
		selfEntity.playEffect = self.effectName
		# һ��ʱ���ɵ��Լ�
		if self.destroyTime > 0.0:
			selfEntity.addFlag( 0 )	# ����ר�ã����ܻ���FLAG_*��ͻ�������û������ԭ��Ӧ��û������
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		elif self.destroyTime == 0.0:
			# ����ʱ��=0�������ؿͻ���ģ��
			selfEntity.addFlag( 1 )	# �ͻ��˲�����ģ��
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		else:
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			selfEntity.destroy( )				# ��������
	
	def entityDead( self, selfEntity ):
		"""
		"""
		pass
		#selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
		
	def corpseDelay( self, selfEntity ):
		"""
		����������ġ�������֮������Щ����
		��������ˢ�¡�����ˢ�¡����Ǹ����Ͳ�ˢ�µ�
		
		��ͬ�Ľű����ͬ�Ĵ���
		��������Ĵ���ʽ�ǣ��򿪳������֮������ģ��
		������selfEntity.rediviousTime��ʱ���ȥ������ˢһ������������ʾģ�ͣ�
		"""
		# QuestBox����ʱ����destroy�Լ�������������ģ�Ͷ���
		if selfEntity.rediviousTime >= 0:
			selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )

