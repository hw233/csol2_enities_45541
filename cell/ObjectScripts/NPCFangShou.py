# -*- coding: gb18030 -*-

from Monster import Monster

class NPCFangShou( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		
	def onHPChanged( self, selfEntity ):
		"""
		Ѫ�������ı�
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase :
			return
		spaceBase.cell.remoteScriptCall( "onFangShouNpcHPChanged", ( selfEntity.HP, selfEntity.HP_Max ) )