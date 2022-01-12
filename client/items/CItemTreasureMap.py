# -*- coding: gb18030 -*-
"""
藏宝图物品类。
"""

import BigWorld
import csconst
import csstatus
import ItemAttrClass
import SkillTargetObjImpl
import skills
import event.EventCenter as ECenter

from gbref import rds
from CItemBase import CItemBase
from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CItemTreasureMap


class CItemTreasureMap( CItemBase ):
	"""
	藏宝图物品类
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: 物品的原始数据
		"""
		CItemBase.__init__( self, srcData )

	def description( self, reference ):
		"""
		产生描述

		@param reference: 玩家entity,表示以谁来做为生成描述的参照物
		@type  reference: Entity
		@return:          物品的字符串描述
		@rtype:           ARRAY of str
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品名字，根据物品的品质决定物品名字的颜色
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = EquipQualityExp.instance().getColorByQuality( self.getQuality() ) )
		self.desFrame.SetDescription("name" , nameDes)
		# 物品类型
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# 需求声望
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
		#是否绑定
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription( "bindType", desBind )
		#是否唯一
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CItemTreasureMap[1] )
		# 是否可出售
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CItemTreasureMap[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )

		# 藏宝图的坐标信息
		treasure_spaceName = ""
		treasure_position = ""
		if self.extra.has_key( "treasure_space" ) and self.extra.has_key( "treasure_position" ):
			spaceName = self.query("treasure_space")
			treasure_space = rds.mapMgr.getWholeArea( spaceName, reference.position[1] )
			treasure_spaceName = treasure_space.spaceName
			treasure_position = self.query("treasure_position")
			treasure_position = eval( treasure_position )
			treasure_position = str( int(treasure_position[0]) ) + ':' + str( int(treasure_position[2]) )

		# 取得额外的描述1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			des1 = des1 % ( treasure_spaceName, treasure_position )
			self.desFrame.SetDescription( "describe1", des1 )
		# 取得额外的描述2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
			des2 = des2 % self.getLevel()
			self.desFrame.SetDescription( "describe2", des2 )
		# 取得额外的描述3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
			self.desFrame.SetDescription( "describe3", des3 )

		return self.desFrame.GetDescription()

	def use( self, owner, target, position = (0.0, 0.0, 0.0) ):
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
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			if checkResult == csstatus.SKILL_TREASURE_POS_NOT_VALID:
				ECenter.fireEvent( "EVT_ON_SHOW_AUTO_FIND_PATH_MENU", self.getOrder() )
			return checkResult

		sk = skills.getSkill( self.query( "spell" ) )
		state = sk.useableCheck( owner, SkillTargetObjImpl.createTargetObjEntity(target) )
		return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

	def checkUse( self, owner ):
		"""
		检测使用者是否能使用该物品
		判断玩家挖宝位置是否合法，如果不合法，则打开“引路蜂、自动寻路”菜单
		"""

		state = CItemBase.checkUse( self, owner )
		if state != csstatus.SKILL_GO_ON:
			return state
		if not self.isTreasurePosValid():
			return csstatus.SKILL_TREASURE_POS_NOT_VALID
		return csstatus.SKILL_GO_ON

	def isTreasurePosValid( self, offset = 20 ):
		"""
		检查玩家挖宝位置是否合法(是否处于某个地图spaceName的坐标position范围内)copy from Spell_322398002.py,change a little

		@param 	offset		:	允许的范围差距，必须为正值
		@type 	offset		:	Tuple
		"""
		treasureSpace = self.query( "treasure_space", "" )		# 取出藏宝图中的地图信息
		treasurePosStr = self.query( "treasure_position", None )# 取出藏宝图中的坐标信息
		treasurePos = eval( treasurePosStr )

		player = BigWorld.player()
		if player.getSpaceLabel() != treasureSpace:
			return False
		negativeOffset = 0 - offset
		currPos = player.position
		x = float(currPos[0]) - float(treasurePos[0])
		z = float(currPos[2]) - float(treasurePos[2])
		return ( x >= negativeOffset and x <= offset and z >= negativeOffset and z <= offset )
