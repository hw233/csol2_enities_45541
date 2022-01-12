# -*- coding:gb18030 -*-


import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_299034( Buff_Normal ):
	"""
	����Ϊ������ʾ�����ӡ����������ʾ����С��
	Buff�Ĺ��ܣ�
	�ƶ��ٶ�����/��С
	����������������/��С
	����������������/��С
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# �ƶ��ٶ�����/��С	
		self._p2 = 0		# ����������������/��С
		self._p3 = 0		# ����������������/��С
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100		# �ƶ��ٶȸı�ٷֱ�
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100		# ����������������/��С�ٷֱ�
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  * 100		# ����������������/��С�ٷֱ�
		
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
		receiver.move_speed_percent += self._p1								# �ƶ��ٶ�
		receiver.calcMoveSpeed()
		
		receiver.armor_percent += self._p2									# �������
		receiver.calcArmor()
		receiver.magic_armor_percent += self._p2							# ��������
		receiver.calcMagicArmor()
		
		receiver.damage_min_percent += self._p3								# ��������
		receiver.calcDamageMin()
		receiver.damage_max_percent += self._p3
		receiver.calcDamageMax()
		receiver.magic_damage_percent += self._p3							# ����������
		receiver.calcMagicDamage()

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
		receiver.move_speed_percent -= self._p1
		receiver.armor_percent += self._p2									# �������
		receiver.magic_armor_percent += self._p2							# ��������
		receiver.damage_min_percent += self._p3
		receiver.damage_max_percent += self._p3
		receiver.magic_damage_percent += self._p3
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.move_speed_percent -= self._p1	
		receiver.calcMoveSpeed()
		
		receiver.armor_percent -= self._p2									# �������
		receiver.calcArmor()
		receiver.magic_armor_percent -= self._p2							# ��������
		receiver.calcMagicArmor()
		
		receiver.damage_min_percent -= self._p3
		receiver.calcDamageMin()
		receiver.damage_max_percent -= self._p3
		receiver.calcDamageMax()
		receiver.magic_damage_percent -= self._p3
		receiver.calcMagicDamage()
		