# -*- coding:gb18030 -*-


from Spell_Item import Spell_Item
import csdefine
import Love3
import ItemTypeEnum
import cschannel_msgs
from bwdebug import *
import csstatus

class Spell_322398010( Spell_Item ):
	"""
	使用物品，奖励随机物品
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.isBinded = 0		# 奖励的物品是否绑定
		self.rewardIndex = 0	# 奖励编号

	def init( self, dictData ):
		"""
		"""
		Spell_Item.init( self, dictData )
		self.isBinded = bool( dictData["param1"] if len( dictData["param1"] ) > 0 else 0 )
		self.rewardIndex = int( dictData["param2"] if len( dictData["param2"] ) > 0 else 0 )

	def receive( self, caster, receiver ):
		"""
		"""
		awarder = Love3.g_rewards.fetch( self.rewardIndex, receiver )
		for item in awarder.items:
			if self.isBinded:
				item.setBindType( ItemTypeEnum.CBT_PICKUP )
			if not receiver.addItemAndNotify_( item, csdefine.ADD_ITEM_TANABATA_QUIZ ):
				receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_MAIL_NOTIFY )
				receiver.mail_send_on_air_withItems( receiver.getName(), csdefine.MAIL_TYPE_QUICK, cschannel_msgs.TANABATA_TREE_PLANTING_MAIL_TITLE, "", [item] )
