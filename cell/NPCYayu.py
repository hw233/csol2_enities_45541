# -*- coding: gb18030 -*-

from Monster import Monster
import csdefine
import cschannel_msgs

YAYU_STAND_BUFF = 122186001			#�m؅վ�����ļ���BUFF
BA_TI_JINENG = 122363004			#���弼��
GOD_WEAPON_QUEST_YAYU_HP_PARAM	= 9		# ��������m؅HP��������90%

class NPCYayu( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_YAYU )
		self.getCurrentSpaceBase().setYayuID( self.id )
		self.setTemp( "yayuCanTalk", True )
		self.setTemp( "yayuFinishTalk", False )
		self.addFlag( csdefine.ENTITY_FLAG_SPEAKER )

	def queryRelation( self, entity ):
		"""
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			if ( self.battleCamp != 0 or entity.battleCamp !=0 ):
				if self.battleCamp != entity.battleCamp:			# �����������Ӫֵ��Ŀ���ǹ����Ҹ��Լ�����ͬһ����Ӫ
					return csdefine.RELATION_ANTAGONIZE
			return csdefine.RELATION_NOFIGHT

	def onActived( self ):
		"""
		define method.
		"""
		if self.queryTemp( "yayuCanTalk", False ) == False:
			# ����Ѿ����˼����ˣ��������������ٴμ���
			return
		self.setTemp( "yayuCanTalk", False )
		self.getCurrentSpaceBase().cell.onConditionChange( {} )
		self.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )
		self.spellTarget( BA_TI_JINENG, self.id ) 


	def onKillAllMonster( self ):
		"""
		define method
		�����й���ɱ��
		"""
		#self.setTemp( "yayuFinishTalk", True )
		#self.addFlag( csdefine.ENTITY_FLAG_SPEAKER )
		self.say( cschannel_msgs.YA_YU_VOICE1 )
		self.spellTarget( YAYU_STAND_BUFF,  self.id )
		self.planesAllClients( "onKillAllMonster", () )
		
		if ( self.HP*10.0/self.HP_Max ) > GOD_WEAPON_QUEST_YAYU_HP_PARAM:		# ��������m؅HP��������90%
			self.getCurrentSpaceBase().cell.onGodWeaponYayuFin()

	def onThankOver( self ):
		"""
		define method
		��л���
		"""
		self.setTemp( "yayuFinishTalk", False )
		self.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )

	def onHPChanged( self ):
		"""
		HP���ı�ص�
		"""
		Monster.onHPChanged( self )
		if self.getCurrentSpaceBase():
			self.getCurrentSpaceBase().cell.onYayuHPChange( self.HP, self.HP_Max )