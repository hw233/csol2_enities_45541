# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from NPCObject import NPCObject
import csdefine
import items
import ECBExtend
from QuestBox import QuestBox

g_items = items.instance()

class FengHuoLianTianBattleFlag( QuestBox ):
	"""
	�����ս������������죩ս��
	"""
	
	def __init__( self ):
		"""
		"""
		
		QuestBox.__init__( self )
		
		
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
		
	def corpseDelay( self, selfEntity ):
		"""
		����������ġ�������֮������Щ����
		��������ˢ�¡�����ˢ�¡����Ǹ����Ͳ�ˢ�µ�
		
		��ͬ�Ľű����ͬ�Ĵ���
		��������Ĵ���ʽ�ǣ��򿪳������֮������ģ��
		������selfEntity.rediviousTime��ʱ���ȥ������ˢһ������������ʾģ�ͣ�
		"""
		# QuestBox����ʱ����destroy�Լ�������������ģ�Ͷ���
		selfEntity.addTimer( 0, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
		#selfEntity.setTemp( "gossipingID", 0 )

