import pandas as pd

from rdkit import Chem
from rdkit.Chem import MolStandardize
from chembl_structure_pipeline import standardizer

# functions for compound standardization
def mol_standardize(mol):
    # standardization by ChEMBL structure pipeline
    std_molblock = standardizer.standardize_molblock(Chem.MolToMolBlock(mol))
    parent_molblock, _ = standardizer.get_parent_molblock(std_molblock)
    mol_norm = Chem.MolFromMolBlock(parent_molblock)
    # keep largest fragment
    lfc = MolStandardize.fragment.LargestFragmentChooser()
    mol_l = lfc.choose(mol_norm)
    return mol_l

def mol_to_standardized_smiles_from_smiles(s):
    try:
        return Chem.MolToSmiles(mol_standardize(Chem.MolFromSmiles(s)))
    except:
        return None

df = pd.read_csv("prediction_data.csv")

df['Smiles'] = [mol_to_standardized_smiles_from_smiles(s) for s in df['Smiles']]

df.to_csv("prediction_data_std.csv", index=False)
