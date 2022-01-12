# -*- coding: gb18030 -*-
#
# $Id: HyperlinkMgr.py,v 1.10 2008-08-19 09:24:56 zhangdengshan Exp $

"""
专门用于处理界面各个窗口文本上关键字（NPC名字， 怪物名字， 物品名字， 任务名字等等）的额外功能管理
2008/03/08: zhangyuxing( 命名为 KeywordManager )
2008/03/24: huangyongwei( 命名为 HyperlinkMgr )
"""

import re
import GUIFacade
import ShareTexts
import cPickle
import csol
import Language
import BigWorld
import Const
import csdefine
import csconst
import csstatus
import keys
import ChatFacade
import ItemTypeEnum
from bwdebug import *
from gbref import rds
from MessageBox import showMessage
from MessageBox import MB_OK
from ChatFacade import chatFacade, chatObjTypes
from items.ItemDataList import ItemDataList
from event import EventCenter as ECenter
from Helper import pixieHelper

# --------------------------------------------------------------------
# 实现帮助搜索的超链接
# --------------------------------------------------------------------
class HLSearch :
	def __init__( self ) :
		pass

	def __call__( self, pyRich, mark ) :
		ECenter.fireEvent( "EVT_ON_HELP_SEARCH", mark )
		
#---------------------------------------------------------------------
#打开窗口
#----------------------------------------------------------------------
class HLLog :
	def __init__( self ):
		pass
	
	def __call__( self, pyRich, mark ) :
		mark = eval( mark )
		ECenter.fireEvent( mark[0],mark[1:] )


# --------------------------------------------------------------------
# 实现导航到 NPC 的超链接
# --------------------------------------------------------------------
class HLGoto :
	def __init__( self ):
		self.__mark = None

	def __call__( self, pyRich, mark ) :
		"""
		"""
		self.__mark = mark
		player = BigWorld.player()
		topParent = pyRich.pyTopParent
		if topParent == rds.ruisMgr.talkingWindow:						#CSOL-1699 接任务界面怪物超链接新增自动接取该任务功能
			qstID = GUIFacade.getQuestID
			if qstID > 0 and not qstID in player.currentDoingQuestIDList:		#未接取过该任务
				self.__acceptQuest( qstID )
				self.__runToNpc()
				return
		if player.getSpaceLabel() in Const.SPACE_NOT_SHOW_NAVIGATE_SELECT:		# CSOL-1522 某些地图中屏蔽寻路选择框的显示 
			self.__runToNpc()
			return
		if self.__fetchFlyBees() :										# 如果身上有引路蜂
			menuStruct = (
						( ShareTexts.FLY_BEE, self.__flyToNpc ),
						( "SPLITTER", 1 ),
						( ShareTexts.AUTO_RUN, self.__runToNpc ),
					)
			ECenter.fireEvent( "EVT_ON_POPUP_GLOBAL_MENU", menuStruct, topParent ) # 弹出选择菜单
		else :
			self.__runToNpc()						# 如果身上没有引路蜂，直接自动寻路

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __fetchFlyBees( self ) :
		"""
		检查身上是否有引路蜂
		"""
		player = BigWorld.player()
		items = player.findItemsByIDFromNKCK( 50101003 )
		if len( items ) == 0 :
			items = player.findItemsByIDFromNKCK( 50101002 )
		return items

	def __runToNpc( self ) :
		"""
		走过去
		"""
		if self.__mark is None : return
		mark = self.__mark
		self.__mark = None
		player = BigWorld.player()
		dstPos = dstSpace = None
		sreDstPos = re.search( "(?<=\[).+?(?=\])", mark )				# mark = ‘[12,34,56]*1*fengming’，还得考虑‘[12,34,56]*fengming’，因为有些特殊配置不是根据NPC ID来进行寻路的；
		if sreDstPos :													# 若提供的标签是坐标和目标地图
			if "*" not in mark : return									# 如果没有提供所在地图，则不允许自动寻路
			dstPos = eval( sreDstPos.group() )							# 否则按照目的地的坐标和
			dstSpace = mark.split( "*" )[-1]							# 目标地图的名称进行寻路，
			if len( mark.split( "*" ) ) == 3:			# 说明这是玩家的寻路，是有分线的
				dstLineNumber = int( mark.split( "*" )[-2] )						# 目标玩家所在分线
				lineNum = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
				if player.getSpaceLabel() == dstSpace:
					if dstLineNumber != lineNum:
						player.statusMessage( csstatus.ROLE_FLAY_TO_PLAYER, dstLineNumber )
						return
		else :															# 否则默认是按照NPC ID来进行寻路
			dstSpace = rds.npcDatasMgr.getNPCSpaceLabel( mark )[0]		# 根据ID获取NPC所在的地图
			dstPos = rds.npcDatasMgr.getNPCPosition( mark, dstSpace )	# 根据ID和地图获取NPC的坐标
			player.setExpectTarget( mark )								# 设置追踪目标NPC的ID
		if dstPos is None:
			ERROR_MSG( "Npc(%s) has no pos datas in NPCDatas!" % mark )
			return
		player.autoRun( dstPos, csconst.COMMUNICATE_DISTANCE - 2, dstSpace )

	def __flyToNpc( self ):
		"""
		飞过去
		"""
		if self.__mark is None : return
		mark = self.__mark
		self.__mark = None
		player = BigWorld.player()
		if player.getState() == csdefine.ENTITY_STATE_FIGHT :
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )
		else :
			bees = self.__fetchFlyBees()
			if len( bees ) == 0 :
				player.statusMessage( csstatus.ROLE_HAS_NOT_FIY_ITEM )
			else :
				player.stopMove()									# 必须先停止移动，以保证追踪目标不被清空
				sreDstPos = re.search( "(?<=\[).+?(?=\])", mark )
				if sreDstPos and len( mark.split( "*" ) ) >= 2:
					if "*" not in mark : return									# 如果没有提供所在地图，则不允许自动寻路
					dstPos = eval( sreDstPos.group() )							# 否则按照目的地的坐标和
					dstSpace = mark.split( "*" )[-1]							# 目标地图的名称进行寻路，
					if len( mark.split( "*" ) ) == 3:
						spaceNumber = int( mark.split( "*" )[-2] )							# 目标地图分线
					else:
						spaceNumber = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
					player.cell.flyToPlayerPosition( dstSpace, spaceNumber, dstPos, bees[0].order )
				else :
					player.setExpectTarget( mark )					# 设置追踪目标NPC的ID
					currSelQID = GUIFacade.getQuestLogSelection()		# 这样做应该是不正确的，但由于之前一直这样使用，问题不大，待有更好办法时再修改。ERROR_MARK
					player.cell.flyToNpc( mark, currSelQID, bees[0].order )
		
	def __acceptQuest( self, qstID ):
		"""
		接取任务
		"""
		qstWnd = rds.ruisMgr.talkingWindow
		GUIFacade.acceptQuest()
		qstWnd.currentWindow = 0
		qstWnd.hide()
		ECenter.fireEvent( "EVT_ON_ACCEPT_TRUE" )


# --------------------------------------------------------------------
# 实现导航到 NPC 的超链接
# --------------------------------------------------------------------
class HLTips :
	def __init__( self ):
		pass

	def __call__( self, pyRich, mark ) :
		INFO_MSG( "show tips of %s" % mark )
		showMessage( mark, "", MB_OK, None )

# --------------------------------------------------------------------
# 实现瞬移到 NPC 处
# --------------------------------------------------------------------
class HLTrsp :
	def __init__( self ):
		pass

	def __call__( self, pyRich, mark ) :
		def query( rs_id ):
			if rs_id == RS_YES:
				flyToNpc()

		def flyToNpc():
			player = BigWorld.player()
			items = []
			items = player.findItemsByIDFromNKCK( 50101002 )
			if items == []:
				items = player.findItemsByIDFromNKCK( 50101003 )
			if items == []:
				player.statusMessage( csstatus.ROLE_HAS_NOT_FIY_ITEM )
				return
			if not player.getState() == csdefine.ENTITY_STATE_FIGHT:
				player.cell.flyToNpc( mark, items[0].order )
			else:
				player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )
		# 是否使用引路蜂传送?
		showMessage( 0x0081, "", MB_YES_NO, query )


# --------------------------------------------------------------------
# 通过点击物品名称显示物品信息
# --------------------------------------------------------------------
class HChatItem :
	def __init__( self ) :
		self.__toolbox = None

	def __showDetails( self, pyRich, item ) :
		"""
		显示物品细节
		"""
		if self.__toolbox is None :
			from guis.Toolbox import toolbox
			self.__toolbox = toolbox
		dsp = item.description( BigWorld.player() )
		self.__toolbox.infoTip.showItemTips( pyRich, dsp )

	def __toChatMessage( self, item ) :
		"""
		输入到聊天输入框中
		"""
		chatFacade.insertChatObj( chatObjTypes.ITEM, item )

	def __call__( self, pyRich, mark ) :
		mark = mark.replace( "\}", "}" )
		id, extra = eval( mark )
		item = ItemDataList.instance().createDynamicItem( id )
		if item is None :
			ERROR_MSG( "item '%i' is not exist!" % id )
			return
		item.extra = extra
		if BigWorld.isKeyDown( keys.KEY_LCONTROL ) or \
			BigWorld.isKeyDown( keys.KEY_RCONTROL ) :
				self.__toChatMessage( item )
		else :
			self.__showDetails( pyRich, item )


# --------------------------------------------------------------------
# 回复是否同意收对方为徒
# --------------------------------------------------------------------
class HLTeach:
	def __init__( self ):
		pass

	def __call__( self, pyRich, prenticeName ):
		def query( rs_id ):
			if rs_id == RS_YES:
				BigWorld.player().teach_remoteTeachReply( True, prenticeName )
			elif rs_id == RS_NO:
				BigWorld.player().teach_remoteTeachReply( False, prenticeName )
		# 是否同意收对方为徒?
		showMessage( 0x0082, "", MB_YES_NO, query )

# --------------------------------------------------------------------
# 打开网址
# --------------------------------------------------------------------
class HLOpenURL :
	def __init__( self ):
		pass

	def __call__( self, pyRich, mark ) :
		csol.openUrl( mark )


# --------------------------------------------------------------------
# 小精灵帮助链接
# --------------------------------------------------------------------
class HPixieHelp :

	def __call__( self, pyRich, mark ) :
		pixieHelper.triggerSection( int( mark ) )


# --------------------------------------------------------------------
# 实现超链接的管理器
# --------------------------------------------------------------------
class HyperlinkMgr :
	__inst			= None

	def __init__( self ) :
		assert HyperlinkMgr.__inst is None
		self.__hyperLinks = {
			"teach" : HLTeach(),

			# 网址
			"url:" : HLOpenURL(),

			# 系统帮助
			"srch:" : HLSearch(),
			"goto:" : HLGoto(),
			"tips:" : HLTips(),
			"trsp:" : HLTrsp(),
			"log:"   : HLLog(),

			# 聊天对象
			ChatFacade.ChatItem.LMARK : HChatItem(),

			# 随身精灵对话
			"pixieHelp:" : HPixieHelp(),
			}

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = HyperlinkMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def process( self, pyRich, linkMark ):
		"""
		根据不同的超链接类型，进行细分处理
		@type			pyRich	 : CSRichText
		@param			pyRich	 : 显示超链接的多行文本控件
		@type			linkMark : str
		@param			linkMark : 超链接标记
		@return					 : None
		"""
		prefix = ""
		for pf in self.__hyperLinks :
			if linkMark.startswith( pf ) :
				prefix = pf
				break
		if prefix == "" :
			ERROR_MSG( "the hyperlink prefix '%s' is not exist!" % prefix )
			return
		preCount = len( prefix )
		self.__hyperLinks[prefix]( pyRich, linkMark[preCount:] )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
hyperlinkMgr = HyperlinkMgr.instance()
