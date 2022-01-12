# -*- coding: gb18030 -*-

# 10 �����鸱�� 
# alienbrain://PROJECTSERVER/����Online/��ɫ�汾/09_��Ϸ����/05_�������/04_���鸱��/10�����鸱��.docx
# by mushuang 

from SpaceCopy import SpaceCopy


class SpaceCopyBeforeNirvana( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )		
		self.spawnMonstersList = {}
		
	def addSpawnPointCopy( self, mailbox, entityName ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( entityName ):
			self.spawnMonstersList[entityName].append( mailbox )
		else:
			self.spawnMonstersList[entityName] = [mailbox]
		
	def openDoor( self, params ):
		"""
		define method��ͨ��spawnPoint�ҵ���entity������entity
		"""
		for e in self.spawnMonstersList[ params["entityName"] ]:
			#e.cell.openDoor()
			e.cell.remoteCallScript( "openDoor", [ False, ] )
