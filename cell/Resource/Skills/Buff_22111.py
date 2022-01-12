# -*- coding: gb18030 -*-

"""
�Ŀ�����
"""

from Buff_Normal import Buff_Normal

class Buff_22111( Buff_Normal ):
	"""
	�Ŀ�����buff����������Ǳ�ܣ���Ȼ��ָ������Чʱ���ڣ���ֵ�൱�����û���κ�״̬�»�þ�������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 					# ����Ǳ�ܵĹ�ʽ--�;���ֵ������ͬ
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 					# ÿ��������ɹ�೤ʱ�䣨 ��λ���� ��--�;���ֵ������ͬ
		self._hpVal = int( self._p1[ 3:len( self._p1 ) ] )		# ���ӵľ���ֵ
		self._hpOpt = self._p1[ 2:3 ]					# ������

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��
		"""
		# �ж��Ƿ����չ�ԡ�Ϸ�ʱ����
		if receiver.isSunBathing() and receiver.sunBathDailyRecord.sunBathCount < self._p2:
			increasePotential = self.getIncreasePotential( receiver.level, self._hpOpt, self._hpVal )
			receiver.addPotential ( increasePotential )
			
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def getIncreasePotential( self, level, opration, value ):
		"""
		���ݹ�ʽ��ü��ٵ�Ѫ��
		"""
		return level + value