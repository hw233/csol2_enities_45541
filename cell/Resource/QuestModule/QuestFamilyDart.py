# -*- coding: gb18030 -*-
#



from QuestDart import QuestDart
import csstatus
import csdefine

class QuestFamilyDart( QuestDart ):


	def accept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

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
		执行任务实际处理
		"""
		QuestDart.onAccept( self, player, tasks )

		familyMB = player.family_getSelfFamilyEntity()
		
		familyMB.addDartCount()

