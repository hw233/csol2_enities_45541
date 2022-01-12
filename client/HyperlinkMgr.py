# -*- coding: gb18030 -*-
#
# $Id: HyperlinkMgr.py,v 1.10 2008-08-19 09:24:56 zhangdengshan Exp $

"""
ר�����ڴ��������������ı��Ϲؼ��֣�NPC���֣� �������֣� ��Ʒ���֣� �������ֵȵȣ��Ķ��⹦�ܹ���
2008/03/08: zhangyuxing( ����Ϊ KeywordManager )
2008/03/24: huangyongwei( ����Ϊ HyperlinkMgr )
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
# ʵ�ְ��������ĳ�����
# --------------------------------------------------------------------
class HLSearch :
	def __init__( self ) :
		pass

	def __call__( self, pyRich, mark ) :
		ECenter.fireEvent( "EVT_ON_HELP_SEARCH", mark )
		
#---------------------------------------------------------------------
#�򿪴���
#----------------------------------------------------------------------
class HLLog :
	def __init__( self ):
		pass
	
	def __call__( self, pyRich, mark ) :
		mark = eval( mark )
		ECenter.fireEvent( mark[0],mark[1:] )


# --------------------------------------------------------------------
# ʵ�ֵ����� NPC �ĳ�����
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
		if topParent == rds.ruisMgr.talkingWindow:						#CSOL-1699 �����������ﳬ���������Զ���ȡ��������
			qstID = GUIFacade.getQuestID
			if qstID > 0 and not qstID in player.currentDoingQuestIDList:		#δ��ȡ��������
				self.__acceptQuest( qstID )
				self.__runToNpc()
				return
		if player.getSpaceLabel() in Const.SPACE_NOT_SHOW_NAVIGATE_SELECT:		# CSOL-1522 ĳЩ��ͼ������Ѱ·ѡ������ʾ 
			self.__runToNpc()
			return
		if self.__fetchFlyBees() :										# �����������·��
			menuStruct = (
						( ShareTexts.FLY_BEE, self.__flyToNpc ),
						( "SPLITTER", 1 ),
						( ShareTexts.AUTO_RUN, self.__runToNpc ),
					)
			ECenter.fireEvent( "EVT_ON_POPUP_GLOBAL_MENU", menuStruct, topParent ) # ����ѡ��˵�
		else :
			self.__runToNpc()						# �������û����·�䣬ֱ���Զ�Ѱ·

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __fetchFlyBees( self ) :
		"""
		��������Ƿ�����·��
		"""
		player = BigWorld.player()
		items = player.findItemsByIDFromNKCK( 50101003 )
		if len( items ) == 0 :
			items = player.findItemsByIDFromNKCK( 50101002 )
		return items

	def __runToNpc( self ) :
		"""
		�߹�ȥ
		"""
		if self.__mark is None : return
		mark = self.__mark
		self.__mark = None
		player = BigWorld.player()
		dstPos = dstSpace = None
		sreDstPos = re.search( "(?<=\[).+?(?=\])", mark )				# mark = ��[12,34,56]*1*fengming�������ÿ��ǡ�[12,34,56]*fengming������Ϊ��Щ�������ò��Ǹ���NPC ID������Ѱ·�ģ�
		if sreDstPos :													# ���ṩ�ı�ǩ�������Ŀ���ͼ
			if "*" not in mark : return									# ���û���ṩ���ڵ�ͼ���������Զ�Ѱ·
			dstPos = eval( sreDstPos.group() )							# ������Ŀ�ĵص������
			dstSpace = mark.split( "*" )[-1]							# Ŀ���ͼ�����ƽ���Ѱ·��
			if len( mark.split( "*" ) ) == 3:			# ˵��������ҵ�Ѱ·�����з��ߵ�
				dstLineNumber = int( mark.split( "*" )[-2] )						# Ŀ��������ڷ���
				lineNum = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
				if player.getSpaceLabel() == dstSpace:
					if dstLineNumber != lineNum:
						player.statusMessage( csstatus.ROLE_FLAY_TO_PLAYER, dstLineNumber )
						return
		else :															# ����Ĭ���ǰ���NPC ID������Ѱ·
			dstSpace = rds.npcDatasMgr.getNPCSpaceLabel( mark )[0]		# ����ID��ȡNPC���ڵĵ�ͼ
			dstPos = rds.npcDatasMgr.getNPCPosition( mark, dstSpace )	# ����ID�͵�ͼ��ȡNPC������
			player.setExpectTarget( mark )								# ����׷��Ŀ��NPC��ID
		if dstPos is None:
			ERROR_MSG( "Npc(%s) has no pos datas in NPCDatas!" % mark )
			return
		player.autoRun( dstPos, csconst.COMMUNICATE_DISTANCE - 2, dstSpace )

	def __flyToNpc( self ):
		"""
		�ɹ�ȥ
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
				player.stopMove()									# ������ֹͣ�ƶ����Ա�֤׷��Ŀ�겻�����
				sreDstPos = re.search( "(?<=\[).+?(?=\])", mark )
				if sreDstPos and len( mark.split( "*" ) ) >= 2:
					if "*" not in mark : return									# ���û���ṩ���ڵ�ͼ���������Զ�Ѱ·
					dstPos = eval( sreDstPos.group() )							# ������Ŀ�ĵص������
					dstSpace = mark.split( "*" )[-1]							# Ŀ���ͼ�����ƽ���Ѱ·��
					if len( mark.split( "*" ) ) == 3:
						spaceNumber = int( mark.split( "*" )[-2] )							# Ŀ���ͼ����
					else:
						spaceNumber = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
					player.cell.flyToPlayerPosition( dstSpace, spaceNumber, dstPos, bees[0].order )
				else :
					player.setExpectTarget( mark )					# ����׷��Ŀ��NPC��ID
					currSelQID = GUIFacade.getQuestLogSelection()		# ������Ӧ���ǲ���ȷ�ģ�������֮ǰһֱ����ʹ�ã����ⲻ�󣬴��и��ð취ʱ���޸ġ�ERROR_MARK
					player.cell.flyToNpc( mark, currSelQID, bees[0].order )
		
	def __acceptQuest( self, qstID ):
		"""
		��ȡ����
		"""
		qstWnd = rds.ruisMgr.talkingWindow
		GUIFacade.acceptQuest()
		qstWnd.currentWindow = 0
		qstWnd.hide()
		ECenter.fireEvent( "EVT_ON_ACCEPT_TRUE" )


# --------------------------------------------------------------------
# ʵ�ֵ����� NPC �ĳ�����
# --------------------------------------------------------------------
class HLTips :
	def __init__( self ):
		pass

	def __call__( self, pyRich, mark ) :
		INFO_MSG( "show tips of %s" % mark )
		showMessage( mark, "", MB_OK, None )

# --------------------------------------------------------------------
# ʵ��˲�Ƶ� NPC ��
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
		# �Ƿ�ʹ����·�䴫��?
		showMessage( 0x0081, "", MB_YES_NO, query )


# --------------------------------------------------------------------
# ͨ�������Ʒ������ʾ��Ʒ��Ϣ
# --------------------------------------------------------------------
class HChatItem :
	def __init__( self ) :
		self.__toolbox = None

	def __showDetails( self, pyRich, item ) :
		"""
		��ʾ��Ʒϸ��
		"""
		if self.__toolbox is None :
			from guis.Toolbox import toolbox
			self.__toolbox = toolbox
		dsp = item.description( BigWorld.player() )
		self.__toolbox.infoTip.showItemTips( pyRich, dsp )

	def __toChatMessage( self, item ) :
		"""
		���뵽�����������
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
# �ظ��Ƿ�ͬ���նԷ�Ϊͽ
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
		# �Ƿ�ͬ���նԷ�Ϊͽ?
		showMessage( 0x0082, "", MB_YES_NO, query )

# --------------------------------------------------------------------
# ����ַ
# --------------------------------------------------------------------
class HLOpenURL :
	def __init__( self ):
		pass

	def __call__( self, pyRich, mark ) :
		csol.openUrl( mark )


# --------------------------------------------------------------------
# С�����������
# --------------------------------------------------------------------
class HPixieHelp :

	def __call__( self, pyRich, mark ) :
		pixieHelper.triggerSection( int( mark ) )


# --------------------------------------------------------------------
# ʵ�ֳ����ӵĹ�����
# --------------------------------------------------------------------
class HyperlinkMgr :
	__inst			= None

	def __init__( self ) :
		assert HyperlinkMgr.__inst is None
		self.__hyperLinks = {
			"teach" : HLTeach(),

			# ��ַ
			"url:" : HLOpenURL(),

			# ϵͳ����
			"srch:" : HLSearch(),
			"goto:" : HLGoto(),
			"tips:" : HLTips(),
			"trsp:" : HLTrsp(),
			"log:"   : HLLog(),

			# �������
			ChatFacade.ChatItem.LMARK : HChatItem(),

			# ������Ի�
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
		���ݲ�ͬ�ĳ��������ͣ�����ϸ�ִ���
		@type			pyRich	 : CSRichText
		@param			pyRich	 : ��ʾ�����ӵĶ����ı��ؼ�
		@type			linkMark : str
		@param			linkMark : �����ӱ��
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
