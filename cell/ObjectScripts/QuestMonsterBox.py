# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.19 2008-07-29 04:11:34 phw Exp $

from QuestBox import QuestBox
import csdefine
import items
import ECBExtend

g_items = items.instance()

class QuestMonsterBox( QuestBox ):
	"""
	QuestBox������
	"""
	
	def __init__( self ):
		"""
		"""
		
		QuestBox.__init__( self )


	def addMonsterCount( self, selfEntity, monsterCount ):
		"""
		����QuestBox�Ѿ��ٻ������Ĺ�������
		"""
		selfEntity.setTemp( "questMonsterCount", selfEntity.queryTemp( "questMonsterCount", 0 ) + monsterCount )

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
			# ����ʱ��>0��Ҫ���ؿͻ���ģ��
			selfEntity.addTimer( self.destroyTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		elif self.destroyTime == 0.0:
			# ����ʱ��=0�������ؿͻ���ģ��
			selfEntity.addFlag( 1 )	# �ͻ��˲�����ģ��
			selfEntity.setTemp( "quest_box_destroyed", 1 )
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		else:
			self.taskStatus( selfEntity, caster )
		
	def entityDead( self, selfEntity ):
		"""
		"""
		self.addMonsterCount( selfEntity, -1 )
		if selfEntity.queryTemp( "questMonsterCount", 0 ) <= 0 and selfEntity.rediviousTime >= 0:
			selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
			
	def corpseDelay( self, selfEntity ):
		"""
		����������ġ�������֮������Щ����
		��������ˢ�¡�����ˢ�¡����Ǹ����Ͳ�ˢ�µ�
		"""
		# QuestBox����ʱ����destroy�Լ�������������ģ�Ͷ���
		selfEntity.addFlag( 0 )	# ����ר�ã����ܻ���FLAG_*��ͻ�������û������ԭ��Ӧ��û������
		if selfEntity.rediviousTime >= 0 and selfEntity.queryTemp( "questMonsterCount", 0 ) <= 0:
			selfEntity.addTimer( selfEntity.rediviousTime, 0, ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID )
