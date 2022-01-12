# -*- coding: gb18030 -*-
#
# $Id: EntityResume.py,v 1.7 2008-09-01 03:39:38 zhangyuxing Exp $



import event.EventCenter as ECenter
from guis.tooluis.CSRichText import CSRichText
from guis import *
import GUI
from guis.ExtraEvents import LastMouseEvent
import csconst
import csdefine
import PetResume
import RoleResume
import VehicleResume
import NpcResume
import MonsterResume
import DartResume
import QuestBoxResume
import SpaceDoorResume
import CollectPointResume
import DanceSeat
import TongNagualResume
import EidolonResume
import SpaceDoorChallengeResume
import CityWarBaseResume
from gbref import rds
import TextFormatMgr
from EntityTip import EntityTip
from bwdebug import *
from LabelGather import labelGather

from EntityDecoratorMgr import EntityDecoratorMgr
import FruitTreeResume

g_entDecConfig = EntityDecoratorMgr.instance()

g_entityResume =	{
						csdefine.ENTITY_TYPE_PET : PetResume.instance,
						csdefine.ENTITY_TYPE_ROLE : RoleResume.instance,
						csdefine.ENTITY_TYPE_NPC : NpcResume.instance,
						csdefine.ENTITY_TYPE_MONSTER : MonsterResume.instance,
						csdefine.ENTITY_TYPE_QUEST_BOX : QuestBoxResume.instance,
						csdefine.ENTITY_TYPE_SLAVE_MONSTER : MonsterResume.instance,
						csdefine.ENTITY_TYPE_TREASURE_MONSTER : MonsterResume.instance,
						csdefine.ENTITY_TYPE_VEHICLE : VehicleResume.instance,
						csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER : MonsterResume.instance,
						csdefine.ENTITY_TYPE_CONVOY_MONSTER : MonsterResume.instance,
						csdefine.ENTITY_TYPE_SPACE_DOOR : SpaceDoorResume.instance,
						csdefine.ENTITY_TYPE_VEHICLE_DART : DartResume.instance,
						csdefine.ENTITY_TYPE_YAYU : MonsterResume.instance,
						csdefine.ENTITY_TYPE_COLLECT_POINT : CollectPointResume.instance,
						csdefine.ENTITY_TYPE_TONG_NAGUAL : TongNagualResume.instance,
						csdefine.ENTITY_TYPE_FRUITTREE : FruitTreeResume.instance,
						csdefine.ENTITY_TYPE_EIDOLON_NPC : EidolonResume.instance,
						csdefine.ENTITY_TYPE_CALL_MONSTER : MonsterResume.instance,
						csdefine.ENTITY_TYPE_SPACE_CHALLENGE_DOOR :SpaceDoorChallengeResume.instance,
						csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM:MonsterResume.instance,
						csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER:MonsterResume.instance,
						csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR:MonsterResume.instance,
						csdefine.ENTITY_TYPE_XIAN_FENG:MonsterResume.instance,
						csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER:MonsterResume.instance,
						csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BATTLE_FLAG : QuestBoxResume.instance,
						csdefine.ENTITY_TYPE_DANCESEAT:DanceSeat.instance,
						csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE:CityWarBaseResume.instance,
						csdefine.ENTITY_TYPE_CAMP_FENG_HUO_TOWER:MonsterResume.instance,
						csdefine.ENTITY_TYPE_CAMP_FENG_HUO_ALTAR:MonsterResume.instance,
						csdefine.ENTITY_TYPE_CAMP_XIAN_FENG:MonsterResume.instance,
						csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BASE_TOWER:MonsterResume.instance,
						csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BATTLE_FLAG : QuestBoxResume.instance,
						csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER : MonsterResume.instance,

				 	}


class EntityResume :
	def __init__( self ) :
		self.initialize()


	def initialize( self ) :
		self.__pyTipWnd = EntityTip()										# 从 TipWindow 修改为 EntityTip，并从 self.wnd 改为 self.__pyTipWnd( 2008.08.19 by hyw )
		self.showState = g_entDecConfig.getEntityResumeShowState()
		self.triggers_ = {}
		self.registerTriggers_()

	def dispose( self ) :
		self.deregisterTriggers()
		self.__pyTipWnd.dispose( self )

	def doMsg_( self, entity ):
		global g_entityResume
		entityType = entity.getEntityType()
		if g_entityResume.has_key( entityType ):
			if entity.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ):
				entityType = csdefine.ENTITY_TYPE_NPC
			msg = g_entityResume[entityType].doMsg_( entity, self.__pyTipWnd )
			return TextFormatMgr.DescriptionText( entity, msg ).makeDescription()
		return labelGather.getText( "EntityResume:entity", "typeNotDefine" )

	# -------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_SHOW_RESUME"] = self.onShowResume
		self.triggers_["EVT_ON_HIDE_RESUME"] = self.onHideResume
		self.triggers_["EVT_ON_ENTITY_RESUME_SET"] = self.onShowStateSet

		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def deregisterTriggers( self ) :
		for key in self.triggers_ :
			ECenter.unregisterEvent( key, self )


	def onShowResume( self, entity ):
		if not self.showState:
			return
		if hasattr( entity, "effect_state" ) and ( entity.effect_state & csdefine.EFFECT_STATE_PROWL ):	# 15:40 2008-12-2,如果entity处于潜行效果状态,不显示
			return
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and entity.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			return
		self.__pyTipWnd.r_pos = GUI.mcursor().position + (0.05, -0.05)
		LastMouseEvent.attach( self.bindMonse )
		self.__pyTipWnd.show( self.doMsg_( entity ) )


	def onHideResume( self ):
		LastMouseEvent.detach( self.bindMonse )
		self.__pyTipWnd.hide()


	def onShowStateSet( self, state ):
		self.showState = state

	def bindMonse( self, dx, dy, dz ):
		pos = GUI.mcursor().position + (0.05, -0.05)
		if pos[0] > 0.75:
			pos = ( 0.75, pos[1] )
		if pos[1] < -0.75:
			pos = ( pos[0], -0.75 )
		self.__pyTipWnd.r_pos = pos



	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------

	def onEvent( self, macroName, *args ) :
		self.triggers_[macroName]( *args )

