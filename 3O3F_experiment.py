import numpy as np
import time
from itertools import product 
from psychopy import visual, core, data, event, sound
import gc
import os

import stimuli

def main():
	# Sigma Settings
	FILL = ["red", "blue"]
	TEXTURE = ["dotted", "slashed"]
	SHAPE = ["circle", "triangle"]
	R = 3
	GENERATION_MODE = "Combination"
	PROD_FORMULA = [{("fill", "red"): 1, ("shape", "triangle"): 1}, {("texture", "dotted"): 1}]

	# Formula Pool
	Bool_Conj = [[1, 1], [1, 1], [1, 1]]
	Sum_Conj = {
		"A": [[1,2], [0], [0]],
		"B": [[0], [2,1], [0]],
		"C": [[0], [0], [1,2]]
	}
	Prod_Conj = {
		"A": [[[1, 0], [0, 0], [0, 0]], [[1, 0], [0, 0], [1, 0]], [[0, 0], [0, 0], [0, 0]]],
		"B": [[[0, 0], [0, 0], [0, 1]], [[0, 0], [1, 0], [0, 1]], [[0, 0], [0, 0], [0, 0]]],
		"C": [[[0, 0], [0, 1], [0, 0]], [[0, 1], [0, 1], [0, 0]], [[0, 0], [0, 0], [0, 0]]]
	}

	# Output Settings
	DIRECTORY = "./rsps/3O3F"
	HEADER = ["Blc", "Seq", "Rsp", "Truth", "Rsp_t1", "Rsp_t2", "Cnfdnc"]

	###########################################################################

	# Init Sigma
	SIG = stimuli.Sigma([FILL, TEXTURE, SHAPE], ["fill", "texture", "shape"], R, generation_mode = GENERATION_MODE)
	present_order = np.arange(len(SIG.sequences), dtype = int)
	seq_perms = [seq.permute() for seq in SIG.sequences]
	
	# Get input settings
	sub_code = input("Enter Subject code: ")
	while os.path.exists(DIRECTORY + sub_code):
		sub_code = input("Duplicate Subject code. Enter a new code again: ")
	os.makedirs(DIRECTORY + sub_code)
	DIRECTORY += sub_code + "/"
	conj_mode = input("Enter Formula Mode: ")
	while conj_mode not in ("B", "S", "P"):
		conj_mode = input("Incorrect Format; Enter Formula Mode Again: ")
	if conj_mode in ("S", "P"):
		conj_type = input("Enter Formula List: ")
		while conj_type not in ("A", "B", "C"):
			conj_type = input("Incorrect Format; Enter Formula List Again: ")
	if conj_mode == "B": 
		prod_conj = SIG.form_conjunct(Bool_Conj, conjunct_type = "Sum")
	if conj_mode == "S":
		prod_conj = SIG.form_conjunct(Sum_Conj[conj_type], conjunct_type = "Sum", subset_type = "==")
	if conj_mode == "P":
		prod_conj = SIG.form_conjunct(Prod_Conj[conj_type], conjunct_type = "Product")
	with open(DIRECTORY + "Sub_resp.csv", "a") as outfile:
		outfile.write("Subject code: " + sub_code + "\n")
		outfile.write("Formula mode: " + conj_mode + "\n")
		if conj_mode in ("S", "P"):
			outfile.write("Formula List: " + conj_type)
		outfile.write("\n")
		outfile.write("\t".join(HEADER))
		outfile.write("\n")
	# print(sub_code)
	# print(prod_conj.hierarchical_rep())
	# print("Solution Cardinality: ", len(list(SIG.satisfies(prod_conj))))

	###########################################################################
	
	# Presentation Settings
	WIN = visual.Window([1728, 1117], monitor="testMonitor", units="deg", fullscr = True, useRetina = True)
	OBJ_DICT = {
		2: visual.ImageStim(WIN, "rsc/rdc.png"),
		3: visual.ImageStim(WIN, "rsc/rdt.png"),
		5: visual.ImageStim(WIN, "rsc/rsc.png"),
		7: visual.ImageStim(WIN, "rsc/rst.png"),
		11: visual.ImageStim(WIN, "rsc/bdc.png"),
		13: visual.ImageStim(WIN, "rsc/bdt.png"),
		17: visual.ImageStim(WIN, "rsc/bsc.png"),
		19: visual.ImageStim(WIN, "rsc/bst.png")
	}
	OBJ_LINSPACE = np.arange(-8, 9, 8)
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
	
	# Starters
	starter_win(WIN, disp_objs)
	block_seq = []
	present_order = np.random.permutation(present_order)
	for ind in present_order: block_seq.append(next(seq_perms[ind]))
	repeat_flag = True
	while repeat_flag:
		repeat_flag = test_block(WIN, OBJ_DICT, TRIAL_OBJ_DICT, block_seq[:3], prod_conj, OBJ_LINSPACE, disp_objs)
	core.wait(1)
	# restart the generator
	present_order = np.arange(len(SIG.sequences), dtype = int)
	seq_perms = [seq.permute() for seq in SIG.sequences]
	
	# Start Blocks
	test_disp_start = visual.TextBox2(WIN, "Training Block", alignment = 'center', letterHeight = 1)
	cont_disp0 = visual.TextBox2(WIN, "Press any key to start",pos = (0, -3), alignment = 'center', letterHeight = 0.8)
	test_disp_end = visual.TextBox2(WIN, "This is the end of Test block.", pos = [0,0], alignment = 'center', letterHeight = 1)
	cont_disp1 = visual.TextBox2(WIN, "Press space/return to proceed to Block 1\nPress R to repeat the Training block", pos = (0,-3), letterHeight = 0.8, alignment = 'center')

	for repeat in range(6):
		block_seq = []
		present_order = np.random.permutation(present_order)
		block_disp_start = visual.TextBox2(WIN, "Block " + str(repeat + 1) + ".", alignment = 'center', letterHeight = 1)
		block_disp_end = visual.TextBox2(WIN, "This is the end of block " + str(repeat + 1) + ".", alignment = 'center', letterHeight = 1)
		cont_disp0 = visual.TextBox2(WIN, "Press any key to start",pos = (0, -3), alignment = 'center', letterHeight = 0.8)	
		cont_disp1 = visual.TextBox2(WIN, "Press any key to continue",pos = (0, -3), alignment = 'center', letterHeight = 0.8)	
		for ind in present_order: block_seq.append(next(seq_perms[ind]))
		block_rsp = block(WIN, repeat+1, [block_disp_start, cont_disp0], [block_disp_end, cont_disp1], OBJ_DICT, TRIAL_OBJ_DICT, block_seq[:2], prod_conj, OBJ_LINSPACE, disp_objs)
		with open(DIRECTORY + "Sub_resp.csv", "a") as outfile:
			for rind in range(len(block_rsp)):
				outfile.write("\t".join(block_rsp[rind].astype(str)))
				outfile.write("\n")
		# record_file(DIRECTORY, SUB_NAME + "_block" + str(repeat + 1), HEADER2, block_rsp)
	end_win(WIN, [])

	WIN.close()
	return

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
	starter_msg1 = visual.TextBox2(win,"      You are a newly employed physicists in the Deep Rock Corporate, and are assigned to the F-302 lab to investigate a group of exotic objects. The objects resemble simple geometric shapes and are otherwise unimpressive. However, eariler report indicates that these objects contain tremendous amount of energy, but will only release the energy (through an explosion) when they are arranged in a certain confirguation with other objects. Previous research in the lab had built up an experimental setup that uses disposable robots to arrange the objects, so one can comfortably observe the explosions in your control room. \n\n      In this experiment, you will see a configuration of objects at a time and observe whether they discharge energy through an explosion. The scope of investigation is limited to a 3-object configuration, with 8 types of objects that vary in their fill (red or blue), shape (triangle or circle), and texture (dotted or slashed). Your job is to go through these observations and deduce the correct and minimal configuration that will cause an explosion. Since Deep Rock Corporate only keeps extremely productive members on board, you will be prompted to give a prediction before the configuration is physically placed, and the company will evaluate your performance basing on your prediction accuracy. At the end of the experiment, you are also required to write an report about the minimal configuration that you think is correct.", pos = (0,-2), size = [40, None], alignment = 'left', letterHeight = 0.7)
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [starter_msg0, starter_msg1] + disp_objs)
	core.wait(0.4)
	
	test_msg = visual.TextBox2(win, "Before officially starting the experiment, let's do some test trials so that you understand the procedure.", pos = (0,0), size = [30, None], letterHeight = 0.8, alignment = "left")
	spec_cont(win, ABORT_KEY, PROCEED_KEYS, [test_msg] + disp_objs)
	core.wait(0.4)
	return

def test_block(win, obj_dict, trial_obj_dict, sequences, formula, obj_linspace, disp_objs = []):
	test_disp_start = visual.TextBox2(win, "Training Block", alignment = 'center', letterHeight = 1)
	cont_disp0 = visual.TextBox2(win, "Press any key to start",pos = (0, -3), alignment = 'center', letterHeight = 0.8)
	any_cont(win, ABORT_KEY, [test_disp_start, cont_disp0])

	total_rsp = np.empty((len(sequences), 6), dtype = object)
	for ind, seq in enumerate(sequences):
		curr_disp_objs = disp_objs.copy()
		trial_counter = visual.TextBox2(win, "Trial " + str(ind + 1) + " out of " + str(len(sequences)) + ".", pos = [0,13], alignment = 'center', letterHeight = 0.7)
		curr_disp_objs.append(trial_counter)
		total_rsp[ind] = trial(win, obj_dict, trial_obj_dict, seq, formula, obj_linspace, curr_disp_objs)
		core.wait(0.4)
	
	test_disp_end = visual.TextBox2(win, "This is the end of Test block.", pos = [0,0], alignment = 'center', letterHeight = 1)
	cont_disp1 = visual.TextBox2(win, "Press space/return to proceed to Block 1\nPress R to repeat the Training block", pos = (0,-3), letterHeight = 0.8, alignment = 'center')
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

def block(win, block_num, block_disp_start, block_disp_end, obj_dict, trial_obj_dict, sequences, formula, obj_linspace, disp_objs = []):
	any_cont(win, ABORT_KEY, block_disp_start)
	core.wait(0.4)

	total_rsp = np.empty((len(sequences), 7), dtype = object)
	total_rsp[:, 0] = block_num
	for ind, seq in enumerate(sequences):
		curr_disp_objs = disp_objs.copy()
		trial_counter = visual.TextBox2(win, "Trial " + str(ind + 1) + " out of " + str(len(sequences)) + ".", pos = [0,13], alignment = 'center', letterHeight = 0.7)
		curr_disp_objs.append(trial_counter)
		total_rsp[ind, 1:] = trial(win, obj_dict, trial_obj_dict, seq, formula, obj_linspace, curr_disp_objs)
		core.wait(0.4)
	
	any_cont(win, ABORT_KEY, block_disp_end)
	core.wait(0.8)
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

def trial(win, obj_dict, trial_obj_dict, Sequence, formula, obj_linspace, disp_objs = []):
	# Initialize Objects
	# print(Sequence.hierarchical_rep())
	win_objs = []
	seq_rep = ""
	for obj in Sequence.objects:
		seq_rep += str(obj.id) + "; "
	seq_rep = seq_rep[:-2]

	for ind, obj in enumerate(Sequence.objects):
		curr_obj = obj_dict[obj.id]
		curr_obj.pos = [obj_linspace[ind], 0]
		win_objs.append(curr_obj)
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

	# Actual trial
	while True:
		# Drawing
		for obj in win_objs: obj.draw()
		for obj in disp_objs: obj.draw()
		prompt_msg.draw()
		win.flip(clearBuffer = False)

		start_time = time.time()
		# Prompt user response
		curr_rsp = None
		while curr_rsp is None:
			allKeys = event.waitKeys()
			for thisKey in allKeys:
				if thisKey == "q": exit("Experiment Aborted")
				if thisKey == "t":
					true_usr.draw()
					curr_rsp = True
					end_time = time.time()
					break
				if thisKey == "f":
					fals_usr.draw()
					curr_rsp = False
					end_time = time.time()
					break		
		trial_rsp = curr_rsp
		if curr_rsp == ground_truth: 
			Correct_sound.play()
			Correct_text.draw()
		else: 
			Incorrect_sound.play()
			Incorrect_text.draw()
		rspt_1 = end_time - start_time
		event.clearEvents()

		# Update window
		for obj in win_objs: obj.draw()
		for obj in disp_objs: obj.draw()
		prompt_msg.draw()
		response_msg.draw()
		if ground_truth == True: true_rsp.draw()
		else: fals_rsp.draw()
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

		win.flip()
		win.flip()
		event.clearEvents()
		break

	core.wait(0.2)
	# Confidence Ratings
	while ratingScale.noResponse:
		ratingScale.draw()
		for obj in disp_objs: obj.draw()
		win.flip()
	rating = ratingScale.getRating()
	win.flip()
	event.clearEvents()

	return [seq_rep, trial_rsp, ground_truth, rspt_1, rspt_2, rating]

if __name__ == "__main__":
	main()

