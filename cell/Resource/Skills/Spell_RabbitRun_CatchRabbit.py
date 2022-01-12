# -*- coding: gb18030 -*-
#
#
#

from SpellBase import *
from Spell_Rabbit_Run import Spell_Rabbit_Run
import csstatus
import BigWorld
import csdefine
import csconst
import Love3
from ObjectScripts.GameObjectFactory import g_objFactory
import items
g_items = items.instance()

class Spell_RabbitRun_CatchRabbit( Spell_Rabbit_Run ):
	"""
	抓住兔子
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Rabbit_Run.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Rabbit_Run.init( self, dict )
		self.radishID = int( dict[ "param3" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if caster.isReal():
			self.getBuffLink(0).getBuff().receive( None, caster )
			caster.client.initSpaceSkills( g_objFactory.getObject("fu_ben_rabbit_run").rabbitSkillIDs, csdefine.SPACE_TYPE_RABBIT_RUN )
		if receiver.isReal() :
			self.getBuffLink(1).getBuff().receive( None, receiver )
			receiver.client.initSpaceSkills( g_objFactory.getObject("fu_ben_rabbit_run").wolfSkillIDs, csdefine.SPACE_TYPE_RABBIT_RUN )
			item = receiver.findItemFromNKCK_( self.radishID )
			if item:
				receiver.removeItem_( item.order, 1, csdefine.DELETE_ITEM_RABBIT_RUN )
				i = g_items.createDynamicItem( self.radishID , 1 )
				caster.addItem( i, csdefine.ADD_ITEM_RABBIT_RUN )
			else:
				caster.statusMessage( csstatus.RABBIT_RUN_NOT_HAVE_RADISH )
		else :
			receiver.receiveOnReal( -1, self )


	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if target.getObject().findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is None:
			return csstatus.RABBIT_RUN_NOT_RABBIT
		if not target.getObject().actionSign( csdefine.ACTION_FORBID_MOVE ):
			return csstatus.RABBIT_RUN_NOT_CANT_MOVE

		return Spell_Rabbit_Run.useableCheck( self, caster, target)
