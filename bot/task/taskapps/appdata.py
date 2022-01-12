# -*- coding: gb18030 -*-
"""
--------------------------------------------------
�����˲����������ð����ĵ�
--------------------------------------------------
����alienbrain://NEWAB/����Online/��������/�����˲���/�����˲����������ð����ĵ�.txt
"""


# �����˲����������ݣ�Ŀǰ�ڴ������ֶ���д���������Կ���
# �������ã������ö�ȡ
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
		("Talk", (7, "���������İ����Ҵ�Խ��!")),
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
		("Talk", (7, "������I am coming!")),
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
		("timeout", (				# Ƕ������ģ��timeout
				10,
				("loop", (			# ����ģ��timeout����Ƕ��loopģ��
					1,
					3,
					("Talk", (1, "��Һá�",),),
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
		("Wait", (10,)),			# ��һ��������Ϊ������
		("timeout", (				# Ƕ������ģ��timeout
				5,
				("loop", (			# ����ģ��timeout����Ƕ��loopģ��
					1,
					3,
					("Talk", (1, "��Һá�",),),
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
		# �ȸ��Ǯ��������Ƶ������ҪǮ
		("WizCommand", ("/set_money 999999999",)),

		# �ȴ��͵����ִ�
		("Teleport", ("xin_ban_xin_shou_cun", (-185, 28.6, -128))),
		("Wait", (40,)),
		("Talk", (7, "���������İ����Ҵ�Խ��!")),
		("Wait", (3,)),

		# ��λ��1ǰ��
		("move_and_detect", {
			"destination": (-165.6, 26.0, -109.4),
			"range": 1,
			"timeout": 10,
			}
		),

		# ����Ƶ��20�����˵һ��
		("Wait", (20,)),
		("Talk", (7, "�ҿ��ܽ���λ��1��!��������...�����ˣ�������һ����λ��2��")),
		("Wait", (3,)),

		# ���͵�λ��2��ڸ���λ��
		("Teleport", ("xin_ban_xin_shou_cun", (-173, 19.6, 50.4))),
		("Wait", (40,)),
		("Talk", (7, "��ʼ����λ��2���Կ�!")),

		# ��λ��2ǰ��
		("move_and_detect", {
			"destination": (-197, 24.5, 61),
			"range": 1,
			"timeout": 10,
			}
		),

		("Wait", (20,)),
		("Talk", (7, "�ҿ��ܽ���λ��2��!��������...�����ˣ�������һ����λ��3��")),
		("Wait", (3,)),

		# ���͵�λ��3��ڸ���λ��
		("Teleport", ("xin_ban_xin_shou_cun", (2, 19.2, 156))),
		("Wait", (40,)),
		("Talk", (7, "��ʼ����λ��3���Կ�!")),

		# ��λ��3ǰ��
		("move_and_detect", {
			"destination": (3.6, 20, 139.1),
			"range": 1,
			"timeout": 10,
			}
		),

		("Wait", (20,)),
		("Talk", (7, "�ҿ��ܽ���λ��3��!��������...�����ˣ�������һ����λ��4��")),
		("Wait", (3,)),

		# ���͵�λ��4��ڸ���λ��
		("Teleport", ("xin_ban_xin_shou_cun", (-15, 10, -183))),
		("Wait", (40,)),
		("Talk", (7, "��ʼ����λ��4���Կ�!")),

		# ��λ��4ǰ��
		("move_and_detect", {
			"destination": (-38, 11, -218),
			"range": 1,
			"timeout": 10,
			}
		),

		("Wait", (20,)),
		("Talk", (7, "λ��4���Ը㶨������ȥ�����λ����߯ô�Ǳ���λ��5����ȥ�ˣ�����88...")),
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
			# ѡ��һ���ж�Ŀ�꣬npc id��20321001
			("FocusEnemy", (("20321001",),),),
			("primacy_parallel", (			# ʹ��������ģ��
				("TargetDead", (),),		# �����񣺵�Ŀ������ʱ��ֹͣ����
				("repeat", (
					-1,
					("custom_serial", (
						# ׷��Ŀ��
						("SeekTarget", (),),
						# �����սʿ����ʹ�ü���323175001
						("ProfessionSpell", (323175001, 16),),
						# ����ǽ��ͣ���ʹ�ü���311338001
						("ProfessionSpell", (311338001, 32),),
						# ��������֣���ʹ�ü���321210001
						("ProfessionSpell", (321210001, 48),),
						("Wait", (1,),),
					),),
				),),
			),),
		),),
	),
)
