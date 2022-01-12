# -*- coding: gb18030 -*-
#



from QuestDart import QuestDart
import csstatus
import csdefine

class QuestFamilyDart( QuestDart ):


	def accept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		
		familyMB = player.family_getSelfFamilyEntity()
		
		if familyMB is None:
			player.statusMessage( csstatus.FAMILY_DART_NOT_EXIST )
			return
		
		familyMB.queryDartCount( player.base, self.getID() )
		

	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		QuestDart.onAccept( self, player, tasks )

		familyMB = player.family_getSelfFamilyEntity()
		
		familyMB.addDartCount()

