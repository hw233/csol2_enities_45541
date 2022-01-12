# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const


DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#���ȫ���뿪�����󣬸���ø�����ɾ��

GOD_WEAPON_QUEST_YAYU		 = 40202002	# ��������m؅ID

class SpaceCopyYayuNew( SpaceCopy ):

	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.spawnDict = {}					# �Ѿ������Ĺ���ID { className: [id1, id2, ���� ]�� ���� }

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.copyDataInit( baseMailbox, params )
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )


	def copyDataInit( self, baseMailbox, params ):
		"""
		�������ݷ���ĳ�ʼ��
		"""
		BigWorld.globalData['Yayu_%i' % params['teamID'] ] = True
		self.setTemp('globalkey','Yayu_%i' % params['teamID'])

		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP, 50 )				# �m؅Ѫ��
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "" )			# ��һ�׶�ʣ��ʱ��
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )				# ʣ��Boss
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_BATCH, 0 )						# ��ǰ�׶�

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
			8: �m؅Ѫ���ٷֱ�
			11:���Ȫm؅��ǰ�׶�
			12:��һ�����￪ʼʱ��(�°�m؅)
			13:�m؅Ѫ���ٷֱ�
			14:Բ��Ѫ��
		]
		"""
		# ��ʾʣ��С�֣�ʣ��BOSS��
		return [ 3,11, 12, 14, 13 ]

	def onYayuDie( self ):
		"""
		define method
		"""
		self.getScript().onYayuDie( self )


	def onYayuHPChange( self, hp, hp_Max ):
		"""
		define method
		"""
		self.getScript().onYayuHPChange( self, hp, hp_Max )

	def onYayuMonsterBorn( self, className, id ):
		"""
		define method
		"""
		if not self.spawnDict.has_key( className ):
			self.spawnDict[ className ] = []
		self.spawnDict[ className ].append( id )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )

		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]


	def onTimer( self, id, userArg ):
		"""
		���ǵײ��onTimer()�������
		"""
		SpaceCopy.onTimer( self, id, userArg )

	def onGodWeaponYayuFin( self ):
		"""
		define method
		����������񣬪m؅HPʣ��90%����
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_YAYU, 1 )

	def destroyMonsters( self ) :
		"""
		��������ˢ�����Ĺ���
		"""
		for monsters in self.spawnDict.itervalues() :
			for m_id in monsters :
				monster = BigWorld.entities.get( m_id )
				if monster:
					monster.destroy()
		self.spawnDict.clear()
