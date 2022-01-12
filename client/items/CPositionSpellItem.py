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
	位置施法物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		self.modelPath = "gzawu/unitselect/unitselect.model"	#给一个默认的光圈路径
		self.modelScale = (1,1,1) #缩放系数

	def use( self, owner, target ):
		"""
		使用物品

		@param    owner: 背包拥有者
		@type     owner: Entity
		@param   target: 使用目标
		@type    target: Entity
		@param position: 目标位置,无则为None
		@type  position: tuple or VECTOR3
		@return: STATE CODE
		@rtype:  UINT16
		"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, UseStatus(self ) )

	def checkUse( self, owner ):
		"""
		检测使用者是否能使用该物品
		判断玩家挖宝位置是否合法，如果不合法，则打开“引路蜂、自动寻路”菜单
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
		获得光圈路径和缩放系数
		"""
		spell = self.getSpell()
		if spell:
			return spell.modelScale
		return self.modelScale

	def getModelpath(self):
		"""
		获得光圈模型路径
		"""
		spell = self.getSpell()
		if spell:
			return spell.modelPath
		return self.modelPath

# --------------------------------------------------------------------
# Define.GST_IN_WORLD 状态中的子状态，进入这种状态后，鼠标左键按击事件
# 将会被该子状态截获。
# 210.05.15: by huangyongwei
# modify by wuxo 2012-2-22
# --------------------------------------------------------------------
class UseStatus( BaseStatus ) :
	def __init__( self,item ) :
		BaseStatus.__init__( self )							# 设置该状态下的鼠标形状，并锁定鼠标形状
		self.__item = item
		self.cbID = 0
		self.addSelect()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __leave( self ) :
		"""
		释放该状态
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
		准备 spell 状态按键消息在此处理
		如果想截获哪个按键的消息，只要判断是指定按键并返回 True 即可。
		"""
		if rds.worldCamHandler.handleKeyEvent( down, key, mods ) :
			return True

		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :
			self.__leave()
			return False

		if key == keys.KEY_LEFTMOUSE and mods == 0 :						# 鼠标左键按下时被调用
			if down :
				player = BigWorld.player()
				pos = gbref.cursorToDropPoint()								# 获取鼠标按下时所击中的地面位置
				if pos is None: return True
				target = SkillTargetObjImpl.createTargetObjPosition( pos )	# 封装位置目标
				if self.__item.validPosition( player, target ) == csstatus.SKILL_GO_ON :
					self.__item.useToPosition( player, target )
			else :
				self.__leave()
			return True
		elif key == keys.KEY_ESCAPE or key == keys.KEY_RIGHTMOUSE :		# 取消该子状态
			self.__leave()
			return True
		elif checkSkillShortcut( key, mods ) and down:
			self.__leave()
			return True

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		鼠标移动时被调用
		"""
		if rds.worldCamHandler.handleMouseEvent( dx, dy, dz ) :				# 旋转镜头中
			return True
		self.addSelect()

	def addSelect(self):
		"""
		加光圈
		"""
		pos = gbref.cursorToDropPoint()		# 获取鼠标按下时所击中的地面位置
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
	判断按键是否是技能快捷键
	"""
	sc = rds.shortcutMgr.getSkillbarSC()
	skillbars = []
	for i in sc:
		skillbars.append( i.shortcutString)
	if keys.shortcutToString( key, mod ) in skillbars:
		return True
	return False