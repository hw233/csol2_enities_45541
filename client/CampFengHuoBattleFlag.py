# -*- coding: gb18030 -*-
#

"""
FengHuoLianTianBattleFlag
�������ս��ͻ��˽ű�
"""
import BigWorld
import Const
from gbref import rds
from QuestBox import QuestBox
import event.EventCenter as ECenter

class CampFengHuoBattleFlag( QuestBox ):
	"""
	�������ս��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		QuestBox.__init__( self )
		self.ownerEffect = None

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld:
			return
		QuestBox.onCacheCompleted( self )
		self.playOwnerEffect( )
	
	def onModelLoadFinish( self, isStatic, event, pyModel ):
		QuestBox.onModelLoadFinish( self, isStatic, event, pyModel )
		self.playOwnerEffect()
		
	def set_ownCamp( self, oldOwnCamp ):
		"""
		�������ı�
		"""
		#ECenter.fireEvent( "EVT_ON_BATTLE_FLAG_OWNTONG_CHANGE", self )
		self.playOwnerEffect( )
	
	def set_utype( self, oldValue ):
		"""
		when the utype changed, it will be called
		"""
		pass
		
	def playOwnerEffect( self ):
		"""
		���Ź�Ч
		"""
		if self.ownerEffect :
			self.ownerEffect.stop()
			self.ownerEffect = None
		p = BigWorld.player()
		if hasattr( p, "getCamp" ):
			if self.ownCamp == p.getCamp() :
				effectID = Const.FHLT_BATTLEFLAG_OTHER_EFFECT_ID
			else:
				effectID = Const.FHLT_BATTLEFLAG_OWN_EFFECT_ID
			type = self.getParticleType()
			effect = rds.skillEffect.createEffectByID( effectID, self.getModel(), self.getModel(), type, type )
			if effect:
				effect.start()
			self.ownerEffect = effect