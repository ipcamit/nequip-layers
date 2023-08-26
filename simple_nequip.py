import torch
from e3nn.o3 import Irreps
from layers import embedding as e
from layers import AtomwiseLinear

import yaml
import sys

if len(sys.argv)!=2:
    raise ValueError("Should provide only one argument, which is the yaml config file")

yaml_file = sys.argv[1]
print(f"Yaml file: {yaml_file}")

with open(yaml_file, "r") as stream:
    config = yaml.safe_load(stream)
print(config)
n_elems = len(config["elements"])

layer_dict = {}

# element node embedding onehot
elem_embedding_layer = e.OneHotAtomEncoding(n_elems)
node_attr_irrep = elem_embedding_layer.irreps_out
layer_dict["elem_embed"] = elem_embedding_layer

# edge embeddings
p = -1 if config["parity"] else 1
edge_attr_irrep = Irreps([(1,(l,p**l)) for l in range(config["lmax"] + 1)])
edge_embedding_layer = e.SphericalHarmonicEdgeAttrs(edge_attr_irrep)

assert(edge_attr_irrep == edge_embedding_layer.irreps_out) # check if sh is same as requested
layer_dict["edge_embed"] = edge_embedding_layer

# Radial basis # to do rmin
cutoff_kwargs = {"r_max": config["r_max"], "p": config["p"]}
basis_kwargs = {"r_max": config["r_max"], "num_basis": config["n_radial_basis"]}
radial_basis_layer = e.RadialBasisEdgeEncoding(basis_kwargs=basis_kwargs, cutoff_kwargs=cutoff_kwargs)
edge_feature_irrep = radial_basis_layer.irreps_out
layer_dict["radial_basis"] = radial_basis_layer

# atomwise embedding
node_feature_irrep = Irreps([(config["node_feature_size"], (0,1))])
first_atom_embedding = AtomwiseLinear(node_attr_irrep, node_feature_irrep)

assert(node_feature_irrep == first_atom_embedding.irreps_out)
layer_dict["first_atom_embed"] = first_atom_embedding
print(first_atom_embedding)
