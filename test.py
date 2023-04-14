import numpy as np
import itertools

fill = ["red", "blue"]
shape = ["circle", "triangle"]
texture = ["dotted", "slashed"]

def main():
	# Sigma = [fill, shape, texture]
	# combinations = cart_prod(Sigma, 2)
	# formula = ["red", "circle", "dotted"]
	Sigma = [fill, shape]
	combinations = cart_prod(Sigma, 2)
	formula = ["red", "circle"]
	eval_res = set_verify(formula, combinations)
	print(sum(eval_res))
	sol = combinations[eval_res]
	for s in sol: print(s)
	return

def cart_prod(Sigma, num_ob):
	object_set = list(itertools.product(*Sigma))
	ob_list = []
	for i in range(num_ob): 
		ob_list.append(object_set)
	combinations = np.array(list(itertools.product(*ob_list)))
	return combinations

def set_verify(formula, combinations):
	formula = set(formula)
	res = np.zeros(combinations.shape[0], dtype = bool)
	for pres_ind in range(len(res)):
		curr_pres = combinations[pres_ind]
		res[pres_ind] = formula.issubset(curr_pres.flatten())
	return res

if __name__ == "__main__":
	main()
