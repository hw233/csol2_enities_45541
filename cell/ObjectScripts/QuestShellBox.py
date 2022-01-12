# -*- coding: gb18030 -*-
#
# ������ĳ������ 2009-01-15 SongPeifang
#

from QuestBox import QuestBox
import ECBExtend

class QuestShellBox( QuestBox ):
	"""
	������ĳ������
	"""
	
	def __init__( self ):
		"""
		"""		
		QuestBox.__init__( self )
	
	def createEntity( self, spaceID, position, direction, param = None ):
		param["isShow"] = int( self.param2 )
		return QuestBox.createEntity( self, spaceID, position, direction, param )
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		�ж���Һ����ӵ�����״̬
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus�� state )
		state == True :  ��ʾ��������״̬�������������ӿ��Ա�ѡ��
		����: û��������״̬�����ܱ�ѡ��
		""" 
		status = 1
		# ��ұ������չ�ԡ���Ҵ���ÿ��ĺϷ��չ�ԡʱ����
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( status )

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
		�ɸó�������ٻ������Ĺ���������Ĵ���
		��Ϊ�˳������Ŀǰû���ٻ�������������Դ˽ӿ���ʱpass
		"""
		pass
		
	def corpseDelay( self, selfEntity ):
		"""
		����������ġ�������֮������Щ����
		��������ˢ�¡�����ˢ�¡����Ǹ����Ͳ�ˢ�µ�
		
		����ֻҪ��������������󣬾���ʧ�����أ���������ˢ�µĳ���
		ˢ������base�˿��Ƶ�ÿ����ˢ20����������ôˢ��ΪʲôҪ��ôˢ������
		��base����ˢ�£���Ҳ���������QuestShellBox���͵�ԭ��
		"""
		selfEntity.addFlag( 0 )	# �ڿͻ������ص�֮��