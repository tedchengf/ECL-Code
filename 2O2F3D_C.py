import numpy as np
import time
import random
from itertools import product 
from psychopy import visual, core, data, event, sound
import gc
import os

import stimuli

OBJ_SIZE = [8,6]
LOG_FLAG = False

def main():
	# Sigma Settings
	METAL = ["Turpeth", "Solaris", "Infernalis"]
	SALT = ["Alembroth", "Volatile", "Petrae"]
	ACID = "Hartshorn"
	R = 2
	GENERATION_MODE = "Combination"

	# Formula Pool
	Bool_Conj = [(1,0,0), (0,0,1)]
	Sum_Conj = {
		"A": [(1,0,0), (0,0,1)],
	}
	Prod_Conj = {
		"A": [[(1,0,0), (0,0,0)], [(0,0,0), (0,0,1)]]
	}
	CORRECT = 24
	INCORRECT = 56

	# Output Settings
	DIRECTORY = "./rsps/2O2F3D_C/"
	HEADER = ["Blc", "Seq", "Rsp", "Truth", "Rsp_t1", "Rsp_t2", "Cnfdnc"]

	###########################################################################

	# Init Sigma
	SIG = stimuli.Sigma([METAL, SALT], ["metal", "salt"], R, generation_mode = GENERATION_MODE)
	for obj in SIG.objects: print(obj)
	# print(len(SIG.objects))
	# print(len(SIG.sequences))
	# exit()

	# ###
	# conj_hypotheses = []
	# for conj in SIG.generate_conjuncts(conjunct_type = "Sum", subset_type = ">="):
	# 	sol_card = len(SIG.satisfies(conj))
	# 	if sol_card > 0: conj_hypotheses.append(conj)

	# # True_formula = SIG.form_conjunct(Prod_Conj["A"], conjunct_type = "Product", subset_type = ">=")
	# True_formula = SIG.form_conjunct(Bool_Conj, conjunct_type = "Sum", subset_type = ">=")
	# # True_formula = SIG.form_conjunct(Sum_Conj["A"], conjunct_type = "Sum", subset_type = "==")
	# model = stimuli.Simple_Bayesian(conj_hypotheses)
	# correct_seq, incorrect_seq = seq_handler(SIG, SIG.sequences, True_formula, CORRECT, INCORRECT)
	# block_seq = correct_seq + incorrect_seq
	# random.shuffle(block_seq)
	# for seq in block_seq: 
	# 	model.update(seq, seq.satisfies(True_formula))
	# best_conjs, best_probs = model.find_max(n = 4)
	# for ind in range(len(best_conjs)):
	# 	print(best_probs[ind])
	# 	print(best_conjs[ind].hierarchical_rep())
	# exit()
	# ###

	# Get input settings
	sub_code = input("Enter Subject code: ")
	while os.path.exists(DIRECTORY + sub_code):
		sub_code = input("Duplicate Subject code. Enter a new code again: ")
	conj_mode = input("Enter Formula Mode: ")
	while conj_mode not in ("B", "S", "P"):
		conj_mode = input("Incorrect Format; Enter Formula Mode Again: ")
	if conj_mode in ("S", "P"):
		conj_type = input("Enter Formula List: ")
		while conj_type not in ("A", "B"):
			conj_type = input("Incorrect Format; Enter Formula List Again: ")
	if conj_mode == "B": 
		prod_conj = SIG.form_conjunct(Bool_Conj, conjunct_type = "Sum")
	if conj_mode == "S":
		prod_conj = SIG.form_conjunct(Sum_Conj[conj_type], conjunct_type = "Sum", subset_type = "==")
	if conj_mode == "P":
		prod_conj = SIG.form_conjunct(Prod_Conj[conj_type], conjunct_type = "Product")
	if LOG_FLAG == True:
		os.makedirs(DIRECTORY + sub_code)
		DIRECTORY += sub_code + "/"
		with open(DIRECTORY + "Sub_resp.csv", "a") as outfile:
			outfile.write("Subject code: " + sub_code + "\n")
			outfile.write("Formula mode: " + conj_mode + "\n")
			if conj_mode in ("S", "P"):
				outfile.write("Formula List: " + conj_type)
			outfile.write("\n")
			outfile.write("\t".join(HEADER))
			outfile.write("\n")

	###########################################################################
	
	# Presentation Settings
	WIN = visual.Window([1728, 1117], monitor="testMonitor", units="deg", fullscr = False, useRetina = True)
	# WIN = visual.Window([1728, 1117], monitor="testMonitor", units="deg", fullscr = False, useRetina = True, screen = 1)
	# WIN = visual.Window([2560, 1440], monitor="testMonitor", units="deg", fullscr = False, useRetina = True, screen = 0)
	STIMSIZE = None
	OBJ_DICT = {
		0: [visual.ImageStim(WIN, "rsc/2O2F3D_C/Hartshorn.png", size = STIMSIZE), visual.ImageStim(WIN, "rsc/2O2F3D_C/Hartshorn.png", size = STIMSIZE)],
		2: visual.ImageStim(WIN, "rsc/2O2F3D_C/TA.png"),
		3: visual.ImageStim(WIN, "rsc/2O2F3D_C/TV.png"),
		5: visual.ImageStim(WIN, "rsc/2O2F3D_C/TP.png"),
		7: visual.ImageStim(WIN, "rsc/2O2F3D_C/SA.png"),
		11: visual.ImageStim(WIN, "rsc/2O2F3D_C/SV.png"),
		13: visual.ImageStim(WIN, "rsc/2O2F3D_C/SP.png"),
		17: visual.ImageStim(WIN, "rsc/2O2F3D_C/IA.png"),
		19: visual.ImageStim(WIN, "rsc/2O2F3D_C/IV.png"),
		23: visual.ImageStim(WIN, "rsc/2O2F3D_C/IP.png")
	}
	OBJ_LINSPACE = [-8.3, 0, 8.3]
	TRIAL_OBJ_DICT = {
		"prompt_msg": visual.TextBox2(WIN, 'Your Prediction: ', pos = [-10, -5], alignment = 'right', letterHeight = 1),
		"true_usr": visual.TextBox2(WIN, 'True', pos = [15, -5], alignment = 'left', color = "Green", letterHeight = 1),
		"fals_usr": visual.TextBox2(WIN, 'False', pos = [15, -5], alignment = 'left', color = "Red", letterHeight = 1),
		"response_msg": visual.TextBox2(WIN, 'Correct Response: ', pos = [-10, -7], alignment = 'right', letterHeight = 1),
		"true_rsp": visual.TextBox2(WIN, 'True', pos = [15, -7], alignment = 'left', color = "Green", letterHeight = 1),
		"fals_rsp": visual.TextBox2(WIN, 'False', pos = [15, -7], alignment = 'left', color = "Red", letterHeight = 1),
		"Correct_sound": sound.Sound("rsc/Correct.wav"),
		"Incorrect_sound": sound.Sound("rsc/Incorrect.wav"),
		"Correct_text": visual.TextBox2(WIN, "Congrats! You prediction is correct!", pos = [0, -10], alignment = 'center', color = "Green", letterHeight = 0.8),
		"Incorrect_text": visual.TextBox2(WIN, "Unfortunately, your prediction is incorrect.", pos = [0, -10], alignment = 'center', color = "Red", letterHeight = 0.8)
	}
	global PROCEED_KEYS
	global ABORT_KEY
	PROCEED_KEYS = ["space", "return"]
	ABORT_KEY = "q"

	###########################################################################

	# define a manual
	ctrl = visual.TextBox2(WIN, "T: True            F: False            1-5: Confidence Rating            Space/Enter: Proceed", size = [30,3], alignment = "center", pos = (0,-15), letterHeight = 0.7, fillColor = "black", opacity = 0.5, borderWidth = 0)
	disp_objs = [ctrl]
	
	# Prepare Stimuli
	correct_seq, incorrect_seq = seq_handler(SIG, SIG.sequences, prod_conj, CORRECT, INCORRECT)
	block_seq = correct_seq + incorrect_seq
	block_seq = block_seq

	# Starters
	starter_win(WIN, disp_objs)
	random.shuffle(block_seq)
	repeat_flag = True
	while repeat_flag:
		repeat_flag = test_block(WIN, OBJ_DICT, TRIAL_OBJ_DICT, block_seq[:4], prod_conj, OBJ_LINSPACE, disp_objs)
	core.wait(1)

	# training block 1
	block_disp_start = visual.TextBox2(WIN, "Now that you are farmiliar with Master Andreae’s notation, you decide to go through the 80 formulas.", alignment = 'left', letterHeight = 0.8)
	block_disp_end = visual.TextBox2(WIN, "And that's the end of the notes. You decide to take a short rest before continuing.", alignment = 'left', letterHeight = 0.8)
	cont_disp0 = visual.TextBox2(WIN, "(This is the start of block 1. Press any key to start.)",pos = (0, -3), alignment = 'center', letterHeight = 0.8)	
	cont_disp1 = visual.TextBox2(WIN, "(This is the end of block 1. Press any key to continue.)",pos = (0, -3), alignment = 'center', letterHeight = 0.8)	
	random.shuffle(block_seq)
	any_cont(WIN, ABORT_KEY, [block_disp_start, cont_disp0])
	core.wait(0.4)
	block_rsp = block(WIN, 1, OBJ_DICT, TRIAL_OBJ_DICT, block_seq, prod_conj, OBJ_LINSPACE, disp_objs)
	if LOG_FLAG == True:
		with open(DIRECTORY + "Sub_resp.csv", "a") as outfile:
			for rind in range(len(block_rsp)):
				outfile.write("\t".join(block_rsp[rind].astype(str)))
				outfile.write("\n")
	any_cont(WIN, ABORT_KEY, [block_disp_end, cont_disp1])
	core.wait(0.8)

	# training block 2		
	block_disp_start = visual.TextBox2(WIN, "You are now ready to go through the notes again.", alignment = 'center', letterHeight = 0.8)
	block_disp_end = visual.TextBox2(WIN, "You have gone through Master Andreae’s note twice and believe that you have more or less gotten down to the truth behind Chrysopoeia. However, just when you are about to leave the library …", alignment = 'left', pos = (0, 2), letterHeight = 0.8)
	cont_disp0 = visual.TextBox2(WIN, "(This is the start of block 2. Press any key to start.)",pos = (0, -3), alignment = 'center', letterHeight = 0.8)	
	cont_disp1 = visual.TextBox2(WIN, "(This is the end of block 2. Press any key to continue.)",pos = (0, -3), alignment = 'center', letterHeight = 0.8)	
	random.shuffle(block_seq)
	any_cont(WIN, ABORT_KEY, [block_disp_start, cont_disp0])
	core.wait(0.4)
	block_rsp = block(WIN, 2, OBJ_DICT, TRIAL_OBJ_DICT, block_seq, prod_conj, OBJ_LINSPACE, disp_objs)
	if LOG_FLAG == True:
		with open(DIRECTORY + "Sub_resp.csv", "a") as outfile:
			for rind in range(len(block_rsp)):
				outfile.write("\t".join(block_rsp[rind].astype(str)))
				outfile.write("\n")
	any_cont(WIN, ABORT_KEY, [block_disp_end, cont_disp1])
	core.wait(0.8)

	# generalization block
	OBJ_LINSPACE = [-16.6 ,-8.3, 0, 8.3, 16.6]
	# OBJ_LINSPACE = np.arange(-30, 31, 4)
	SIG_gen = stimuli.Sigma([METAL, SALT], ["metal", "salt"], R + 1, generation_mode = GENERATION_MODE)
	sol, non_sol = SIG_gen.satisfies(prod_conj, return_non_solutions = True)
	correct_seq, incorrect_seq = seq_handler(SIG_gen, SIG_gen.sequences, prod_conj, 6, 6)
	block_seq = correct_seq + incorrect_seq
	
	block_disp_start = visual.TextBox2(WIN, "You are confronted by master Andreae himself,  steadily breathing and walking on his legs! As it turns out, the old geezer faked his own death just to give you a prank of a lifetime (although he himself insisted that he is only testing your ability as an alchemist). And while you are still recovering from the shock, master Andreae throws you 12 novel formulas and asks you to predict whether they will produce gold. Except that this time you no longer have access to the experiment result. You press on, hoping that you have indeed learned the right configuration.", alignment = 'left', pos = (0, 5), size = [40, None],  letterHeight = 0.8)
	block_disp_end = visual.TextBox2(WIN, "You have finished the 12 formulas Master Andreae gave you. You wondered how you perform, but only Andreae knows the answer. You gather your thoughts and leave the library.", alignment = 'left', pos = (0, 2), letterHeight = 0.8)
	cont_disp0 = visual.TextBox2(WIN, "(This is the start of the Generalization Block. Press any key to start.)",pos = (0, -3), size = [40, None], alignment = 'center', letterHeight = 0.8)
	cont_disp1 = visual.TextBox2(WIN, "(This is the end of the experiment. Thank you for your participation!)",pos = (0, -3), size = [40, None], alignment = 'center', letterHeight = 0.8)	
	random.shuffle(block_seq)
	any_cont(WIN, ABORT_KEY, [block_disp_start, cont_disp0])
	core.wait(0.4)
	block_rsp = block(WIN, "G1", OBJ_DICT, TRIAL_OBJ_DICT, block_seq, prod_conj, OBJ_LINSPACE, disp_objs, show_truth = False)
	if LOG_FLAG == True:
		with open(DIRECTORY + "Sub_resp.csv", "a") as outfile:
			for rind in range(len(block_rsp)):
					outfile.write("\t".join(block_rsp[rind].astype(str)))
					outfile.write("\n")	
	any_cont(WIN, ABORT_KEY, [block_disp_end, cont_disp1])
	core.wait(0.8)

	WIN.close()
	return

def seq_handler(sig, sequences, formula, correct_num, incorrect_num):
	correct_comb = []
	incorrect_comb = []
	for seq in sequences:
		if seq.satisfies(formula): correct_comb.append(seq)
		else: incorrect_comb.append(seq)
	extended_correct = __sq_helper(sig, correct_comb, correct_num)
	extended_incorrect = __sq_helper(sig, incorrect_comb, incorrect_num)
	return extended_correct, extended_incorrect

def __sq_helper(sig, comb, num):
	full_perm = sig.fully_permute_sequences(comb)
	extended_seq = []
	if len(full_perm) < num:
		extended_seq = full_perm
	random.shuffle(comb)
	perm_gen = [seq.permute() for seq in comb]
	curr_ind = 0
	while len(extended_seq) < num:
		if curr_ind >= len(perm_gen): curr_ind = 0
		try:
			extended_seq.append(next(perm_gen[curr_ind]))
			curr_ind += 1
		except StopIteration:
			random.shuffle(comb)
			perm_gen = [seq.permute() for seq in comb]
	return extended_seq

def record_file(directory, name, titles, contents):
	with open(directory + name + ".csv", "a") as outfile:
		outfile.write("\t".join(titles))
		outfile.write("\n")
		for rind in range(len(contents)):
			outfile.write("\t".join(contents[rind].astype(str)))
			outfile.write("\n")
		outfile.write("\n")
	return

def end_win(win, disp_objs = []):
	end_msg0 = visual.TextBox2(win, "This is the end of the experiment.\nThank you for your participation!", pos = (0,2), size = [40, None], letterHeight = 1.5, alignment = "center")
	end_msg1 = visual.TextBox2(win, "Press any key to end", pos = (0,-3), size = [30, None], letterHeight = 0.8, alignment = "center")
	any_cont(win, ABORT_KEY, [end_msg0, end_msg1])
	return

def starter_win(win, disp_objs = []):
	# Signal start of the experiment
	welcome_msg0 = visual.TextBox2(win, "Welcome to the experiment!", pos = (0,2), size = [40, None], letterHeight = 1.5, alignment = "center")
	welcome_msg1 = visual.TextBox2(win, "Press any key to start", pos = (0,-3), size = [30, None], letterHeight = 0.8, alignment = "center")

	any_cont(win, ABORT_KEY, [welcome_msg0, welcome_msg1])
	core.wait(0.4)

	# Control Page
	control_msg0 = visual.TextBox2(win, "Here are your controls for the experiments:", pos = (0,4), size = [31, None], alignment = "left", letterHeight = 1.3)
	ctrl = visual.TextBox2(win, "T: True            F: False            1-5: Confidence Rating            Space/Enter: Proceed", size = [30,3], alignment = "center", pos = (0,0), letterHeight = 0.7, fillColor = "black", opacity = 0.5, borderWidth = 0)
	control_msg1 = visual.TextBox2(win, "These control mappings will be kept at the bottom of the screen during the entire experiment. Now, please press space/return to proceed.", pos = (0, -4), size = [31, None], alignment = "left", letterHeight = 0.8)
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [control_msg0, ctrl, control_msg1])
	core.wait(0.4)

	# Background Messages
	starter_msg0 = visual.TextBox2(win, "Background Story:", pos = (0,7), size = [41, None], alignment = 'left', letterHeight = 1.6)
	starter_msg1 = visual.TextBox2(win,"     You are the student of the renowned alchemist Johannes Valentinus Andreae, the master in the field of Chrysopoeia (transmuting gold from base metals). Master Andreae was one step away from realizing profitable Chrysopoeia when he died of a chronic illness. The burden of completing his Magnum Opus falls on your shoulder. In this experiment, you will consult the notes of master Andreae and find out the minimal configuration of the materials that will be transmuted into gold. \n\n      Master Andreae managed to shrink down the potential ingredient to 1 acid (Acidum Hartshorn), three metals (Lapis Turpeth, Lapis Solaris, Lapis Infernalis) and three salts (Sol Alembroth, Sol Volatile, Sol Petrae). Specifically, his formula binds two metal-salt compounds with the acid to produce gold. However, as you will see later, not all of his formulas work. Your duty, therefore, is to go through these formulas and deduce the correct (and minimal) configuration that will always achieve Chrysopoeia.", pos = (0,-2), size = [40, None], alignment = 'left', letterHeight = 0.7)
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [starter_msg0, starter_msg1] + disp_objs)
	core.wait(0.2)
	
	# More Background notes
	msg1 = visual.TextBox2(win,"Before going into the task, You want to familiarize yourself with Master Andreae’s notation. Above are the three types of metals you will see. They are all color-coded in orange.", pos = (0,-7), size = [40, None], alignment = 'left', letterHeight = 0.8)
	obj0 = visual.ImageStim(win, "rsc/2O2F3D_C/T.png", pos = (-8,1))
	obj1 = visual.ImageStim(win, "rsc/2O2F3D_C/S.png", pos = (0,1))
	obj2 = visual.ImageStim(win, "rsc/2O2F3D_C/I.png", pos = (8,1))
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [msg1, obj0, obj1, obj2] + disp_objs)
	core.wait(0.2)

	msg1 = visual.TextBox2(win,"Above are the three types of salts you will see. They are all color-coded in blue.", pos = (0,-7), size = [40, None], alignment = 'left', letterHeight = 0.8)
	obj0 = visual.ImageStim(win, "rsc/2O2F3D_C/A.png", pos = (-8,1))
	obj1 = visual.ImageStim(win, "rsc/2O2F3D_C/V.png", pos = (0,1))
	obj2 = visual.ImageStim(win, "rsc/2O2F3D_C/P.png", pos = (8,1))
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [msg1, obj0, obj1, obj2] + disp_objs)
	core.wait(0.2)

	msg1 = visual.TextBox2(win,"Master Andrae creates a metal-salt compound by mixing a metal with a salt. A compound (shown above) is represented as two elements inside a rectangular box.", pos = (0,-7), size = [40, None], alignment = 'left', letterHeight = 0.8)
	obj0 = visual.ImageStim(win, "rsc/2O2F3D_C/TA.png", pos = (0,1))
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [msg1, obj0] + disp_objs)
	core.wait(0.2)

	msg1 = visual.TextBox2(win,"A formula is composed of two compounds plus one acid (Hartshorn) that binds them together. Above is a formula written down in the notes.", pos = (0,-7), size = [40, None], alignment = 'left', letterHeight = 0.8)
	obj0 = visual.ImageStim(win, "rsc/2O2F3D_C/TA.png", pos = (-8.3,1), size = OBJ_SIZE)
	obj1 = visual.ImageStim(win, "rsc/2O2F3D_C/Hartshorn.png", pos = (0,1), size = OBJ_SIZE)
	obj2 = visual.ImageStim(win, "rsc/2O2F3D_C/IP.png", pos = (8.3,1), size = OBJ_SIZE)
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [msg1, obj0, obj1, obj2] + disp_objs)
	core.wait(0.2)

	msg1 = visual.TextBox2(win,"In this experiment, you will see a formula from Master Andreae’s notebook at each trial. To engage yourself with the task, you decide to first predict whether the formula will produce gold. You then record your confidence and see if your prediction matches the experimental result. There are 80 formulas written down, and you will go through each of them twice (in two blocks).", pos = (0,1), size = [40, None], alignment = 'left', letterHeight = 0.8)
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [msg1] + disp_objs)
	core.wait(0.2)

	test_msg = visual.TextBox2(win, "Before officially starting the experiment, let's do some practice trials so that you understand the procedure.", pos = (0,0), size = [30, None], letterHeight = 0.8, alignment = "left")
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [test_msg] + disp_objs)
	core.wait(0.4)
	return

def test_block(win, obj_dict, trial_obj_dict, sequences, formula, obj_linspace, disp_objs = []):
	test_disp_start = visual.TextBox2(win, "Practice Block", alignment = 'center', letterHeight = 1)
	cont_disp0 = visual.TextBox2(win, "Press any key to start",pos = (0, -3), alignment = 'center', letterHeight = 0.8)
	any_cont(win, ABORT_KEY, [test_disp_start, cont_disp0])

	total_rsp = np.empty((len(sequences), 6), dtype = object)
	for ind, seq in enumerate(sequences):
		curr_disp_objs = disp_objs.copy()
		trial_counter = visual.TextBox2(win, "Trial " + str(ind + 1) + " out of " + str(len(sequences)) + ".", pos = [0,13], alignment = 'center', letterHeight = 0.7)
		curr_disp_objs.append(trial_counter)
		total_rsp[ind] = trial(win, obj_dict, trial_obj_dict, seq, formula, obj_linspace, curr_disp_objs)
		core.wait(0.4)
	
	test_disp_end = visual.TextBox2(win, "This is the end of the practice block.", pos = [0,0], alignment = 'center', letterHeight = 1)
	cont_disp1 = visual.TextBox2(win, "Press space/return to proceed to Block 1\nPress R to repeat the practice block", pos = (0,-3), letterHeight = 0.8, alignment = 'center')
	test_disp_end.draw()
	cont_disp1.draw()
	win.flip()
	while True:
		allKeys = event.waitKeys()
		break_flag = False
		repeat_flag = False
		for thisKey in allKeys:
			if thisKey == ABORT_KEY: exit("Experiment Aborted")
			if thisKey == "r":
				break_flag = True
				repeat_flag = True
				break
			if thisKey in PROCEED_KEYS:
				break_flag = True
				break
		if break_flag == True: break
	win.flip()
	event.clearEvents()
	core.wait(0.8)
	return repeat_flag

def block(win, block_num, obj_dict, trial_obj_dict, sequences, formula, obj_linspace, disp_objs = [], show_truth = True):
	total_rsp = np.empty((len(sequences), 7), dtype = object)
	total_rsp[:, 0] = block_num
	for ind, seq in enumerate(sequences):
		curr_disp_objs = disp_objs.copy()
		trial_counter = visual.TextBox2(win, "Trial " + str(ind + 1) + " out of " + str(len(sequences)) + ".", pos = [0,13], alignment = 'center', letterHeight = 0.7)
		curr_disp_objs.append(trial_counter)
		total_rsp[ind, 1:] = trial(win, obj_dict, trial_obj_dict, seq, formula, obj_linspace, curr_disp_objs, show_truth = show_truth)
		core.wait(0.4)
	return total_rsp

def any_cont(win, abort_key, disp_objs):
	win.flip()
	for obj in disp_objs: obj.draw()
	win.flip()
	while True:
		allKeys = event.waitKeys()
		for thisKey in allKeys: 
			if thisKey == abort_key: exit("Experiment Aborted")
		if len(allKeys) != 0: break
	win.flip()
	event.clearEvents()
	return

def spec_cont(win, abort_key, spec_keys, disp_objs):
	win.flip()
	for obj in disp_objs: obj.draw()
	win.flip()
	while True:
		allKeys = event.waitKeys()
		break_flag = False
		for thisKey in allKeys:
			if thisKey == abort_key: exit("Experiment Aborted")
			if thisKey in spec_keys:
				break_flag = True
				break
		if break_flag == True: break
	win.flip()	
	event.clearEvents()
	return

def trial(win, obj_dict, trial_obj_dict, Sequence, formula, obj_linspace, disp_objs = [], show_truth = True):
	# Initialize Objects
	# print(Sequence.hierarchical_rep())
	seq_rep = ""
	for obj in Sequence.objects:
		seq_rep += str(obj.id) + "; "
	seq_rep = seq_rep[:-2]

	win_objs = []
	filler_gen = obj_dict[0].__iter__()
	for obj_ind, obj in enumerate(Sequence.objects):
		win_objs += [obj_dict[obj.id]]
		if obj_ind < len(Sequence.objects) - 1:
			win_objs += [next(filler_gen)]
	for obj_ind in range(len(win_objs)):
		win_objs[obj_ind].pos = [obj_linspace[obj_ind], 2]
		win_objs[obj_ind].size = OBJ_SIZE

	prompt_msg = trial_obj_dict["prompt_msg"]
	true_usr = trial_obj_dict["true_usr"]
	fals_usr = trial_obj_dict["fals_usr"]
	response_msg = trial_obj_dict["response_msg"]
	true_rsp = trial_obj_dict["true_rsp"]
	fals_rsp = trial_obj_dict["fals_rsp"]
	Correct_sound = trial_obj_dict["Correct_sound"]
	Incorrect_sound = trial_obj_dict["Incorrect_sound"]
	Correct_text = trial_obj_dict["Correct_text"]
	Incorrect_text = trial_obj_dict["Incorrect_text"]
	ratingScale = visual.RatingScale(win, low = 1, high = 5, labels = ["(1) I was just guessing", "(5) Very Confident"], scale = "How confident are you in your prediction?", markerColor = "orange", pos = (0,0), size = 1.2, stretch = 1.4, textSize = 0.8, acceptPreText = "Your rating: ", acceptKeys = ['return', 'space'])
	ground_truth = Sequence.satisfies(formula)

	# # Actual trial
	# while True:
	# 	# Drawing
	# 	for obj in win_objs: obj.draw()
	# 	for obj in disp_objs: obj.draw()
	# 	prompt_msg.draw()
	# 	win.flip(clearBuffer = False)

	# 	start_time = time.time()
	# 	# Prompt user response
	# 	curr_rsp = None
	# 	while curr_rsp is None:
	# 		allKeys = event.waitKeys()
	# 		for thisKey in allKeys:
	# 			if thisKey == "q": exit("Experiment Aborted")
	# 			if thisKey == "t":
	# 				true_usr.draw()
	# 				curr_rsp = True
	# 				end_time = time.time()
	# 				break
	# 			if thisKey == "f":
	# 				fals_usr.draw()
	# 				curr_rsp = False
	# 				end_time = time.time()
	# 				break
	# 	for obj in win_objs: obj.draw()
	# 	for obj in disp_objs: obj.draw()
	# 	prompt_msg.draw()
	# 	win.flip(clearBuffer = False)
	# 	rspt_1 = end_time - start_time
	# 	trial_rsp = curr_rsp
	# 	break

	# while True:
	# 	allKeys = event.waitKeys()
	# 	break_flag = False
	# 	for thisKey in allKeys:
	# 		if thisKey == "q": exit("Experiment Aborted")
	# 		if thisKey == 'space' or thisKey == 'return':
	# 			break_flag = True
	# 			break
	# 	if break_flag == True: break
	
	start_time = time.time()
	trial_rsp = decision_process(win, win_objs, disp_objs, prompt_msg, true_usr, fals_usr)
	end_time = time.time()
	rspt_1 = end_time - start_time


	# Confidence Ratings
	core.wait(0.1)
	win.flip()
	while ratingScale.noResponse:
		ratingScale.draw()
		for obj in disp_objs: obj.draw()
		win.flip()
	rating = ratingScale.getRating()
	rating = ratingScale.getRating()
	win.flip()
	core.wait(0.1)

	if show_truth == True:
		# Update window
		for obj in win_objs: obj.draw()
		for obj in disp_objs: obj.draw()
		prompt_msg.draw()
		response_msg.draw()
		if ground_truth == True: true_rsp.draw()
		else: fals_rsp.draw()
		if trial_rsp == True:
			true_usr.draw()
		else:
			fals_usr.draw()
		if trial_rsp == ground_truth: 
			Correct_sound.play()
			Correct_text.draw()
		else: 
			Incorrect_sound.play()
			Incorrect_text.draw()
		win.flip(clearBuffer = False)


		# Wait for user response to finish the trial
		start_time = time.time()
		while True:
			allKeys = event.waitKeys()
			break_flag = False
			for thisKey in allKeys:
				if thisKey == "q": exit("Experiment Aborted")
				if thisKey == 'space' or thisKey == 'return':
					break_flag = True
					end_time = time.time()
					break
			if break_flag == True: break
		rspt_2 = end_time - start_time
	else: rspt_2 = -1

	win.flip()
	win.flip()
	event.clearEvents()

	return [seq_rep, trial_rsp, ground_truth, rspt_1, rspt_2, rating]

def decision_process(win, win_objs, disp_objs, prompt_msg, true_usr, fals_usr):
	prev_rsp = None
	# Actual trial
	while True:
		# Drawing
		win.flip()
		for obj in win_objs: obj.draw()
		for obj in disp_objs: obj.draw()
		prompt_msg.draw()
		if prev_rsp is not None: prev_rsp.draw()
		win.flip(clearBuffer = False)

		# Prompt user response
		curr_rsp = None
		while curr_rsp is None:
			allKeys = event.waitKeys()
			for thisKey in allKeys:
				if thisKey == "q": exit("Experiment Aborted")
				if thisKey == "t":
					true_usr.draw()
					prev_rsp = true_usr
					curr_rsp = True
					break
				if thisKey == "f":
					fals_usr.draw()
					prev_rsp = fals_usr
					curr_rsp = False
					break
				if thisKey == 'space' or thisKey == 'return':
					if prev_rsp is not None:
						if prev_rsp == true_usr: return True
						else: return False
		prompt_msg.draw()
		win.flip(clearBuffer = False)


if __name__ == "__main__":
	main()

