# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster


class MonsterShuijing( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )


	def onDie( self, killerID ):
		"""
		virtual method.

		�������鴦��
		
		"""
		if self.className == "20752011":	#��ˮ��������ʹ�����أ������ʽ�ȼ��ܺ��ʣ�
			for i in self.entitiesInRangeExt( 5.0, "Role", self.position ):
				i.setHP( int( i.HP * 0.8 ) )
			for i in self.entitiesInRangeExt( 5.0, "Pet", self.position ):
				i.setHP( int( i.HP * 0.8 ) )

		Monster.onDie( self, killerID )
		
		