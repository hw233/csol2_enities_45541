# -*- coding: gb18030 -*-

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_66012( Buff_Normal ):
	"""
	�����������ʻ��Ƿ��������� 
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.phy = 0.0
		self.mag = 0.0
		self.magDoubleHit = 0.0
		self.phyDoubleHit = 0.0


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		Param1 ��ʽ��a;b;c;d
			a�����������Ӱٷֱ�
			b�������������Ӱٷֱ�
			c�������������Ӱٷֱ�
			d���������������Ӱٷֱ�
		0.0 =< a/b/c/d =< 1.0
		"""
		

		Buff_Normal.init( self, dict )
		self._p1 =  dict[ "Param1" ]
		if self._p1 != "" :
			tmp = self._p1.split( ";" ) # bug here
			self.phy = float( tmp[0] ) * csconst.FLOAT_ZIP_PERCENT
			self.mag = float( tmp[1] ) * csconst.FLOAT_ZIP_PERCENT
			self.phyDoubleHit = float( tmp[2] ) * csconst.FLOAT_ZIP_PERCENT
			self.magDoubleHit = float( tmp[3] ) * csconst.FLOAT_ZIP_PERCENT
			
		
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
		
		#������
		receiver.damage_min_percent += self.phy
		receiver.damage_max_percent += self.phy
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		
		#��������
		receiver.magic_damage_percent += self.mag
		receiver.calcMagicDamage()
		
		#��������
		receiver.double_hit_probability_percent += self.phyDoubleHit
		receiver.calcDoubleHitProbability()
		
		#����������
		receiver.magic_double_hit_probability_percent += self.magDoubleHit
		receiver.calcMagicDoubleHitProbability()
		
	
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
		
		#������
		receiver.damage_min_percent -= self.phy
		receiver.damage_max_percent -= self.phy
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		
		#��������
		receiver.magic_damage_percent -= self.mag
		receiver.calcMagicDamage()
		
		#��������
		receiver.double_hit_probability_percent -= self.phyDoubleHit
		receiver.calcDoubleHitProbability()
		
		#����������
		receiver.magic_double_hit_probability_percent -= self.magDoubleHit
		receiver.calcMagicDoubleHitProbability()
			
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )

		#������
		receiver.damage_min_percent += self.phy
		receiver.damage_max_percent += self.phy
		#��������
		receiver.magic_damage_percent += self.mag
		#��������
		receiver.double_hit_probability_percent += self.phyDoubleHit
		#����������
		receiver.magic_double_hit_probability_percent += self.magDoubleHit
		
