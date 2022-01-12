# -*- coding: gb18030 -*-

import Define
from CItemBase import CItemBase
import csstatus
import BigWorld
import ItemAttrClass
import TextFormatMgr
from gbref import rds
import gbref
from StatusMgr import BaseStatus
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import BigWorld
import Define
import keys
from bwdebug import *
from UnitSelect import unitSelect
import SkillTargetObjImpl
import csstatus
import csdefine

class CPositionSpellItem( CItemBase ) :
	"""
	λ��ʩ����Ʒ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		self.modelPath = "gzawu/unitselect/unitselect.model"	#��һ��Ĭ�ϵĹ�Ȧ·��
		self.modelScale = (1,1,1) #����ϵ��

	def use( self, owner, target ):
		"""
		ʹ����Ʒ

		@param    owner: ����ӵ����
		@type     owner: Entity
		@param   target: ʹ��Ŀ��
		@type    target: Entity
		@param position: Ŀ��λ��,����ΪNone
		@type  position: tuple or VECTOR3
		@return: STATE CODE
		@rtype:  UINT16
		"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, UseStatus(self ) )

	def checkUse( self, owner ):
		"""
		���ʹ�����Ƿ���ʹ�ø���Ʒ
		�ж�����ڱ�λ���Ƿ�Ϸ���������Ϸ�����򿪡���·�䡢�Զ�Ѱ·���˵�
		"""

		state = CItemBase.checkUse( self, owner )
		if state != csstatus.SKILL_GO_ON:
			return state
		return csstatus.SKILL_GO_ON

	def useToPosition( self, player, target ):
		"""
		"""
		assert target.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION, "target is not position."
		player.cell.useItem( self.uid, target )

	def validPosition( self, player, target ):
		"""
		"""
		spell = self.getSpell()
		if spell:
			return spell.validPosition( player, target )
		return csstatus.SKILL_GO_ON

	def getSpellScale(self):
		"""
		��ù�Ȧ·��������ϵ��
		"""
		spell = self.getSpell()
		if spell:
			return spell.modelScale
		return self.modelScale

	def getModelpath(self):
		"""
		��ù�Ȧģ��·��
		"""
		spell = self.getSpell()
		if spell:
			return spell.modelPath
		return self.modelPath

# --------------------------------------------------------------------
# Define.GST_IN_WORLD ״̬�е���״̬����������״̬�������������¼�
# ���ᱻ����״̬�ػ�
# 210.05.15: by huangyongwei
# modify by wuxo 2012-2-22
# --------------------------------------------------------------------
class UseStatus( BaseStatus ) :
	def __init__( self,item ) :
		BaseStatus.__init__( self )							# ���ø�״̬�µ������״�������������״
		self.__item = item
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
				if self.__item.validPosition( player, target ) == csstatus.SKILL_GO_ON :
					self.__item.useToPosition( player, target )
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

	def addSelect(self):
		"""
		�ӹ�Ȧ
		"""
		pos = gbref.cursorToDropPoint()		# ��ȡ��갴��ʱ�����еĵ���λ��
		if pos is None: return

		player = BigWorld.player()
		target = SkillTargetObjImpl.createTargetObjPosition( pos )
		if self.__item.validPosition( player, target ) == csstatus.SKILL_GO_ON:
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
	"""
	sc = rds.shortcutMgr.getSkillbarSC()
	skillbars = []
	for i in sc:
		skillbars.append( i.shortcutString)
	if keys.shortcutToString( key, mod ) in skillbars:
		return True
	return False