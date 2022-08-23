import json
import os

import nfp
import pytest
from nfp.frameworks import tf
from nfp.preprocessing.crystal_preprocessor import PymatgenPreprocessor

dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope="module")
def smiles_inputs():
    preprocessor = nfp.preprocessing.mol_preprocessor.SmilesPreprocessor()
    dataset = tf.data.Dataset.from_generator(
        lambda: (
            preprocessor(smiles, train=True) for smiles in ["CC", "CCC", "C1CC1", "C"]
        ),
        output_signature=preprocessor.output_signature,
    ).padded_batch(batch_size=4)

    return preprocessor, list(dataset.take(1))[0]


@pytest.fixture(scope="module")
def inputs_no_padding(smiles_inputs):
    preprocessor, inputs = smiles_inputs

    dataset = tf.data.Dataset.from_generator(
        lambda: (
            preprocessor(smiles, train=True) for smiles in ["CC", "CCC", "C(C)C", "C"]
        ),
        output_signature=preprocessor.output_signature,
    ).padded_batch(batch_size=4)

    return list(dataset.take(1))[0]


@pytest.fixture(scope="module")
def inputs_with_padding(smiles_inputs):
    preprocessor, inputs = smiles_inputs

    dataset = tf.data.Dataset.from_generator(
        lambda: (
            preprocessor(smiles, train=True) for smiles in ["CC", "CCC", "C(C)C", "C"]
        ),
        output_signature=preprocessor.output_signature,
    ).padded_batch(
        batch_size=4,
        padded_shapes={"atom": (20,), "bond": (40,), "connectivity": (40, 2)},
    )

    return list(dataset.take(1))[0]


@pytest.fixture(scope="module")
def structure_inputs():
    pymatgen_core = pytest.importorskip("pymatgen.core")
    with open(os.path.join(dir_path, "structure_data.json"), "r") as f:
        structures_dict = json.loads(f.read())
        structures = [
            pymatgen_core.Structure.from_dict(item) for item in structures_dict.values()
        ]

    return structures


@pytest.fixture(scope="module")
def crystals_and_preprocessor(structure_inputs):
    preprocessor = PymatgenPreprocessor()
    dataset = tf.data.Dataset.from_generator(
        lambda: (preprocessor(struct, train=True) for struct in structure_inputs),
        output_signature=preprocessor.output_signature,
    ).padded_batch(batch_size=5, padding_values=preprocessor.padding_values)

    return preprocessor, list(dataset.take(1))[0]
