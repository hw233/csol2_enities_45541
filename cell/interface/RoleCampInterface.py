# -*- coding: gb18030 -*-

import datetime
import BigWorld
import csdefine
import csconst

class RoleCampInterface:
	def __init__( self ):
		pass
	
	def camp_beKilled( self, killer ):
		"""
		����Ӫ��ɱ
		"""
		if killer.getEntityType() == csdefine.ENTITY_TYPE_ROLE and killer.getCamp() != self.getCamp():
			self.camp_refreshBeKill()
			killer.camp_killReward( self, self.level, self.camp_bekill )
			self.camp_bekill += 1
		
	def camp_refreshBeKill( self ):
		if self.camp_refreshTime != str( datetime.date.today() ):
			self.camp_bekill = 0
			self.camp_refreshTime = str( datetime.date.today() )
	
	def camp_addHonour( self, honour ):
		"""
		define method.
		�����Ӫ����
		"""
		val = honour + honour * self.camp_honourMult # �����౶����
		self.camp_honour += val
	
	def camp_decHonour( self, honour ):
		"""
		define method.
		�����Ӫ����
		"""
		self.camp_honour -= honour
	
	def camp_getHonour( self ):
		"""
		��ȡ��Ӫ����
		"""
		return self.camp_honour
	
	def camp_getKillReward( self, beKLevel, killNum ):
		"""
		��ɱ����= max(1, ��׼���� * �ȼ�����ϵ�� * ��λ�ɱ����ϵ�� ) 
        �ȼ�����ϵ��= min( 5, 0.5^(( ��ɱ���ȼ� - ����ɱ���ȼ� )/10) ) 
		"""
		levelBaseCoe = min( 5, pow( 0.5, ( ( self.level - beKLevel ) / 10 ) ), )
		numKillCoe = pow( 0.5, ( killNum / 5 ) )
		return 	max( 1, int( csconst.CAMP_KILL_REWARD_HONOUR_BASE * levelBaseCoe * numKillCoe ) )
	
	def camp_killReward( self, beKillMB, beKLevel, beKNum ):
		"""
		define method
		��Ӫ��ɱ����
		"""
		rewardHonour = self.camp_getKillReward( beKLevel, beKNum )
		self.camp_addHonour( rewardHonour )
		
	def camp_addMorale( self, camp, amount ):
		"""
		�����Ӫ���֣�Morale����Ϊ����
		"""
		BigWorld.globalData[ "CampMgr" ].addMorale( camp, amount )
		self.questCampMoraleChange( camp, amount )
		
	def camp_systemCastSpell( self, camp, skillID ):
		"""
		define method
		ĳ��Ӫ���ʹ��һ��ϵͳ���ܣ����������Ӫbuff
		"""
		if self.getCamp() == camp:
			self.systemCastSpell( skillID )
			