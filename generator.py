import numpy as np
from itertools import product, combinations, permutations
import stimuli

fill = ["red", "blue"]
shape = ["circle", "triangle"]
texture = ["dotted", "slashed"]


'''
Formula Style:
	Boolean       : ["feature", "feature", "feature", "feature"]
	Counting      : {"feature": x, "feature": y, "feature": z}
	Combinatorial : [["feature", "feature"], ["feature", "feature"]]

Specificity Style:
	Boolean       : 2
	Counting      : [2,1,3] (elems specify feature)
	Combinatorial : [3,2,1] (elems specify object)
'''

def main():
	
	# generator = generate(4,3)
	# for s in generator: print(s)
	# return

	# A = ["a1", "a2", "a3", "a4"]
	# B = ["b1", "b2", "b3"]
	# C = ["c1", "c2", "c3"]

	# objects = generate_list(2, A, B)
	# counter = 0
	# for obj in objects:
	# 	print(obj)
	# 	counter += 1
	# print(counter)

	# # for s in generate(3,2): print(s)
	# # print(generate_counting_formula([2,3,0], fill, shape, texture))
	print(len(list(generate(6,3))))
	return

	print("Boolean Formula")
	print("------------------------------------------------------------------")
	boolean_specificity = np.arange(7)
	for spec in boolean_specificity:
		formula = generate_boolean_formula(spec, fill, shape, texture)
		# solutions = verify_boolean_formula(formula, combinations(product(fill, shape, texture), 3))
		# solutions = verify_boolean_formula(formula, permutations(product(fill, shape, texture), 3))
		solutions = verify_boolean_formula(formula, generate_list(3, fill, shape, texture))
		# solutions = verify_boolean_formula(formula, product(product(fill, shape, texture), product(fill, shape, texture), product(fill, shape, texture)))
		print("Specificity:", spec, "; solution size:", len(solutions))

	# print("Multiset Combination")
	# print("------------------------------------------------------------------")
	# sig = stimuli.Sigma([fill, shape, texture], ["fill", "shape", "texture"], 3, generation_mode = "Multiset Combination")
	# print("Boolean Formula: ")
	# specificity = np.arange(7, dtype = int)
	# for spec in specificity:
	# 	conjunct = sig.generate_conjuncts(spec, conjunct_type = "boolean")
	# 	print(conjunct)
	# 	# solutions = sig.satisfies(conjunct)
	# 	# print("\tSpecificity:", spec, "; solution size:", len(solutions))

	print("Combination")
	print("------------------------------------------------------------------")
	sig = stimuli.Sigma([fill, shape, texture], ["fill", "shape", "texture"], 3, generation_mode = "Multiset Combination")
	print("Boolean Formula: ")
	specificity = np.arange(7, dtype = int)
	for spec in specificity:
		conjunct = sig.generate_conjuncts(spec, conjunct_type = "boolean")
		solutions = sig.satisfies(conjunct)
		print("\tSpecificity:", spec, "; solution size:", len(solutions))

	# print("Counting Formula")
	# print("------------------------------------------------------------------")
	# counting_specificity = generate(4,3, constructor = list)
	# for spec in counting_specificity:
	# 	formula = generate_counting_formula(spec, fill, shape, texture)
	# 	solutions = verify_counting_formula(formula, generate_list(3, fill, shape, texture))
	# 	print("Specificity:", spec, "; solution size:", len(solutions))

	# # formula = {"circle": 2, "blue": 1}
	# # solutions = verify_counting_formula(formula, generate_list(3, fill, shape, texture))
	# # print("solution size:", len(solutions))

	# print("Combinatorial Formula")
	# print("------------------------------------------------------------------")
	# combinatorial_specificity = generate(4,3, constructor = list)
	# for spec in combinatorial_specificity:
	# 	formula = generate_combinatorial_formula(spec, fill, shape, texture)
	# 	solutions = verify_combinatorial_formula(formula, generate_list(3, fill, shape, texture))
	# 	print("Specificity:", spec, "; solution size:", len(solutions))

	# formula = [["red", "triangle"], ["slashed"]]
	# solutions = verify_combinatorial_formula(formula, generate_list(3, fill, shape, texture))
	# print("solution size:", len(solutions))

	# test_list = [
	# 		(('red', 'circle', 'dotted'), ('red', 'circle', 'dotted'), ('blue', 'circle', 'dotted')), 
	# 		(('red', 'circle', 'dotted'), ('blue', 'circle', 'dotted'), ('blue', 'circle', 'slashed')),
	# 		(('red', 'circle', 'dotted'), ('blue', 'circle', 'slashed'), ('blue', 'circle', 'dotted'))
	# 	]
	
	# formula = [["red", "circle", "slashed"], ["blue", "triangle", "dotted"], ["red"]]
	# solutions = verify_combinatorial_formula(formula, generate_list(3, fill, shape, texture))
	# print("Combinatorial Formula:", formula)
	# for s in solutions: print(s)
	# print("Solution Set Size:", len(solutions))

	# formula = [["red", "circle"], ["dotted", "blue"]]
	# solutions = verify_combinatorial_formula(formula, generate_list(3, fill, shape, texture))
	# print("Combinatorial Formula:", formula)
	# print("Solution Set Size:", len(solutions))

	# formula = {"blue": 1, "slashed": 1}
	# solutions = verify_counting_formula(formula, generate_list(3, fill, shape, texture))
	# print("Counting Formula:", formula)
	# print("Solution Set Size:", len(solutions))
	# print("------------------------------------------------------------------")

	# formula = ["red", "blue", "circle", "triangle", "dotted", "slashed"]
	# solutions = verify_boolean_formula(["red", "blue", "circle", "triangle", "dotted", "slashed"], generate_list(3, fill, shape, texture))
	# print("Boolean Formula:", formula)
	# print("Solution Set Size:", len(solutions))
	# print("------------------------------------------------------------------")
	# return

def generate_combinatorial_formula(specificity, *features):
	features = [*features]
	if max(specificity) > len(features): raise RuntimeError("The number of features included is insufficient to specify the given specificity")
	formula = []
	for obj_i, obj_spec in enumerate(specificity):
		np.random.shuffle(features)
		if obj_spec == 0: 
			formula.append([])
		else:
			obj_formula = []
			for i in range(obj_spec):
				obj_formula.append(np.random.choice(features[i]))
			formula.append(obj_formula)
	return formula

def generate_counting_formula(specificity, *features):
	features = [*features]
	if len(specificity) > len(features): raise RuntimeError("The number of features included is insufficient to specify the given specificity")	
	formula = {}
	for feature_i, feature_spec in enumerate(specificity):
		if feature_spec != 0:
			# Generate all possible feature states configs
			feature_config = []
			curr_feature = features[feature_i]
			for s_config in product(*np.repeat(np.arange(feature_spec + 1).reshape(1, -1), len(curr_feature), axis = 0)):
				if sum(s_config) == feature_spec: feature_config.append(s_config)
			# choose a config
			curr_config = feature_config[np.random.choice(np.arange(len(feature_config)))]
			for fs, c in zip(curr_feature, curr_config):
				if c != 0: formula.update({fs:c})
	return formula
	
def generate_boolean_formula(specificity, *features):
	feature_pool = []
	for f in features:
		for fs in f:
			feature_pool.append(fs)
	return np.array(feature_pool)[np.random.choice(len(feature_pool), size = specificity, replace = False)]

def generate(n, r, constructor = tuple):
	"""Generate sets of size r from sample space of n elements"""
	indices = [0] * r

	yield constructor(indices)
	while True:
		# find the right-most index that does not reach the end
		for i in reversed(range(r)):
			if indices[i] != n - 1:
				break
		else:
			# if all indices are n - 1, done
			return
		# e.g. if n = 3, (0, 1, 2) --> (0, 2, 2)
		indices[i:] = [indices[i] + 1] * (r - i)
		yield constructor(indices)

def generate_list(r, *features):
	vectors = tuple(product(*features))
	for indices in generate(len(vectors), r):
		yield tuple(vectors[i] for i in indices)

def verify_boolean_formula(formula, generator):
	formula = set(formula)
	solutions = []
	for s in generator:
		s_set = np.array(s).flatten()
		if formula.issubset(s_set):
			solutions.append(s)
	return solutions

def verify_counting_formula(formula, generator):
	solutions = []
	for s in generator:
		s_arr = np.array(s).flatten()
		s_count = dict(zip(*np.unique(s_arr, return_counts = True)))
		solve_flag = False
		for feature in formula:
			try:
				object_c = s_count[feature]
				if object_c >= formula[feature]: 
				# if object_c == formula[feature]: 
					solve_flag = True
				else:
					solve_flag = False
					break
			except KeyError: 
				if formula[feature] == 0:
					solve_flag = True
				else:
					solve_flag = False
					break
		if solve_flag == True or len(formula) == 0:
			solutions.append(s)
	return solutions

def verify_combinatorial_formula(formula, generator):
	formula = [set(obj_f) for obj_f in formula]
	solutions = []
	counter = 1
	for s in generator:
		s_list = [set(obj) for obj in s]
		solve_flag = recur_verify_obj__(formula.copy(), s_list.copy())
		if solve_flag == True: solutions.append(s)
	return solutions

# def verify_objects__(formula, s_list):
# 	formula = formula.copy()
# 	# While there's still terms in the formula
# 	while len(formula) > 0:
# 		for obj_i, obj_f in enumerate(formula):
# 			# There's no object to match any term
# 			if len(s_list) == 0: return False
# 			solve_flag = False
# 			for ind, obj in enumerate(s_list):
# 				# When an object match the term
# 				if obj_f.issubset(obj):
# 					s_list.pop(ind)
# 					formula.pop(obj_i)
# 					solve_flag = True 
# 					break
# 			# When no object satisfy a term
# 			if solve_flag == False:
# 				return False
# 	# When all terms have been met
# 	return True

def recur_verify_obj__(formula, s_list):
	# success: all term have been matched
	if len(formula) == 0: return True
	# failure: no term to be matched
	if len(s_list) == 0: return False

	# normal recursive operations
	match_list = []
	# for each term
	for obj_i, obj_f in enumerate(formula):
		# for each object
		for ind, obj in enumerate(s_list):
			# a term is matched
			if obj_f.issubset(obj):
				# we start one branch in searching because we cannot
				# gaurentee that we should match this object with this term
				branch_formula = np.delete(formula, obj_i)
				branch_s_list = np.delete(s_list, ind)
				match_list.append(recur_verify_obj__(branch_formula, branch_s_list))
	# failure: no term find a matching object
	if len(match_list) == 0 or sum(match_list) == 0:
		return False
	else:
		return True

if __name__ == "__main__":
	main()