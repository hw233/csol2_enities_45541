# -*- coding: gb18030 -*-
#
#���������ƶ� ���ܵĿͻ��˽ű�
# edit by wuxo 2012-4-27

import csdefine
import BigWorld
from gbref import rds
import SkillTargetObjImpl
from SpellBase import Spell
from config.client.NpcSkillName import Datas as npcSkillName

class Spell_MoveEffect( Spell ):
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )
		self._offsetYaw = 0.0
		self.eid = 0
		self.caster = None
		self._isOnce = None	
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict[ "param2" ] != "":
			self._offsetYaw = float( dict[ "param2" ] )
		else:
			self._offsetYaw = 0.0
		self._isOnce = bool( int( dict[ "param3" ] ) )
		
		
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.hasCast = True
		skillID = self.getID()

		# �Զ������ԣ���ֻ�Ქ��һ��
		self.pose.cast( caster, skillID, targetObject )

		pos = targetObject.getObjectPosition()
		model = caster.getModel()
		if model:
			scale = model.scale[0]
			k = scale * model.height * 0.8
		dPos = ( pos[0], pos[1] + k, pos[2] )
		self.eid = BigWorld.createEntity( "CameraEntity", caster.spaceID, 0, dPos, (0,0,0), {"isFall":False} )
		BigWorld.callback(0.1, self.onCreate)
		self.caster = caster

		# ����������ʾ
		speller = caster  #���¸�ֵ����ֹ������û���
		if hasattr( speller, 'getOwner' ):
			speller = speller.getOwner()

		player = BigWorld.player()
		if player is None: return
		if speller is None: return

		if player.position.distTo( speller.position ) > 20: return
		if hasattr( caster, "className" ):
			sk_id = str( skillID )[:-3]
			if not sk_id: return		# ���Ϊ�գ�ֱ�ӷ���
			orgSkillID = int( sk_id )	# ֧�����ñ�ɱ�ȼ�NPC������д
			skillIDs = npcSkillName.get( caster.className, [] )
			if orgSkillID in skillIDs or skillID in skillIDs:
		 		caster.showSkillName( skillID )
				return
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			caster.showSkillName( skillID )

	def isMoveSpell( self ):
		"""
		�ж��Ƿ�������������
		@return: BOOL
		"""
		return True
	
	def onCreate(self):
		"""
		������ص�
		"""
		if self.eid:
			en = BigWorld.entity( self.eid )
			en.model = BigWorld.Model("")
			t = SkillTargetObjImpl.createTargetObjEntity(en)
			rds.skillEffect.playCastEffects( self.caster, t, self.getID() )
			BigWorld.callback( 30, self.ondestroy )
			
			
	def ondestroy(self):
		"""
		ɾ��������ʵ��
		"""
		BigWorld.destroyEntity( self.eid )