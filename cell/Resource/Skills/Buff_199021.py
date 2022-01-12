# -*- coding: gb18030 -*-

import copy
import csdefine
from bwdebug import *
from Resource.SkillLoader import g_skills
from Buff_Normal import Buff_Normal

class Buff_199021( Buff_Normal ):
	"""
	��ħ��ս����buff
	��buff��һ����ͳ�Ʊ��������ļ��ܡ��ӵ������ߵġ�������ʱ�����ļ����б�springReceiverCureList������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
	
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		if receiver.getEntityType() != csdefine.ENTITY_TYPE_ROLE:			# ��buffֻ�����������
			return
		try:
			skill = g_skills[ self.param1 ]
		except:
			ERROR_MSG( "%i: skill %i not exist." % ( self.id, self.param1 ) )
			return
		receiver.appendReceiverCure( buffData[ "skill" ] )
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		fightMonster = receiver.queryTemp( "TDB_fightingMonster ", [] )
		if not fightMonster:
			return False
			
		for monsterID in copy.copy( fightMonster ):
			monster = BigWorld.entities.get( monsterID )
			if not monster or monster.targetID != receiver.id:
				fightMonster.remove( monsterID )
			
		if len( fightMonster ) == 0:					# ���û�б��κ���ħ��ս����ѡΪ��ǰս��Ŀ�꣬��buff�Ƴ�
			receiver.removeTemp( "TDB_fightingMonster " )
			return False
			
		receiver.setTemp( "TDB_fightingMonster ", fightMonster )
		return Buff_Normal.doLoop( self, receiver, buffData )
			
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeCasterCure( buffData[ "skill" ].getUID() )