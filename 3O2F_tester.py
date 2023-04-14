import numpy as np
from itertools import product 

import stimuli


fill = ["red", "blue"]
shape = ["circle", "triangle"]

bool_config_tab = {
	2: [1,1],
	1: [1],
	0: [0]
}

sum_config_tab = {
	5: [3],
	4: [2,1],
	3: [2],
	2: [1,1],
	1: [1],
	0: [0]
}

prod_obj = product([[0,1],[1,0],[0,0]], [[0,1],[1,0],[0,0]])
all_obj = []
for prod in prod_obj: all_obj.append(list(prod))
prod_config_tab = {}
for ind, prod in enumerate(all_obj):
	prod_config_tab.update({ind: prod})

print("Combination")
print("------------------------------------------------------------------")
sig = stimuli.Sigma([fill, shape], ["fill", "shape"], 3, generation_mode = "Combination")
print(len(sig.sequences))
# for seq in sig.sequences: print(seq.hierarchical_rep())
# exit()

form_generator = stimuli.multiset_comb(len(sum_config_tab), 2)
res_dict = {}
for formula in form_generator:
	curr_spec = []
	for config_id in formula:
		curr_spec.append(sum_config_tab[config_id])
	curr_conj = sig.form_conjunct(curr_spec, conjunct_type = "Sum", subset_type = "==")
	card_sate = len(list(sig.satisfies(curr_conj)))
	if card_sate in res_dict: 
		res_dict[card_sate].append(curr_spec)
	else:
		res_dict.update({card_sate: [curr_spec]})
with open("Complexity_Sum.txt", 'w') as outfile:
	outfile.write("Summation Complexity:\n")
	for card_sate in sorted(res_dict.keys()):
		outfile.write("  - " + str(card_sate) + "\n")
		for spec in res_dict[card_sate]: 
			outfile.write("    " + str(spec) + "\n")
	# for spec in res_dict[card_sate]: 
	# 	print("    " + str(spec))
exit()

test_conj1 = stimuli.Conjunct({("fill", "red"):2, ("shape", "circle"):1, ("texture", "dotted"):2})
test_conj2 = stimuli.Conjunct({("fill", "red"):1, ("fill", "blue"):1, ("shape", "circle"):1, ("texture", "dotted"):1, ("texture", "slashed"):1})

print(test_conj1.hierarchical_rep())
print(test_conj2.hierarchical_rep())
exit()
print("---------------------------------------------")
counter = 0
for seq in sig.sequences:
	print(seq.hierarchical_rep(level = "Feature"))
	print("satisfies: ", str(seq.satisfies(test_conj2)))
	if seq.satisfies(test_conj2): counter += 1
	print("")
print("total count " + str(counter))

# for seq in sig.sequences: print(seq.hierarchical_rep())

# test_seq = sig.sequences[2]
# for perm in test_seq.permute(unique = False): print(perm)

# for form in sig.generate_conjuncts([2,2,1], conjunct_type = "sum"):
# 	print(form.hierarchical_rep())
# 	print(len(sig.satisfies(form)))
# 	print("")


exit()