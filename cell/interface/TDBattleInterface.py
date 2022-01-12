# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
import csstatus
import VehicleHelper
import SkillTargetObjImpl
from Resource.SkillLoader import g_skills
from bwdebug import *

SKILL_ID = 123549001

class TDBattleInterface:
	"""
	��ħ��ս�ӿ�
	"""
	def __init__( self ):
		pass
	
	def TDB_onClickActButton( self, srcEntityID ):
		"""
		Exposed method
		�ͻ��˵���ͼ��
		"""
		BigWorld.globalData["TaoismAndDemonBattleMgr"].onClickActButton( self.base, self.getCamp() )
		
	def TDB_showTransWindow( self ):
		"""
		define method
		��ʾ���ͽ���
		"""
		endTime = BigWorld.globalData["TDBattleEndTime"]
		record = self.query( "TDB_transData", None )
		if record and record[2] == int( endTime ):
			if record[3]:		# �Ѿ��سǸ�����
				self.client.TDB_showTransWindow( 3 )		# ���ͺʹ��ذ�ť����ʾ
			else:
				self.client.TDB_showTransWindow( 2 )		# ��ʾ�ش���ť
		else:
			self.client.TDB_showTransWindow( 1 )		# ��ʾ���Ͱ�ť
			if record:
				self.remove( "TDB_transData" )

	def TDB_onPlayerLogin( self, srcEntityID ):
		"""
		Exposed method
		��ҵ�½
		"""
		if srcEntityID != self.id: return
		record = self.query( "TDB_transData", None )
		if record:
			if not BigWorld.globalData.has_key( "TDBattleEndTime" ) or BigWorld.globalData["TDBattleEndTime"] != record[2]:
				self.remove( "TDB_transData" )
		BigWorld.globalData["TaoismAndDemonBattleMgr"].onPlayerLogin( self.base, self.getName() )

	def addFightMonster( self, monsterID ):
		"""
		define method
		��ĳ��������Լ���Ϊ��ǰս������ʱ����Ҽ�¼�˹���id
		"""
		fightMonster = self.queryTemp( "TDB_fightingMonster ", [] )
		if monsterID not in fightMonster:
			fightMonster.append( monsterID )
			self.setTemp( "TDB_fightingMonster ", fightMonster )
		
		if not self.findBuffsByBuffID( 199021 ):
			try:
				spell = g_skills[ SKILL_ID ]
			except:
				ERROR_MSG( "%i: skill %i not exist." % ( self.id, SKILL_ID ) )
				return
			spell.use( self, SkillTargetObjImpl.createTargetObjEntity( self ) )			# ����Ҽ�Buff_199021��ʹ����ܵ�����ʱ���Խ�������֪ͨ����ħ��ս������

	def removeFightMonster( self, monsterID ):
		"""
		define method
		���ɾ���˹���id
		"""
		fightMonster = self.queryTemp( "TDB_fightingMonster ", [] )
		if monsterID in fightMonster:
			fightMonster.remove( monsterID )
			self.setTemp( "TDB_fightingMonster ", fightMonster )

	def TDB_transToActPos( self, srcEntityID ):
		"""
		Exposed method
		���͵������
		"""
		if self.id != srcEntityID:
			return
		if not self.transConditionCheck():
			return
		if not BigWorld.globalData.has_key( "TDBattleEndTime" ):
			return
			
		endTime = BigWorld.globalData[ "TDBattleEndTime" ]
		self.set( "TDB_transData", [ self.spaceType, tuple( self.position ), int( endTime ), False ] )
		if self.getCamp() == csdefine.ENTITY_CAMP_TAOISM:
			space = csconst.TDB_TRANSPORT_SPACE_T
			position = csconst.TDB_TRANSPORT_POSITION_T
		else:
			space =  csconst.TDB_TRANSPORT_SPACE_D
			position = csconst.TDB_TRANSPORT_POSITION_D
		self.gotoSpace( space, position, self.direction )
		
	def TDB_transportBack( self, srcEntityID ):
		"""
		Exposed method
		�ص�����ǰλ��
		"""
		if self.id != srcEntityID:
			return
		if not self.transConditionCheck():
			return
			
		record = self.query( "TDB_transData", None )
		if record:
			self.remove( "TDB_transData" )
			self.gotoSpace( record[0], record[1], self.direction )
		else:
			ERROR_MSG( "Player(ID: %s) has not record position!" % self.id )
	
	def TDB_onReviveOnCity( self ):
		"""
		�سǸ�����
		"""
		record = self.query( "TDB_transData", None )
		if record:
			record[3] = True
		
	def TDB_onBattleOver( self, endTime ):
		"""
		define method
		ս��������boss�������߻������
		
		@param endTime : type INT32
		@param endTime : ���λ�Ľ���ʱ��
		"""
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			return
		record = self.query( "TDB_transData", None )
		if not record or record[2] != endTime:			# ˵�����֮ǰû�е㴫�ͻ��߲��Ǳ��λ���˴���
			return
		self.client.TDB_showActTip()