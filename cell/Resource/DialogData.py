# -*- coding: gb18030 -*-
#
# $Id: DialogData.py,v 1.13 2008-08-11 01:02:04 kebiao Exp $

"""
"""

from bwdebug import *
from DialogMsg import DialogMsg
from Resource.FuncsModule.Functions import Functions

class DialogData:
	"""
	对话抽像层
	"""
	def __init__( self, section = None ):
		"""
		"""
		self._functions = []
		self._actions = []
		self._dlgMsg = None	# dict type
		self._dlgDepands = {}	# key is menuKey, value is instance of class DialogData
		self._isAlwayOpen = False
		if section:
			self.init( section )

	def init( self, section ):
		"""
		@param section: xml data section
		@type  section: pyDataSection
		"""
		# init dialog message
		self.initDialogMsg( section )
		if section.has_key( "alwayOpen" ):
			self._isAlwayOpen = True

		# init functions
		if section.has_key( "functions" ):
			funcs = Functions( section["functions"] )
			self._functions.append( funcs )		# 事实上，当前的配置只有一个Functions了

	def initDialogMsg( self, section ):
		"""
		@param section: xml data section
		@type  section: pyDataSection
		"""
		dlg = DialogMsg()
		self._dlgMsg = dlg
		dlg.setMsg( section.readString( "msg" ) )
		if section.has_key( "keys" ):
			for m in section["keys"].values():
				key = m.readString( "key" )
				title = m.readString( "title" )
				type = m.readInt( "type" )
				dlg.addMenu( key, title, type )
		return	# the end

	def doTalk( self, player, talkEntity = None ):
		"""
		执行对话动作

		@param player: 玩家
		@type  player: Entity
		@param talkEntity: 对话的原始目标Entity
		@type  talkEntity: Entity
		@return: None
		"""
		if not self.doFunction( player, talkEntity ):
			player.endGossip( talkEntity )
			return	# 如果执行功能失败则不进行对话

		if self._dlgMsg is None:
			return	# 没有对话,直接返回

		# send dialog
		player.setGossipText( self._dlgMsg.getMsg() )
		for m in self._dlgMsg.getMenus():
			if self._dlgDepands[m[0]].canTalk( player, talkEntity ):
				player.addGossipOption( *m )

		# 这句不应该放这里,当前方法只负责对话,但是否完成由外面决定
		#target.sendGossipComplete( player )


	def doFunction( self, player, talkEntity = None ):
		"""
		执行功能

		@return: 如果有actions且所有的action都执行失败则返回False,否则返回True
		@return: BOOL
		"""
		if len( self._functions ) == 0:
			if talkEntity != None:
				player.endGossip( talkEntity )
			return True

		# do all functions
		for funcs in self._functions:
			ret = funcs.valid( player, talkEntity )
			if ret == None:
				funcs.do( player, talkEntity )
				return True
			else:
				if ret != -1:
					ret.doTalk( player, talkEntity )
		return False

	def canTalk( self, player, talkEntity = None ):
		"""
		检查对话动作是否允许

		@param player: 玩家
		@type  player: Entity
		@param talkEntity: 一个扩展的参数
		@type  talkEntity: entity
		@return: None
		"""
		if len( self._functions ) == 0 or self._isAlwayOpen: return True	# no function
		for funcs in self._functions:
			if funcs.valid( player, talkEntity ) is None:
				return True
		return False

	def buildDepend( self, manager ):
		"""
		@param manager: 类的管理者
		@type  manager: DialogManager
		"""
		# buildDepend all functions
		for funcs in self._functions:
			funcs.buildDepend( manager )

		if self._dlgMsg is None:
			return
		menus = self._dlgMsg.getMenuKeys()
		for m in menus:
			dlgData = manager.getDialog( m )
			if dlgData is None:
				continue
			self._dlgDepands[m] = dlgData



#
# $Log: not supported by cvs2svn $
# Revision 1.12  2008/08/05 06:30:59  zhangyuxing
# 调整没有对白不发送对话信息判断
#
# Revision 1.11  2008/02/26 02:02:24  zhangyuxing
# 关于对话选项多一个图标标识的相关修改（主要是配置文件多一个 type,)
# 这里需要读出
#
# Revision 1.10  2008/01/15 06:06:21  phw
# 调整了初始化方式
#
# Revision 1.9  2007/12/04 04:39:54  fangpengjun
# 将npc普通对话接口转到玩家
#
# Revision 1.8  2007/05/22 08:18:31  phw
# method modified: canTalk(), 修正有函数功能的对话不能正确表现的bug
#
# Revision 1.7  2007/05/18 08:40:20  kebiao
# 加入isAlwayOpen属性决定一个功能不管是否失败都显示对话和菜单
# 修改所有param 为targetEntity
# 加入某个功能失败 则调用失败功能
#
# Revision 1.6  2006/12/23 07:28:14  kebiao
# 添加了对话key中如 "quit：结束对话"这样没有制定一个功能函数处理的时候默认为关闭对话框param.endGossip( player )
#
# Revision 1.5  2006/03/23 09:24:53  phw
# *** empty log message ***
#
# Revision 1.4  2006/02/28 08:03:03  phw
# no message
#
# Revision 1.3  2005/12/08 01:07:20  phw
# no message
#
#
