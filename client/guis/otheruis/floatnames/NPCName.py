# -*- coding: gb18030 -*-
#
# $Id: NPCName.py,v 1.14 2008-05-29 05:44:12 huangyongwei Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

import csdefine
import Const
import event.EventCenter as ECenter
import ResMgr
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from FloatName import FloatName
from QuestMarks import QuestMarks
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from NPCQuestSignMgr import npcQSignMgr
from NPCDatasMgr import npcDatasMgr
from DoubleName import DoubleName


class NPCName( FloatName ) :
	__cg_wnd = None
	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/npcname.gui" )

	def __init__( self ) :
		if NPCName.__cg_wnd is None :
			NPCName.__cg_wnd = GUI.load( NPCName.__cc_dummySection )
		wnd = util.copyGuiTree( NPCName.__cg_wnd )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.viewInfoKey_ = "npc"
		self.__initialize( wnd )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleDoubleName( False )
		
		self.__pyQstMarks = QuestMarks( wnd.qstMarks )
		self.__pyNPCSign = PyGUI( wnd.npcSign )
		self.__pyOwnerName = StaticText( wnd.ownerName )
		self.__pyOwnerName.setFloatNameFont()
		self.__pyOwnerName.visible = False
		self.pyElements_ = [self.pyLbName_, self.__pyOwnerName, self.__pyNPCSign, self.__pyQstMarks]
		self.registerTriggers_()

	def __onQuestStateChanged( self, npc, id ) :
		if self.entity_ == None or self.entity_ != npc : return
		self.__pyQstMarks.flush()
		signStr = npcQSignMgr.getSignBySignID( id )
		self.__pyQstMarks.showMark( signStr )
		self.layout_()
		npc.stopPreCompleteEffect()	
		if signStr in [ "normalFinish", "directFinish" ]:
			npc.playPreCompleteEffect()
	
	def __onFightStateChange( self, npc ):
		"""
		战斗状态改变,任务标识隐藏
		"""
		if self.entity_ == None or self.entity_.id != npc.id : return
		self.__pyQstMarks.flush()


	def __onNPCOwnerFamilyNameChanged( self, npcID, ownerName ):
		if self.entity_ == None or npcID != self.entity_.id:return
		self.__pyOwnerName.visible = False
		self.__pyOwnerName.text = ownerName
		self.layout_()

	def __onFlagsChanged( self, npc ) :
		if self.entity_ == None or self.entity_ != npc : return
		self.__updateNPCSign()

	def __updateNPCSign( self ) :
		"""
		设置NPC头顶的标记
		"""
		if self.entity_ == None:return
		npc = self.entity_
		title = npc.getTitle()
		if npc.hasFlag( csdefine.ENTITY_FLAG_COPY_STARTING ) :
			self.__pyNPCSign.texture = "maps/entity_signs/fighting.texanim"
			self.__pyNPCSign.visible = True
		else :
			self.__pyNPCSign.texture = npcDatasMgr.getNPCSignFile( npc.className )
			if self.__pyNPCSign.texture == "" :
				self.__pyNPCSign.visible = False

		# 任务目标未完成显示entity名称规则
		player = BigWorld.player()
		taskIndexMonsters = player.getTaskIndexMonsters()
		if hasattr( npc, "className" ) and npc.className in taskIndexMonsters:
			self.visible = True
			self.pyLbName_.toggleRightName( title != "" )
			self.pyLbName_.toggleLeftName( True )

		if npc.hasFlag( csdefine.ENTITY_FLAG_HEAD_ALWAYS_SHOW ) :
			self.visible = True
			self.pyLbName_.toggleRightName( title != "" )
			self.pyLbName_.toggleLeftName( True )
		elif npc.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_NAME ):
			self.visible = False
			self.pyLbName_.toggleLeftName( False )
			self.pyLbName_.toggleRightName( False )
		elif npc.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_QUEST ):
			self.__pyQstMarks.visible = False
		else:
			self.pyLbName_.toggleLeftName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" ) )
			if title != "":
				self.pyLbName_.toggleRightName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "title" ) )
		self.layout_()
	
	def __setHeadColor( self ):
		"""
		设置NPC头顶颜色
		"""
		if self.entity_ == None:return
		npc = self.entity_
		nameColor = npc.nameColor
		camp = BigWorld.player().getCamp()
		color = "c1"
		if nameColor == 0:
			color = "c48"
		elif nameColor == 3 or nameColor == 4:
			color = "c47"
		else:
			color = camp == nameColor and "c47" or "c4"
		self.pyLbName_.color = cscolors[color]
	
	def __onNPCNameColorChanged( self, npc ):
		"""
		nameColor值改变
		"""
		if self.entity_ == None or self.entity_.id != npc.id:return
		self.__setHeadColor()

	def __onPlayerQuestStateChanged( self, questID, taskIndex ):
		"""
		quest state change
		"""
		if self.entity_ is None: return
		self.__updateNPCSign()

	def __onPlayerAddQuest( self, questID ):
		"""
		add quest
		"""
		if self.entity_ is None: return
		self.__updateNPCSign()

	def __onPlayerRemoveQuest( self, questID ):
		"""
		remove quest
		"""
		if self.entity_ is None: return
		self.__updateNPCSign()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onViewInfoChanged_( self, infoKey, itemKey, oldValue, value ) :
		if self.viewInfoKey_ != infoKey or self.entity_ == None: return
		FloatName.onViewInfoChanged_( self, infoKey, itemKey, oldValue, value )

		# 任务目标未完成显示entity名称规则
		player = BigWorld.player()
		taskIndexMonsters = player.getTaskIndexMonsters()
		if hasattr( self.entity_, "className" ) and self.entity_.className in taskIndexMonsters:
			self.visible = True
			self.pyLbName_.toggleRightName( self.entity_.getTitle() != "" )
			self.pyLbName_.toggleLeftName( True )

		if self.entity_.hasFlag( csdefine.ENTITY_FLAG_HEAD_ALWAYS_SHOW ) :
			self.visible = True
			self.pyLbName_.toggleRightName( self.entity_.getTitle() != "" )
			self.pyLbName_.toggleLeftName( True )

		if hasattr( self.entity_,"uiAttachsShow" ) and not self.entity_.uiAttachsShow:
			self.visible = False
		self.layout_()

	def onAttachEntity_( self ):
		ppos = BigWorld.player().position
		npos = self.entity_.position
		self.visible = ppos.distTo( npos ) < Const.SHOW_NPCNAME_RANGE				# 超出指定范围，不显示 NPC 头顶名称
		own_familyName = self.entity_.own_familyName
		self.__onNPCNameColorChanged( self.entity_ )
		if own_familyName:
			self.__pyOwnerName.text = own_familyName
		else:
			self.__pyOwnerName.visible = False
		
	def onDetachEntity_( self ):
		self.pyLbName_.toggleDoubleName( False )
		self.__pyOwnerName.visible = False
		self.__pyOwnerName.text = ""
		self.__pyNPCSign.visible = False
		self.__pyQstMarks.flush()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_NPC_FLAGS_CHANGED"] = self.__onFlagsChanged
		self.triggers_["EVT_ON_NPC_QUEST_STATE_CHANGED"] = self.__onQuestStateChanged
		self.triggers_["EVT_ON_NPC_FAMILY_NAME_CHANGE"] = self.__onNPCOwnerFamilyNameChanged
		self.triggers_["EVT_ON_NPC_NAMECOLOR_CHANGED"] = self.__onNPCNameColorChanged
		self.triggers_["EVT_ON_MONSTER_FIGHT_STATE_CHANGE"] = self.__onFightStateChange
		self.triggers_["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__onPlayerQuestStateChanged
		self.triggers_["EVT_ON_QUEST_LOG_ADD"] = self.__onPlayerAddQuest
		self.triggers_["EVT_ON_QUEST_LOG_REMOVED"]	= self.__onPlayerRemoveQuest
		FloatName.registerTriggers_( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def dispose( self ) :
		self.__pyQstMarks.dispose()
		self.__pyNPCSign.dispose()
		FloatName.dispose( self )

	def onEnterWorld( self ):
		FloatName.onEnterWorld( self )
		self.__updateNPCSign()
