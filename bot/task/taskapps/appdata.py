# -*- coding: gb18030 -*-
"""
--------------------------------------------------
机器人测试任务配置帮助文档
--------------------------------------------------
见：alienbrain://NEWAB/创世Online/测试数据/机器人测试/机器人测试任务配置帮助文档.txt
"""


# 机器人测试任务数据，目前在代码中手动编写，将来可以考虑
# 做成配置，从配置读取
DATA = {}


# --------------------------------------
# template to test bot enter plane wm1 of xin_ban_xin_shou_cun .
#
# key: wm1_xin_ban_xin_shou_cun
# --------------------------------------
DATA["wm1_xin_ban_xin_shou_cun"] = (
	"tp_wait_move", {
		"Teleport": ("xin_ban_xin_shou_cun", (-185, 28.6, -128)),
		"Wait": (5,),
		"Move": ((-165.6, 26.0, -109.4),),
	},
)


# --------------------------------------
# template to test bot enter plane wm2 of xin_ban_xin_shou_cun .
#
# key: wm2_xin_ban_xin_shou_cun
# --------------------------------------
DATA["wm2_xin_ban_xin_shou_cun"] = (
	"tp_wait_move", {
		"Teleport": ("xin_ban_xin_shou_cun", (-173, 19.6, 50.4)),
		"Wait": (5,),
		"Move": ((-197, 24.5, 61),),
	},
)


# --------------------------------------
# template to test bot enter plane wm3 of xin_ban_xin_shou_cun .
#
# key: wm3_xin_ban_xin_shou_cun
# --------------------------------------
DATA["wm3_xin_ban_xin_shou_cun"] = (
	"tp_wait_move", {
		"Teleport": ("xin_ban_xin_shou_cun", (2, 19.2, 156)),
		"Wait": (5,),
		"Move": ((3.6, 20, 139.1),),
	},
)


# --------------------------------------
# template to test bot enter plane wm4 of xin_ban_xin_shou_cun .
#
# key: wm4_xin_ban_xin_shou_cun
# --------------------------------------
DATA["wm4_xin_ban_xin_shou_cun"] = (
	"tp_wait_move_detect", {
		"Teleport": ("xin_ban_xin_shou_cun", (-15, 10, -183)),
		"Wait": (5,),
		"Move": ((-38, 11, -218),),
		"PositionDetect": ((-38, 11, -218), 1),
		"Timeout": (10,),
	},
)


# --------------------------------------
# template to test custom combine.
#
# key: test_custom_combine
# --------------------------------------
DATA["test_custom_combine"] = (
	"custom_serial", (
		("Teleport", ("xin_ban_xin_shou_cun", (-185, 28.6, -128))),
		("Wait", (5,)),
		("move_and_detect", {
			"destination": (-179.8, 28.2, -123.4),
			"range": 1,
			"timeout": 10,
			}
		),
		("move_and_detect", {
			"destination": (-165.6, 26.0, -109.4),
			"range": 1,
			"timeout": 10,
			}
		),
	)
)


# --------------------------------------
# template to teleport xin_shou_cun entry.
#
# key: teleport_xin_shou_cun_entry
# --------------------------------------
DATA["teleport_xin_shou_cun_entry"] = (
	"custom_serial", (
		("Teleport", ("xin_ban_xin_shou_cun", (-185, 28.6, -128))),
		("Wait", (40,)),
		("Talk", (7, "有人吗？这哪啊，我穿越啦!")),
	)
)


# --------------------------------------
# template to teleport teleport_feng_ming_cheng.
#
# key: teleport_xin_shou_cun_entry
# --------------------------------------
DATA["teleport_feng_ming_cheng"] = (
	"custom_serial", (
		("Teleport", ("fengming", (75, 15, 16))),
		("Wait", (40,)),
		("Talk", (7, "哈哈！I am coming!")),
	)
)


# --------------------------------------
# template to move to a position.
#
# key: teleport_xin_shou_cun_entry
# --------------------------------------
DATA["move_to_position"] = (
	"custom_serial", (
		("Move", ((-183, 13, -78),)),
	)
)


# --------------------------------------
# template to test loop task.
#
# key: teleport_xin_shou_cun_entry
# --------------------------------------
DATA["test_loop"] = (
	"loop", (1, 1, ("custom_serial", (
			("Move", ((-183, 13, -78),)),
			)
		)
	)
)


# --------------------------------------
# template to test test_custom_parallel.
#
# key: test_custom_parallel
# --------------------------------------
DATA["test_custom_parallel"] = (
	"custom_parallel", (
		("Teleport", ("xin_ban_xin_shou_cun", (-185, 28.6, -128))),
		("Move", ((0, 0, 0),),),
		("timeout", (
				10,
				("PositionDetect", ((0, 0, 0), 1, 0.5),),
			),
		),
		("timeout", (				# 嵌套任务模板timeout
				10,
				("loop", (			# 任务模板timeout中再嵌套loop模板
					1,
					3,
					("Talk", (1, "大家好。",),),
					),
				),
			),
		),
	),
)

# --------------------------------------
# template to test test_primacy_parallel.
#
# key: test_primacy_parallel
# --------------------------------------
DATA["test_primacy_parallel"] = (
	"primacy_parallel", (
		("Wait", (10,)),			# 第一个任务将作为主任务
		("timeout", (				# 嵌套任务模板timeout
				5,
				("loop", (			# 任务模板timeout中再嵌套loop模板
					1,
					3,
					("Talk", (1, "大家好。",),),
					),
				),
			),
		),
	),
)


# --------------------------------------
# template to test bot enter plane all plane of xin_ban_xin_shou_cun .
#
# key: all_wm_xin_ban_xin_shou_cun
# --------------------------------------
DATA["all_wm_xin_ban_xin_shou_cun"] = (
	"custom_serial", (
		# 先搞点钱，在世界频道喊话要钱
		("WizCommand", ("/set_money 999999999",)),

		# 先传送到新手村
		("Teleport", ("xin_ban_xin_shou_cun", (-185, 28.6, -128))),
		("Wait", (40,)),
		("Talk", (7, "有人吗？这哪啊，我穿越啦!")),
		("Wait", (3,)),

		# 向位面1前进
		("move_and_detect", {
			"destination": (-165.6, 26.0, -109.4),
			"range": 1,
			"timeout": 10,
			}
		),

		# 世界频道20秒才能说一次
		("Wait", (20,)),
		("Talk", (7, "我可能进入位面1啦!呃，可能...不管了，继续下一个，位面2！")),
		("Wait", (3,)),

		# 传送到位面2入口附近位置
		("Teleport", ("xin_ban_xin_shou_cun", (-173, 19.6, 50.4))),
		("Wait", (40,)),
		("Talk", (7, "开始进行位面2测试咯!")),

		# 向位面2前进
		("move_and_detect", {
			"destination": (-197, 24.5, 61),
			"range": 1,
			"timeout": 10,
			}
		),

		("Wait", (20,)),
		("Talk", (7, "我可能进入位面2啦!呃，可能...不管了，继续下一个，位面3！")),
		("Wait", (3,)),

		# 传送到位面3入口附近位置
		("Teleport", ("xin_ban_xin_shou_cun", (2, 19.2, 156))),
		("Wait", (40,)),
		("Talk", (7, "开始进行位面3测试咯!")),

		# 向位面3前进
		("move_and_detect", {
			"destination": (3.6, 20, 139.1),
			"range": 1,
			"timeout": 10,
			}
		),

		("Wait", (20,)),
		("Talk", (7, "我可能进入位面3啦!呃，可能...不管了，继续下一个，位面4！")),
		("Wait", (3,)),

		# 传送到位面4入口附近位置
		("Teleport", ("xin_ban_xin_shou_cun", (-15, 10, -183))),
		("Wait", (40,)),
		("Talk", (7, "开始进行位面4测试咯!")),

		# 向位面4前进
		("move_and_detect", {
			"destination": (-38, 11, -218),
			"range": 1,
			"timeout": 10,
			}
		),

		("Wait", (20,)),
		("Talk", (7, "位面4测试搞定！！我去，测个位面搞得忒么狼狈，位面5俺不去了，撤！88...")),
	)
)


# --------------------------------------
# taskapp test_focus_target
#
# key: test_focus_target_20321001
# --------------------------------------
DATA["test_focus_target_20321001"] = (
	"custom_serial", (
		("FocusTarget", ((20321001,),),),
	),
)


# --------------------------------------
DATA["test_focus_self"] = (
	"custom_serial", (
		("FocusSelf", (),),
	),
)


# --------------------------------------
# taskapp test_focus_target
#
# key: test_focus_enemy_20321002
# --------------------------------------
DATA["test_focus_enemy_20321002"] = (
	"custom_serial", (
		("FocusEnemy", ((20321002,),),),
	),
)


# --------------------------------------
# taskapp test_focus_target
#
# key: test_add_skill_311153001
# --------------------------------------
DATA["test_add_skill_311153001"] = (
	"custom_serial", (
		("AddSkills", ((311153001,), 32),),
	),
)


# --------------------------------------
# taskapp test_focus_target
#
# key: test_spell_target_with_311153001
# --------------------------------------
DATA["test_spell_target_with_311153001"] = (
	"custom_serial", (
		("SpellTarget", (311153001,),),
	),
)


# --------------------------------------
# taskapp test_fight_to_enemy
#
# key: test_fight_to_enemy
# --------------------------------------
DATA["test_fight_to_enemy"] = (
	"repeat", (
		10,
		("custom_serial", (
			# 选择一个敌对目标，npc id是20321001
			("FocusEnemy", (("20321001",),),),
			("primacy_parallel", (			# 使用主任务模板
				("TargetDead", (),),		# 主任务：当目标死亡时就停止任务
				("repeat", (
					-1,
					("custom_serial", (
						# 追上目标
						("SeekTarget", (),),
						# 如果是战士，就使用技能323175001
						("ProfessionSpell", (323175001, 16),),
						# 如果是剑客，就使用技能311338001
						("ProfessionSpell", (311338001, 32),),
						# 如果是射手，就使用技能321210001
						("ProfessionSpell", (321210001, 48),),
						("Wait", (1,),),
					),),
				),),
			),),
		),),
	),
)
