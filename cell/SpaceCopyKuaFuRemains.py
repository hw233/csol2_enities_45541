# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#���ȫ���뿪�����󣬸���ø�����ɾ��
#GOD_WEAPON_QUEST_KR = 40202006		# ��������
GOD_WEAPON_QUEST_KR = 40202001			# ��������
GOD_WEAPON_QUEST_KR_2 = 50201010		# ��������
CLASS_NAME_BOSS_3 = "20114007"			# ����
GW_HP_CHANGE_RATE = 0.85	# ����Ҫ�󣺳ɹ���ɱ�����������Ѫ����Ȼ������85%���ϡ�

class SpaceCopyKuaFuRemains( SpaceCopy ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.setTemp( "godWoodHPTooLow", False )
	
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )

	def onMonsterDie( self, params ):
		"""
		define method
		��һ���������
		"""
		self.getScript().onMonsterDie( self, params )
		# ��������������Ѫ����Ȼ������85%���ϣ�����������������
		if params["className"] == CLASS_NAME_BOSS_3:
			if self.queryTemp( "godWoodHPTooLow" ) is False:
				self.onGodWeaponKR_2()
		
	def onGodWoodHPChange( self, hp, hp_max ):
		"""
		define method
		����ľ HP ����һ��ֵ
		"""
		if hp*1.0/hp_max < GW_HP_CHANGE_RATE:
			self.setTemp( "godWoodHPTooLow", True )

	def shownDetails( self ):
		"""
		"""
		# ��ʾ����Ѫ��
		return [ csconst.SPACE_SPACEDATA_TREE_HP_PRECENT, ]

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			del BigWorld.globalData[self.queryTemp('globalkey')]
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )

	def onGodWeaponKR( self ):
		"""
		�����������
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_KR, 1 )
			
	def onGodWeaponKR_2( self ):
		"""
		�����������2		ɱ��ĳbossΪֹ��������
		"""
		if self.queryTemp( "roleDieNum", 0 ) > 0:
			return
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_KR_2, 1 )