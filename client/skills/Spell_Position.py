# -*- coding: gb18030 -*-
#
# $Id: Spell_Position.py,v 1.1 2008-07-24 08:40:51 kebiao Exp $
#modify by wuxo 2012-2-22
"""
Spell�����ࡣ
"""
import BigWorld
import Define
import keys
from bwdebug import *
import gbref 	
from gbref import rds
from StatusMgr import BaseStatus
from UnitSelect import unitSelect
from SpellBase import *
import SkillTargetObjImpl
import csstatus
import csdefine
import csarithmetic
from config.client.NpcSkillName import Datas as npcSkillName

"""
��һ��λ��ʩ���� ��player�����λ��ʩ��ʱ�� �ͻ��˵��ü���ͨ�ýṹspell, ������spell��֪ͨ�ͻ����ϲ�
�����λ��ʩ���� �ϲ������λ�ú�ͨ��SkillTargetObjImpl.createTargetObjPosition( (0,0,0) )��װһ��target
���ü��ܵ�spellToPosition�ӿڼ��ɡ�
"""
class Spell_Position( Spell ):
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )
		self.modelPath = "gzawu/unitselect/unitselect.model"	#��һ��Ĭ�ϵĹ�Ȧ·��
		self.modelScale = (1,1,1) #����ϵ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self.param3 = str( dict["param3"] ).split(";")
		if len(self.param3) >= 2:
			self.modelPath = self.param3[-2]
			self.modelScale = eval(self.param3[-1])

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		return csstatus.SKILL_GO_ON

	def spell( self, caster, target ):
		"""
		�����������Spell����

		@param caster:		ʩ����Entity
		@type  caster:		Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, SpellStatus(self ) )		# ���� Spell ��״̬

	def validPosition( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return Spell.useableCheck( self, caster, target )

	def spellToPosition( self, caster, target ):
		"""
		�����������Spell����
		
		@param caster:		ʩ����Entity
		@type  caster:		Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		assert target.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION, "target is not position."
		Spell.spell( self, caster, target )

	def rotate( self, caster, receiver ):
		pass

	def getSpellScale(self):
		"""
		��ù�Ȧ·��������ϵ��
		"""
		return self.modelScale

	def getModelpath(self):
		"""
		��ù�Ȧģ��·��
		"""
		return self.modelPath

class Spell_ChasePosition( Spell_Position ):
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Spell_Position.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell_Position.init( self, dict )
		self.eid = 0
		self.caster = None

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

		dstPos = targetObject.getObjectPosition()
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, dstPos, dstPos + (0,-20,0) )	 # ����ײ����ֹ��ͣ���ڿ���
		self.eid = BigWorld.createEntity( "CameraEntity", caster.spaceID, 0, endDstPos, (0,0,0), {} )
		BigWorld.callback(0.01, self.onCreate)
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

# --------------------------------------------------------------------
# Define.GST_IN_WORLD ״̬�е���״̬����������״̬�������������¼�
# ���ᱻ����״̬�ػ�
# 210.05.15: by huangyongwei
# modify by wuxo 2012-2-22
# --------------------------------------------------------------------
class SpellStatus( BaseStatus ) :
	def __init__( self,spell ) :
		BaseStatus.__init__( self )							# ���ø�״̬�µ������״�������������״
		self.__spell = spell
		self.cbID = 0
		self.addSelect()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __leave( self ) :
		"""
		�ͷŸ�״̬
		"""
		if self.cbID != 0:
			BigWorld.cancelCallback( self.cbID )
		unitSelect.hideSpellSite()
		rds.statusMgr.leaveSubStatus( Define.GST_IN_WORLD, self.__class__ )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods  ) :
		"""
		׼�� spell ״̬������Ϣ�ڴ˴���
		�����ػ��ĸ���������Ϣ��ֻҪ�ж���ָ������������ True ���ɡ�
		"""
		if rds.worldCamHandler.handleKeyEvent( down, key, mods ) :
			return True

		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :
			self.__leave()
			return False

		if key == keys.KEY_LEFTMOUSE and mods == 0 :						# ����������ʱ������
			if down :
				player = BigWorld.player()
				pos = gbref.cursorToDropPoint()								# ��ȡ��갴��ʱ�����еĵ���λ��
				if pos is None: return True
				target = SkillTargetObjImpl.createTargetObjPosition( pos )	# ��װλ��Ŀ��
				if self.__spell.validPosition( player, target ) == csstatus.SKILL_GO_ON :
					self.__spell.spellToPosition( player, target )
			else :
				self.__leave()
			return True
		elif key == keys.KEY_ESCAPE or key == keys.KEY_RIGHTMOUSE :		# ȡ������״̬
			self.__leave()
			return True
		elif checkSkillShortcut( key, mods ) and down:
			self.__leave()
			return True

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		����ƶ�ʱ������
		"""
		if rds.worldCamHandler.handleMouseEvent( dx, dy, dz ) :				# ��ת��ͷ��
			return True
		self.addSelect()

	def addSelect( self ):
		"""
		�ӹ�Ȧ
		"""
		pos = gbref.cursorToDropPoint()		# ��ȡ��갴��ʱ�����еĵ���λ��
		if pos is None: return

		player = BigWorld.player()
		target = SkillTargetObjImpl.createTargetObjPosition( pos )
		if self.__spell.validPosition( player, target ) == csstatus.SKILL_GO_ON:
			unitSelect.setInRangeTexture()
		else:
			unitSelect.setOutOfRangeTexture()
		unitSelect.setSpellSize( 3.0 )
		unitSelect.setSpellSite( pos )
		if self.cbID != 0:
			BigWorld.cancelCallback( self.cbID )

		self.cbID = BigWorld.callback( 0.01, self.addSelect )

def checkSkillShortcut( key, mod ):
	"""
	�жϰ����Ƿ��Ǽ��ܿ�ݼ�
	edit by wuxo
	"""
	sc = rds.shortcutMgr.getSkillbarSC()
	skillbars = []
	for i in sc:
		skillbars.append( i.shortcutString)
	if keys.shortcutToString( key, mod ) in skillbars:
		return True
	return False