#data from: https://github.com/cp2k/cp2k/blob/master/data/POTENTIAL && https://github.com/cp2k/cp2k/blob/master/data/BASIS_MOLOPT
from amaceing_toolkit.workflow.utils import xyz_reader

def available_functionals():
    return ["PBE", "PBE_SR", "BLYP", "BLYP_SR", "REVPBE", "REVPBE_SR", "RPBE", "RPBE_SR"]

def kind_data_functionals(functional, coord_file=None):
    output_string = f"#KIND DATA from cp2k_kind_data.py ({functional.split('_')[0]} Functional)"
    atom_list = []

    if coord_file is not None:
        # Read the first frame of the coordinate file and get only the atoms
        atoms = xyz_reader(coord_file, only_atoms=True)[0]

        # Search for individual atoms in the atom array
        atom_list = []
        for atom in atoms:
            if atom not in atom_list:
                atom_list.append(atom)
    else:
        atom_list = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "Ta", "W", "Ir", "Pt", "Au", "Tl", "Pb", "Bi"]

    if atom_list in ["Cd", "Tc", "Sn", "Xe", "Nb", "Cs", "Ta", "Ir", "Pt", "Tl"] and functional in ["BLYP", "BLYP_SR"]:
        print(
            f"WARNING: Unable to locate a CP2K GTH pseudopotential / MOLOPT basis combination for element '{atom}' "
            f"when using functional '{functional}'.\n"
            "Reason: The distributed CP2K POTENTIAL/BASIS_MOLOPT sets do not provide data for this element.\n"
            "Suggested resolutions: Switch to a supported functional such as 'PBE' (preferred for broad element coverage)\n"
            "Action: Aborting to prevent running with incomplete KIND definitions."
        )
        exit(1)

    dict_atom_ppot_velec = {
        'H': 1,
        'He': 2,
        'Li': 3,
        'Be': 4,
        'B': 3,
        'C': 4,
        'N': 5,
        'O': 6,
        'F': 7,
        'Ne': 8,
        'Na': 9,
        'Mg': 10,
        'Al': 3,
        'Si': 4,
        'P': 5,
        'S': 6,
        'Cl': 7,
        'Ar': 8,
        'K': 9,
        'Ca': 10,
        'Sc': 11,
        'Ti': 12,
        'V': 13,
        'Cr': 14,
        'Mn': 15,
        'Fe': 16,
        'Co': 17,
        'Ni': 18,
        'Cu': 11,
        'Zn': 12,
        'Ga': 13,
        'Ge': 4,
        'As': 5,
        'Se': 6,
        'Br': 7,
        'Kr': 8,
        'Rb': 9,
        'Sr': 10,
        'Y': 11,
        'Zr': 12,
        'Nb': 13,
        'Mo': 14,
        'Tc': 15,
        'Ru': 16,
        'Rh': 17,
        'Pd': 18,
        'Ag': 11,
        'Cd': 12,
        'In': 13,
        'Sn': 4,
        'Sb': 5,
        'Te': 6,
        'I': 7,
        'Xe': 8,
        'Cs': 9,
        'Ba': 10,
        'Ta': 13,
        'W': 14,
        'Ir': 17,
        'Pt': 18,
        'Au': 11,
        'Tl': 13, 
        'Pb': 4,
        'Bi': 5
    }

    short_range = False
    if "SR" in functional:
        functional = functional.replace("_SR", "")
        short_range = True

    if functional in ["REVPBE", "RPBE"]:
        functional = "PBE"  # Use PBE pseudopotentials

    for atom in atom_list:
        if atom in dict_atom_ppot_velec:
            if not short_range and atom in ["H", "C", "N", "O", "F", "Si", "P", "S", "Cl"]:
                output_string += f"""
    &KIND {atom}
        BASIS_SET DZVP-MOLOPT-GTH-q{dict_atom_ppot_velec[atom]}
        POTENTIAL GTH-{functional}-q{dict_atom_ppot_velec[atom]}
    &END KIND

"""
            else:
                output_string += f"""
    &KIND {atom}
        BASIS_SET DZVP-MOLOPT-SR-GTH-q{dict_atom_ppot_velec[atom]}
        POTENTIAL GTH-{functional}-q{dict_atom_ppot_velec[atom]}
    &END KIND

"""
    return output_string