# -*- coding: gb18030 -*-
#
# $Id: PetName.py,v 1.7 2008-06-27 03:20:42 huangyongwei Exp $

"""
implement float name of the character

2007.12.17: writen by huangyongwei
2009.02.13: tidy up by huangyongwei
"""

import csdefine
import event.EventCenter as ECenter
from guis.common.PyGUI import PyGUI
from PetFormulas import formulas
from guis import *
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from FloatName import FloatName
from LV_HP import LV_HP
from DoubleName import DoubleName

class PetName( FloatName ) :
	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/petname.gui" )

	def __init__( self ) :
		wnd = GUI.load( "guis/otheruis/floatnames/petname.gui" )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.viewInfoKey_ = "pet"							# 其他玩家宠物
		self.__initialize( wnd )		

	def __initialize( self, wnd ) :
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleDoubleName( False )
		self.__pyLVHP = LV_HP( wnd.lvhp )
		self.__pyLVHP.hpValue = 0
		self.pyElements_ = [self.__pyLVHP, self.pyLbName_]

	def dispose( self ) :
		self.__pyLVHP.dispose()
		FloatName.dispose( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_ENTITY_LEVEL_CHANGED"] = self.__onLevelChanged
		self.triggers_["EVT_ON_PET_ATTR_CHANGED"] = self.__onSpeciesChanged
		self.triggers_["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onTeammateAdded
		self.triggers_["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onTeammateLeft
		self.triggers_["EVT_ON_TEAM_DISBANDED"] = self.__onTeamDisbanded
		self.triggers_["EVT_ON_ENTITY_PK_STATE_CHANGED"] = self.__onOwnerPkStateChanged
		self.triggers_["EVT_ON_ROLE_PKMODE_CHANGED"] = self.__onPKModeChanged
		self.triggers_["EVT_ON_ROLE_HAS_SAFEAREA_FLAG"] = self.__onRoleSafeChanged
		self.triggers_["EVT_ON_ROLE_ACTWORD_CHANGED"] = self.__onRoleActWordChanged
		self.triggers_["EVT_ON_ROLE_SYSPKMODE_CHANGED"] = self.__onSysModeChange	# 系统PK改变
		self.triggers_["EVT_ON_ROLE_MODEL_INFO_CHANGED"] = self.__onRoleModelInfoChanged
		FloatName.registerTriggers_( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetNameColor( self ) :
		"""
		根据角色与宠物的等级差设置宠物名字的颜色
		"""
		if formulas.isHierarchy( self.entity_.species, csdefine.PET_HIERARCHY_GROWNUP ) :
			self.pyLbName_.leftColor = 255, 255, 255, 255
		elif formulas.isHierarchy( self.entity_.species, csdefine.PET_HIERARCHY_INFANCY1 ) :
			self.pyLbName_.leftColor = 0, 128, 255, 255
		else :
			self.pyLbName_.leftColor = 254, 163, 8, 255

	# -------------------------------------------------
	def __onLevelChanged( self, pet, oldLevel, newLevel ) :
		"""
		等级改变时该方法被调用
		"""
		if self.entity_ is None or self.entity_ != pet : return
		self.__pyLVHP.level = newLevel
		self.layout_()

	def __onSpeciesChanged( self, dbid, attrName ) :
		"""
		宠物类型改变时该方法被调用
		"""
		if self.entity_ is None or dbid != self.entity_.databaseID : return
		if attrName != "species" : return
		self.__resetNameColor()

	def __updateViewInfo( self ):
		"""
		设置元素的可见性
		"""
		self.__pyLVHP.toggleHPBar( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "HP" ) )
		self.__pyLVHP.toggleLevel( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "HP" ) )
		if self.entity_ != BigWorld.player().pcg_getActPet() : 								# 不是自己的宠物可以设置
			#visible = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "model" )
			self.entity_.updateVisibility()

	def __onTeammateAdded( self, joinor ):
		"""
		当一个队友加入时被调用
		"""
		if self.entity_ is None:return
		if self.viewInfoKey_ == "playerPet" :return
		if BigWorld.player().isTeamMember( self.entity_.ownerID ):
			self.viewInfoKey_ = "teammatePet"
			self.__updateViewInfo()
			self.layout_()

	def __onTeammateLeft( self, objectID ):
		"""
		当一个队友离开时被调用
		"""
		if self.entity_ is None:return
		if self.viewInfoKey_ != "teammatePet":return
		if objectID == self.entity_.ownerID:
			self.viewInfoKey_ = "pet"
			self.__updateViewInfo()
			self.layout_()

	def __onTeamDisbanded( self ) :
		if self.entity_ is None:return
		if self.viewInfoKey_ != "teammatePet" : return
		self.viewInfoKey_ = "pet"
		self.__updateViewInfo()
		self.layout_()
	
	def __onOwnerPkStateChanged( self, role ):
		"""
		主人PK状态改变
		"""
		if self.entity_ is None:return
		owner = self.entity_.getOwner()
		if owner is None:return
		if owner.id != role.id:return
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )

	def __onPKModeChanged( self, role, pkMode ):
		"""
		角色pk模式改变
		"""
		if self.entity_ is None:return
		owner = self.entity_.getOwner()
		if owner is None:return
		if owner.id != role.id:return
		relation = self.getRelation( owner )
		self.__setHPBarColor( relation )

	def __onRoleSafeChanged( self, role, safeFlag ):
		"""
		角色安全区标识改变
		"""
		if self.entity_ is None:return
		owner = self.entity_.getOwner()
		if owner is None:return
		if role.id != owner.id: return
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )

	def __onRoleActWordChanged( self, role, old, new ):
		"""
		角色actWord改变
		"""
		if self.entity_ is None:return
		owner = self.entity_.getOwner()
		if owner is None:return
		if role.id != owner.id: return
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )

	def __onSysModeChange( self, role, newVal ):
		"""
		系统pk模式改变
		"""
		if self.entity_ is None:return
		owner = self.entity_.getOwner()
		if owner is None:return
		if role.id != owner.id:return
		relation = self.getRelation( role )
		self.__setHPBarColor( relation )
	
	def __setHPBarColor( self, relation ):
		"""
		设置血条颜色
		"""
		texturePath = "guis/otheruis/floatnames/%s.dds"
		if relation == csdefine.RELATION_FRIEND:
			self.__pyLVHP.hpTexture = texturePath%"hpbar_0"
		else:
			self.__pyLVHP.hpTexture = texturePath%"hpbar"

	def __onRoleModelInfoChanged( self ):
		"""
		"""
		if self.entity_ is None:return
		self.entity_.visibilitySettingChanged( "pet", rds.viewInfoMgr.getSetting( "pet", "model" ) )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onViewInfoChanged_( self, infoKey, itemKey, oldValue, value ) :
		"""
		显示信息改变时被触发
		"""
		if self.viewInfoKey_ != infoKey : return
		if itemKey == "HP" :
			self.__pyLVHP.toggleHPBar( value )
			self.__pyLVHP.toggleLevel( value )  #同时绑定宠物等级显示/隐藏
		elif itemKey == "model":
			self.entity_.visibilitySettingChanged( infoKey, value )
			ECenter.fireEvent( "EVT_ON_PET_MODEL_INFO_CHANGED" )
		FloatName.onViewInfoChanged_( self, infoKey, itemKey, oldValue, value )

	def onHPChanged_( self, hp, hpMax ) :
		"""
		HP 改变时该方法被调用
		"""
		rate = hpMax > 0 and float( hp ) / hpMax or 0
		self.__pyLVHP.hpValue = rate
		
	def onAttachEntity_( self ):
		pet = self.entity_
		if pet == BigWorld.player().pcg_getActPet():
			self.viewInfoKey_ = "playerPet" 				# 角色自己宠物
		elif BigWorld.player().isTeamMember( pet.ownerID ):
			self.viewInfoKey_ = "teammatePet" 				# 队友宠物
		owner = pet.getOwner()
		relation = self.getRelation( owner )
		self.__setHPBarColor( relation )
		rate = self.entity_.HP_Max > 0 and float( self.entity_.HP ) / self.entity_.HP_Max or 0
		self.__pyLVHP.hpValue = rate
		self.__updateViewInfo()
	
	def getRelation( self, owner ):
		"""
		玩家与宠物的关系
		"""
		player = BigWorld.player()
		if not player.canPk( owner ) or \
		not player.currAreaCanPk():
			return csdefine.RELATION_FRIEND
		else:
			return csdefine.RELATION_ANTAGONIZE

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		if self.entity_ is None:return
		FloatName.onEnterWorld( self )
		self.__onLevelChanged( self.entity_, 0, self.entity_.level )
		self.__resetNameColor()
		owner = self.entity_.getOwner()
		if owner is None:return
		relation = self.getRelation( owner )
		self.__setHPBarColor( relation )
