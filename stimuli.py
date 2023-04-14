import numpy as np
import random
from itertools import product, combinations, permutations

class Object():
	def __init__(self, identity, encoding):
		self.id = None
		self.encoding = None
		self.abrv_encoding = None

		self.__initialize(identity, encoding)

	def contains(self, f_state):
		if type(f_state) is tuple: return self.__contains__(f_state)
		res = np.zeros((len(f_state), len(self.encoding)), dtype = bool)
		for ind, f_s in enumerate(f_state): 
			res[ind, :] = self.__contains__(f_s)
		return res

	def summarize(self):
		res_dict = {}
		for enc in self.encoding:
			if enc in res_dict: res_dict[enc] += 1
			else: res_dict.update({enc: 1})
		return res_dict

	def hierarchical_rep(self):
		repr_str = "Obj " + str(self.id) + "\n"
		repr_str += hierarchical_rep(self.summarize(), base_indent = "  ") + "\n"
		return repr_str[:-1]

	def __getitem__(self, key):
		res = []
		for f in self.encoding:
			if f[0] == key: res.append(f)
		return res

	def __len__(self):
		return len(self.encoding)

	def __iter__(self):
		return self.encoding.__iter__()

	def __contains__(self, key):
		if type(key) is not tuple: raise TypeError("The input key must be a tuple")
		# empty query is automatically true
		if len(key) == 0: return True
		res = np.zeros(len(self.encoding), dtype = bool)
		for ind, enc in enumerate(self.encoding):
			res[ind] = key == enc
		return res

	def __eq__(self, other):
		if isinstance(other, Object) == False: return False
		return self.id == other.id	
	def __ne__(self, other):
		return not self.__eq__(other)
	def __hash__(self):
		return hash(str(self.id))

	def __str__(self):
		return "Obj " + str(self.id) + " : " + self.encoding.__str__()

	def __repr__(self):
		return "Obj " + str(self.id)

	def __initialize(self, identity, encoding):
		if type(identity) is not int: raise TypeError("identity must be an int")
		self.id = identity
		self.encoding = encoding
		self.abrv_encoding = tuple((enc[1] for enc in self.encoding))

class Sequence():
	def __init__(self, objects):
		self.objects = None

		self.__cid = None
		self.__pid = None

		self.__initialize(objects)

	def cequal(self, other):
		if isinstance(other, Sequence) == False: raise TypeError("The input variable must be an instance of Sequence")
		return self.cid == other.cid

	def pequal(self, other):
		if isinstance(other, Sequence) == False: raise TypeError("The input variable must be an instance of Sequence")
		diff_arr = np.subtract(self.__pid, other.pid)
		# return not np.any(diff_arr)
		return diff_arr == 0

	def permute(self, unique = True):
		if unique == True:
			unique_elem = list(set(self.objects))
			counts = [self.objects.count(obj) for obj in unique_elem]
			perms = list(unique_perm(unique_elem, counts, [0]*len(self.objects), len(self.objects) - 1, constructor = Sequence))
			index = np.random.permutation(np.arange(len(perms)))
			for ind in index: yield perms[ind]
		elif unique == False:
			perms = list(permutations(self.objects, len(self.objects)))
			index = np.random.permutation(np.arange(len(perms)))
			for ind in index: yield perms[ind]
		# return [permutations[ind] for ind in index]
		# return unique_perm(unique_elem, counts, [0]*len(self.objects), len(self.objects) - 1, constructor = Sequence)

	def summarize(self, level = "Feature"):
		if level == "Object":
			res_dict = {}
			for obj in self.objects:
				if obj in res_dict: res_dict[obj] += 1
				else: res_dict.update({obj: 1})
			return res_dict
		if level == "Feature":
			sum_dicts = []	
			for obj in self.objects: sum_dicts.append(obj.summarize())
			return sum_dicts
		raise ValueError("Unaccepted level for summarize")

	def satisfies(self, conjunct):
		if isinstance(conjunct, Conjunct) == False: raise TypeError("The input Conjunct must be an instance of Conjunct")
		if conjunct.subset_type == "==": Sub_Func = subset_dicts_eq
		elif conjunct.subset_type == ">=": Sub_Func = subset_dicts_geq
		else: raise ValueError("The input subset_type must be either '==' or '>='.")
		if conjunct.conjunct_type == "Sum":
			f_dicts = self.summarize(level = "Feature")
			f_sum = merge_dicts(*f_dicts)
			return Sub_Func(conjunct.query, f_sum)
		if conjunct.conjunct_type == "Product":
			s_list = self.summarize(level = "Feature")
			formula = conjunct.query.copy()
			return recur_verify_obj(formula, s_list, Sub_Func)

	def hierarchical_rep(self, level = "Object"):
		repr_str = self.__repr__() + "\n"
		if level == "Feature":
			obj_dict = self.summarize(level = "Feature")
			obj_dict = merge_dicts(*obj_dict)
			repr_str += hierarchical_rep(obj_dict, base_indent = "  ")
			return repr_str
		if level == "Object":
			for obj in self.objects:
				repr_str += "  Obj " + str(obj.id) + "\n"
				repr_str += hierarchical_rep(obj.summarize(), base_indent = "    ") + "\n"
			return repr_str[:-1]

	def __eq__(self, other):
		if isinstance(other, Sequence) == False: return False
		return self.pid == other.pid
	def __ne__(self, other):
		return not self.__eq__(other)
	def __hash__(self):
		return hash(self.pid)

	def __getattr__(self, name):
		if name == "cid": return self.__cid
		if name == "pid": return tuple(self.__pid)
		if name == "encodings":
			encodings = []
			for obj in self.objects:
				encodings.append(obj.encoding)
			return tuple(encodings)
		if name == "abrv_encodings":
			abrv_encodings = []
			for obj in self.objects:
				abrv_encodings.append(obj.abrv_encoding)
			return tuple(abrv_encodings)			
		raise AttributeError("Unknown attribute " + name)

	def __getitem__(self, key):
		return self.objects[key]

	def __len__(self):
		return len(self.objects)

	def __iter__(self):
		return self.objects.__iter__()

	def __contains__(self, q_obj):
		if isinstance(q_obj, Object) == False: raise TypeError("The input variable must be an instance of Object")
		for obj in self.objects:
			match_flag = obj == q_obj
			if match_flag == True: return match_flag
		return False

	def __str__(self):
		repr_str = "Seq ("
		for obj in self.objects: repr_str += obj.__repr__() + ", "
		repr_str = repr_str[:-2] + ")"
		return repr_str

	def __repr__(self):
		return "Seq " + str(self.pid)

	def __initialize(self, objects):
		if len(objects) == 0: raise RuntimeError("The sequence must have a least 1 object")
		self.objects = tuple(objects)
		self.__pid = np.zeros(len(objects), dtype = int)
		for ind, obj in enumerate(self.objects):
			self.__pid[ind] = obj.id
		self.__cid = np.prod(self.__pid)
		return

class Sigma():
	def __init__(self, features, feature_names, r, generation_mode = "Multiset Combination"): 
		self.features = None
		self.cardinality = None
		self.objects = None
		self.sequences = None
		self.r = None
		self.generation_mode = None

		self.__feature_dict = None

		self.__initialize(features, feature_names, r, generation_mode)

	def summarize(self):
		all_states = []
		for f in self: all_states += f
		return all_states.copy()

	def satisfies(self, conjunct, return_non_solutions = False):
		solutions = []
		non_solutions = []
		for seq in self.sequences:
			if seq.satisfies(conjunct): 
				solutions.append(seq)
			else:
				non_solutions.append(seq)
		if return_non_solutions == False:
			return solutions
		else:
			return solutions, non_solutions

	def form_conjunct(self, abrv_defn, conjunct_type = "Sum", subset_type = ">="):
		if conjunct_type == "Bool": conjunct_type = "Sum"
		if conjunct_type == "Sum":
			conjunct_dict = {}
			for f_ind, f_spec in enumerate(abrv_defn):
				curr_feature = self[f_ind]
				for fs_ind, fs_spec in enumerate(f_spec):
					if fs_spec > 0: conjunct_dict.update({curr_feature[fs_ind]: fs_spec})
			return Conjunct(conjunct_dict, subset_type)
		if conjunct_type == "Product":
			conjunct_list = []
			for obj_config in abrv_defn:
				conjunct_dict = {}
				for f_ind, f_spec in enumerate(obj_config):
					curr_feature = self[f_ind]
					for fs_ind, fs_spec in enumerate(f_spec):
						if fs_spec > 0: conjunct_dict.update({curr_feature[fs_ind]: fs_spec})
				conjunct_list.append(conjunct_dict)
			return Conjunct(conjunct_list, subset_type)

	def generate_conjuncts(self, conjunct_type = "Product", subset_type = ">="):
		all_conjuncts = []
		if conjunct_type == "Bool":
			full_config_gen = self.__generate_object_conj(2)
		elif conjunct_type == "Sum":
			full_config_gen = self.__generate_object_conj(self.r + 1)
		elif conjunct_type == "Product":
			obj_conj = list(self.__generate_object_conj(2))
			full_config_gen = product(*[obj_conj]*self.r)
		else: raise KeyError
		for full_config in full_config_gen:
			all_conjuncts.append(self.form_conjunct(full_config, conjunct_type = conjunct_type, subset_type = subset_type))
		return all_conjuncts

	def __generate_object_conj(self, max_config):
		f_configs = []
		for feature in self:
			curr_configrange = list(range(max_config))
			all_config = [curr_configrange]*len(feature)
			config_gen = product(*all_config)
			curr_f = []
			for config in config_gen:
				if sum(config) <= self.r: curr_f.append(config)
			f_configs.append(curr_f)
		full_config_gen = product(*f_configs)
		return full_config_gen

	def fully_permute_sequences(self, sequences = None):
		if sequences is None: sequences = self.sequences
		full_seq = []
		for seq in sequences:
			for seq_perm in seq.permute(): full_seq.append(seq_perm)
		random.shuffle(full_seq)
		return full_seq

	def __generate_config_space(self, specificity):
		fs_configs = []
		for feature_i, feature_spec in enumerate(specificity):
			curr_config = []
			curr_feature = self[feature_i]
			if feature_spec > len(curr_feature): raise RuntimeError("The given specificity at pos " + str(feature_i) + " exceeds the cardinality of the corresponding feature.")
			if feature_spec > 0:
				for s_config in product(*np.repeat(np.arange(feature_spec + 1).reshape(1, -1), len(curr_feature), axis = 0)):
					if sum(s_config) == feature_spec: 
						curr_config.append(s_config)
			fs_configs.append(curr_config)
		return product(*fs_configs)

	def __getitem__(self, key):
		if key is None: return np.array([])
		if type(key) is str:
			try:
				return self.__feature_dict[key]
			except KeyError:
				raise KeyError("The key " + key + " is undefined.")
		if type(key) is int:
			return self.__feature_dict[self.features[key]]
		raise TypeError("The input key must be a str")

	def __len__(self):
		return len(self.features)

	def __iter__(self):
		for key in self.features:
			yield self.__feature_dict[key]

	def __contains__(self, key):
		return key in self.__feature_dict

	def __initialize(self, features, feature_names, r, generation_mode):
		self.features = []
		self.cardinality = []
		self.__feature_dict = {}
		self.r = r
		self.generation_mode = generation_mode
		
		for f, f_name in zip(features, feature_names):
			self.features.append(f_name)
			f_list = []
			for f_s in f:
				f_list.append((f_name, f_s))
			self.__feature_dict.update({f_name: f_list})
			self.cardinality.append(len(f))

		self.features = tuple(self.features)
		self.cardinality = tuple(self.cardinality)

		self.objects = self.__generate_objects()
		self.sequences = self.__populate(r, generation_mode)
		
	def __populate(self, r, generation_mode = "Multiset Combination"):
		sequences = []
		if generation_mode == "Combination":
			seqs = combinations(self.objects, r)
			for seq in seqs:
				sequences.append(Sequence(seq))
			return sequences
		if generation_mode == "Permutation":
			seqs = permutations(self.objects, r)
			for seq in seqs:
				sequences.append(Sequence(seq))
			return sequences
		if generation_mode == "Multiset Combination":
			for indices in multiset_comb(len(self.objects), r):
				seq = tuple(self.objects[i] for i in indices)
				sequences.append(Sequence(seq))
			return sequences
		if generation_mode == "Multiset Permutation":
			for indices in multiset_perm(len(self.objects), r):
				seq = tuple(self.objects[i] for i in indices)
				sequences.append(Sequence(seq))
			return sequences
		
		raise ValueError("Unaccepted generation_mode for populate")

	def __generate_objects(self):
		feature_arrs = []
		for f in self: feature_arrs.append(f)
		obj_arrs = []
		primes = get_primes()
		for encoding in product(*feature_arrs):
			obj_id = next(primes)
			obj_arrs.append(Object(obj_id, encoding))
		return obj_arrs

class Conjunct():
	def __init__(self, query, subset_type = ">="):
		self.query = None
		self.conjunct_type = None
		self.subset_type = None

		self.___initialize(query, subset_type)

	def ___initialize(self, query, subset_type):
		if type(query) is dict:
			self.conjunct_type = "Sum"
		elif type(query) is list:
			for q_dict in query:
				if type(q_dict) is not dict:
					raise TypeError("If the query is a list, its element must be dicts")
			self.conjunct_type = "Product"
		else:
			raise TypeError("The input query must be a dict or a list of dicts")
		self.query = query
		if subset_type not in (">=", "=="): raise ValueError("The input subset_type must be either '==' or '>='.")
		self.subset_type = subset_type 

	def hierarchical_rep(self, feature_order = None):
		if self.conjunct_type == "Sum":
			repr_str = "Sum Conjunct\n"
			repr_str += hierarchical_rep(self.query, base_indent = "  ", key_order = feature_order)
			return repr_str
		if self.conjunct_type == "Product":
			repr_str = "Product Conjunct\n"
			for ind, obj_dict in enumerate(self.query):
				repr_str += "  Object " + str(ind) + "\n"
				repr_str += hierarchical_rep(obj_dict, base_indent = "    ", key_order = feature_order) + "\n"
			return repr_str[:-1]

	def flattened_rep(self, feature_names, feature_lists):
		if self.conjunct_type == "Sum":
			return self.__flatten_dict(self.query,feature_names,feature_lists)
		if self.conjunct_type == "Product":
			final_rep = []
			for obj_dict in self.query: final_rep.append(self.__flatten_dict(obj_dict, feature_names, feature_lists))
			return tuple(final_rep)

	def __flatten_dict(self, query, feature_names, feature_lists):
		final_rep = []
		for f in feature_lists:
			final_rep.append([0]*len(f))
		if len(query) == 0: return tuple(final_rep)
		for key in query:
			f_pos = feature_names.index(key[0])
			fs_pos = feature_lists[f_pos].index(key[1])
			final_rep[f_pos][fs_pos] = query[key]
		return tuple(tuple(rep) for rep in final_rep)

	def __len__(self):
		return len(self.query)

	def __str__(self):
		return self.conjunct_type + " Conjunct " + self.query.__str__()

	def __repr__(self):
		return self.conjunct_type + " Conjunct " + self.query.__repr__() 

class Simple_Bayesian():
	def __init__(self, conjuncts, priors = None):
		self.priors = None
		self.conjuncts = None
		self.LLF = None

		self.__initialize(conjuncts, priors)

	def likelihood(self, sequence, prediction):
		likelihood_prob = np.empty(len(self.conjuncts), dtype = float)
		for ind, conj in enumerate(self.conjuncts):
			curr_pred = sequence.satisfies(conj)
			if curr_pred == prediction: likelihood_prob[ind] = 1
			else: likelihood_prob[ind] = 0.1
		return likelihood_prob

	def posterior(self, likelihood_prob):
		marginalizer = likelihood_prob.dot(self.priors)
		return np.multiply(likelihood_prob, self.priors)

	def update(self, sequence, prediction):
		self.priors = self.posterior(self.likelihood(sequence, prediction))

	def find_max(self, n = 1):
		sorted_inds = np.flip(np.argsort(self.priors))[:n]
		sorted_prob = self.priors[sorted_inds]
		sorted_conjuncts = []
		for ind in sorted_inds: sorted_conjuncts.append(self.conjuncts[ind])
		return sorted_conjuncts, sorted_prob

	def __initialize(self, conjuncts, priors):
		self.conjuncts = conjuncts
		if priors is not None:
			if len(priors) != len(conjuncts): raise RuntimeError
			self.priors = priors
		else:
			self.priors = np.ones(len(conjuncts), dtype = float)*(1/len(conjuncts))

# Helper Functions
###############################################################################

def hierarchical_rep(fs_dict, base_indent = "", key_order = None):
	if len(fs_dict) == 0: return base_indent + "Null"
	repr_str = ""
	all_f = []
	for key in fs_dict: all_f.append(key[0])
	unq_f = set(all_f)
	if key_order is not None:
		if not unq_f.issubset(key_order): raise KeyError
		new_f = []
		for k in key_order:
			if k in unq_f: new_f.append(k)
		unq_f = new_f
	for f in unq_f:
		repr_str += base_indent + "Feature " + str(f) + ":\n"
		for key in fs_dict: 
			if key[0] == f:
				repr_str += base_indent + "  " + str(fs_dict[key]) + " | " + str(key[1]) + "\n"
	return repr_str[:-1]

def recur_verify_obj(formula, s_list, Sub_Func):
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
			if Sub_Func(obj_f, obj):
				# we start one branch in searching because we cannot
				# gaurentee that we should match this object with this term
				branch_formula = np.delete(formula, obj_i)
				branch_s_list = np.delete(s_list, ind)
				match_list.append(recur_verify_obj(branch_formula, branch_s_list, Sub_Func))
	# failure: no term find a matching object
	if len(match_list) == 0 or sum(match_list) == 0:
		return False
	else:
		return True

def merge_dicts(*dicts):
	res_dict = {}
	for d in dicts:
		for key in d:
			if key in res_dict: res_dict[key] += d[key]
			else: res_dict.update({key: d[key]})
	return res_dict

# Determine whether B is a subset of A
# Generally, B is a subset of A if B is more specific than A:
#	- Every key in A must also present in B
#   - Every keyed value in B must be equal to the keyed value in A
def subset_dicts_eq(A, B):
	if len(A) == 0: return True
	for k_a in A:
		v_a = A[k_a]
		if k_a in B:
			v_b = B[k_a]
			if v_b != v_a: return False
		else:
			return False
	return True

# Determine whether B is a subset of A
# Generally, B is a subset of A if B is more specific than A:
#	- Every key in A must also present in B
#   - Every keyed value in B must be larger or equal to the keyed value in A
def subset_dicts_geq(A, B):
	if len(A) == 0: return True
	for k_a in A:
		v_a = A[k_a]
		if k_a in B:
			v_b = B[k_a]
			if v_b < v_a: return False
		else:
			return False
	return True

def unique_perm(elems, counts, result_list, d, constructor = tuple):
	if d < 0: yield constructor(result_list)
	else:
		for ind in range(len(elems)):
			if counts[ind] > 0:
				result_list[d] = elems[ind]
				counts[ind] -= 1
				for g in unique_perm(elems, counts, result_list, d-1, constructor = constructor):
					yield g
				counts[ind] += 1

def multiset_comb(n, r, constructor = tuple):
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

def multiset_perm(n, r):
	indices = np.arange(n)
	res = [indices for i in range(r)]
	return product(*res)

def get_primes():
	""" Generate an infinite sequence of prime numbers.
	"""
	# Maps composites to primes witnessing their compositeness.
	# This is memory efficient, as the sieve is not "run forward"
	# indefinitely, but only as long as required by the current
	# number being tested.
	#
	D = {}
	
	# The running integer that's checked for primeness
	q = 2
	
	while True:
		if q not in D:
			# q is a new prime.
			# Yield it and mark its first multiple that isn't
			# already marked in previous iterations
			# 
			yield q
			D[q * q] = [q]
		else:
			# q is composite. D[q] is the list of primes that
			# divide it. Since we've reached q, we no longer
			# need it in the map, but we'll mark the next 
			# multiples of its witnesses to prepare for larger
			# numbers
			# 
			for p in D[q]:
				D.setdefault(p + q, []).append(p)
			del D[q]
		
		q += 1