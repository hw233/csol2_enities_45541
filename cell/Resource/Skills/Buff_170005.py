# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csdefine
from config.server.FlawMonster import Datas as g_flawMonster
import random

class Buff_170005( Buff_Normal ):
	"""
	�����ݻ�BUFF
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0
		self.param4 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( dict["Param1"] )			# ��������ID
		self.param2 = int( dict["Param2"] )			# �ݻ�����ID

		oddsList = dict["Param3"].split(",")
		if len( oddsList ) == 2:
			self.param3 = int( oddsList[0] )		# ��������
			self.param4 = int( oddsList[1] )		# �ݻ�����

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ��ߣ�None��ʾ������
		@type  receiver: Entity
		"""
		if caster is None: return
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		if receiver.className not in g_flawMonster: return

		buffIndex = receiver.getBuffIndexByType( csdefine.BUFF_TYPE_FLAW )
		if buffIndex == -1:
			odds = self.param3
			skillID = self.getSourceSkillID()/1000
			odds += caster.skillBuffOdds.getOdds( skillID ) * 100
			if random.randint( 1, 100 ) <= odds:
				caster.spellTarget( self.param1, receiver.id )
		else:
			if random.randint( 1, 100 ) <= self.param4:
				caster.spellTarget( self.param2, receiver.id )
