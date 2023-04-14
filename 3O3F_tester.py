import numpy as np
from itertools import product 

import stimuli

# Presentation Settings
image_dict = {
	2: "rsc/rdc.png",
	3: "rsc/rdt.png",
	5: "rsc/rsc.png",
	7: "rsc/rst.png",
	11: "rsc/bdc.png",
	13: "rsc/bdt.png",
	17: "rsc/bsc.png",
	19: "rsc/bst.png"
}

fill = ["red", "blue"]
shape = ["circle", "triangle"]
texture = ["dotted", "slashed"]

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

prod_obj = product([[0,1],[1,0],[0,0]], [[0,1],[1,0],[0,0]], [[0,1],[1,0],[0,0]])
all_obj = []
for prod in prod_obj: all_obj.append(list(prod))
prod_config_tab = {}
for ind, prod in enumerate(all_obj):
	prod_config_tab.update({ind: prod})

print("Combination")
print("------------------------------------------------------------------")
sig = stimuli.Sigma([fill, texture, shape], ["fill", "texture", "shape"], 3, generation_mode = "Combination")
print(len(sig.sequences))
form_generator = stimuli.multiset_comb(len(prod_config_tab), 3)
res_dict = {}
for formula in form_generator:
	curr_spec = []
	for config_id in formula:
		curr_spec.append(prod_config_tab[config_id])
	curr_conj = sig.form_conjunct(curr_spec, conjunct_type = "Product", subset_type = ">=")
	card_sate = len(list(sig.satisfies(curr_conj)))
	if card_sate in res_dict: 
		res_dict[card_sate].append(curr_spec)
	else:
		res_dict.update({card_sate: [curr_spec]})
with open("Complexity_Prod.txt", 'w') as outfile:
	outfile.write("Product Complexity:\n")
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
print("Boolean Formula: ")
specificity = np.arange(7, dtype = int)
for spec in specificity:
	conjunct = sig.generate_conjuncts(spec, conjunct_type = "boolean")
	solutions = sig.satisfies(conjunct)
	print("\tSpecificity:", spec, "; solution size:", len(solutions))


# seqs = test_Sigma.populate(3, generation_mode = "Combination")
# print("Combination:", len(seqs))
# seqs = test_Sigma.populate(3, generation_mode = "Permutation")
# print("Permutation:", len(seqs))
# seqs = test_Sigma.populate(3, generation_mode = "Multiset Combination")
# print("Multiset Combination:", len(seqs))
# formula = stimuli.Conjunct({("shape", "circle"): 2, ("fill", "blue"): 1})
# counter = 0
# for seq in seqs:
# 	if seq.satisfies(formula): counter += 1
# print(counter)

# print("Multiset Combination:", len(seqs))
# formula = stimuli.Conjunct([{("fill", "red"): 1, ("shape", "triangle"): 1}, {("texture", "slashed"): 1}])
# counter = 0
# for seq in seqs:
# 	if seq.satisfies(formula): counter += 1
# print(counter)

# seqs = test_Sigma.populate(3, generation_mode = "Multiset Permutation")
# print("Multiset Permutation:", len(seqs))

# Testing the formula satisfaction


## Testing the symmetry of generated sequences
# f_sum = []
# o_sum = []
# for seq in seqs:
# 	f_sum += seq.summarize(level = "Feature")
# 	o_sum.append(seq.summarize(level = "Object"))
# f_dict = stimuli.merge_dicts(*f_sum)
# o_dict = stimuli.merge_dicts(*o_sum)
# print("Objects")
# for k in o_dict:
# 	print("\t", k, ":", o_dict[k])
# print("Features")
# for k in f_dict:
# 	print("\t", k, ":", f_dict[k])

# print(seqs[0].encodings)
# print(seqs[0].abrv_encodings)

# print("----")
# print(seqs[0].summarize(level = "Object"))
# print(seqs[0].summarize(level = "Feature"))
# print("----")

# obj = seqs[0][0]
# print(obj)
# print(obj.contains([("fill", "red"), ("shape", "square"), ("texture", "dotted")]))
# print(obj.encoding)
# print(obj.abrv_encoding)



# obj1 = seqs[0][0]
# obj2 = seqs[20][1]
# print(obj2)
# obj3 = stimuli.Object(2, (('fill', 'red'), ('shape', 'circle'), ('texture', 'dotted')))

# print(obj1 == obj2)
# print(obj1 == obj3)
# print(obj1.__hash__())
# print(obj2.__hash__())
# print(obj3.__hash__())

# test_dict = {obj1: 1, obj2: 2}
# print(test_dict)
# print(test_dict[obj3])

# print(seqs[0])
# print(seqs[0].cid)
# print(seqs[0].pid)
# print(seqs[0].cequal(seqs[0]))
# print(seqs[0].cequal(seqs[1]))
# print(seqs[0].pequal(seqs[0]))
# print(seqs[0].pequal(seqs[1]))
# print(seqs[0] == seqs[0])
# print(seqs[0][1])
# for obj in seqs[0]: print(obj)
# print(seqs[0][1] in seqs[0])
# print(seqs[1][2] in seqs[0])

# print("-----")
# perm_seq = seqs[0].permute()
# for seq in perm_seq:
# 	print(seqs[0])
# 	print(seq)
# 	print(seqs[0].cequal(seq))
# 	print(seqs[0].pequal(seq))
# 	print("--")

# print(objs)
# print(set([objs[0], objs[0], objs[1]]))
# print(np.unique(objs[:2], return_counts = True, axis = 0))
# print(objs[0])
# print(objs[1])

# testseq_1 = stimuli.Sequence([objs[0], objs[1], objs[0]])
# for seq in testseq_1.permute(): print(seq)
# print("")
# testseq_2 = stimuli.Sequence(objs[:3])
# for seq in testseq_2.permute(): print(seq)

# a = list(stimuli.unique_perm([1,2], [2,1], [0]*3, 2))
# print(a)

# a = list(stimuli.perm_unique([1,1,2]))
# print(a)

# obj = objs[1]
# print(obj)
# print(len(obj))
# print(obj["fill"])
# for fs in obj: print(fs)
# # print(("fill", "red") in obj)
# print(obj.contains([()]))
# print(obj.contains([("fill", "red"), ("shape", "triangle"), ("texture", "slashed")]))