# -*- coding: gb18030 -*-

import BigWorld
import Define
from gbref import rds
from SkillTrap import SkillTrap
from Function import Functor

class MoveTrap( SkillTrap ):
	"""
	���ƶ�������
	"""
	def __init__( self ):
		"""
		"""
		SkillTrap.__init__( self )

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.PlayerAvatarFilter()

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		# ��ΪһЩ��̯����Ҳ�õ����entity.�Ҹ�entity�ǲ��ɼ���,����Ӧ�����δ���entity��ģ��
		if len( self.modelNumber ) == 0: return
		# ģ�Ϳ��԰���Ӧ�Ĺ�Ч
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		if pyModel is None:
			return
		self.setModel( pyModel, event )
		am = BigWorld.ActionMatcher( self )    #����ģ��am
		self.model.motors = ( am, )
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )
		self.setVisibility( False )

	def moveToPosFC( self, pos, speed, dir ):
		"""
		define method
		������֪ͨ�ƶ���ĳ��
		"""
		self.setVisibility( True )
		SkillTrap.moveToPosFC( self, pos, speed, dir )

	def onDestroy( self ):
		"""
		define method.
		������Ч�����ƹ���������Ч
		"""
		model = self.getModel()
		if model:
			infos = rds.npcModel._datas[self.modelNumber]
			effectID = infos.get( "blast_effect", "" )
			type = self.getParticleType()
			effect = rds.skillEffect.createEffectByID( effectID, model, model, type, type )
			if effect:
				effect.start()
			self.setVisibility( False )

	def fadeInModel( self ):
		"""
		����ģ�ͣ�MoveTrap������Ĵ���
		"""
		pass

	def refreshVisible( self ):
		"""
		"""
		pass