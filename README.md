# Use of the prediction model

This directory contains the trained prediction model, preprocessing script, and configuration file
required to apply the model reported in this study to new compounds.

For practical use, one trained checkpoint is provided. Among the five final GCN + RDKit models
evaluated on the external pesticide dataset, the model with the lowest RMSE was selected for
distribution. This selection was made only for model distribution; the predictive performance reported
in the manuscript is based on the mean and standard deviation across all five final models.

## Contents

```text
README.md               this file
prepare_data.py         structure standardization
predict_config.json     kMoL configuration for prediction
checkpoint.pt           trained GCN + RDKit model
```

## Software versions

The following software versions were used:

- Python: 3.9.17
- RDKit: 2022.9.4
- ChEMBL Structure Pipeline: 1.2.2
- kMoL: 1.1.9.3

The preprocessing script additionally requires `pandas`.

kMoL is available at <https://github.com/elix-tech/kmol>. Installation instructions for the conda
environment and the Docker image are provided in the repository. All kMoL operations are controlled
by JSON configuration files, and each command is executed as `kmol <job> <configuration file>`.

The configuration file provided here assumes that all input files are located in the working directory
from which kMoL is executed. Adjust the `input_path`, `checkpoint_path`, `output_path`, and
`cache_location` entries if a different directory structure is used.

## 1. Input files

### Compounds to be predicted

To apply the model to new compounds, prepare a CSV file containing at least the following columns:

- `Smiles`: molecular structure represented as SMILES. Molecular structures should be standardized
  before prediction using the procedure described below.
- `LogM`: log10-transformed EC50 in mol/L. When experimental values are not available, an arbitrary
  placeholder value can be used because kMoL requires the target column during inference.

Place the CSV file in the same directory as `prepare_data.py`.

When experimental toxicity data are used to evaluate model performance, we recommend curating the
data according to the procedures described in the Materials and Methods of the manuscript. In
particular, 48-h EC50 values for *Daphnia magna* should be used and converted to LogM.

## 2. Structure standardization

`prepare_data.py` standardizes molecular structures as follows:

1. Reads the input CSV file.
2. Standardizes molecular structures using ChEMBL Structure Pipeline 1.2.2.
3. Retains the largest fragment for multi-component compounds using RDKit.
4. Converts the standardized structures back to SMILES.
5. Writes the standardized data to a new CSV file.

Run the script as follows:

```bash
python prepare_data.py
```

Structures that cannot be standardized should be removed before the file is passed to kMoL.

The standardized SMILES should be provided in the `Smiles` column used for prediction.

## 3. Model architecture

The provided model is a graph convolutional network built with `torch_geometric.nn.GCNConv` layers
and combined with the 17 RDKit molecular descriptors described in Table S1 of the Supporting
Information. The model was implemented using kMoL version 1.1.9.3.

The provided checkpoint is already trained and can be used directly for prediction. Details of model
construction, training, and evaluation are described in the Materials and Methods of the manuscript.

## 4. Prediction

Place `checkpoint.pt` in the working directory, or set its path as `checkpoint_path` in
`predict_config.json`. The `loader` section should point to the standardized file containing the
compounds to be predicted. Predictions are then generated with:

```bash
kmol predict predict_config.json
```

In `predict_config.json`, the splitter assigns all records to the test partition, so that predictions
are generated for every compound in the input file. The results are written to `predictions.csv`
under `output_path`.

The predicted values are given as LogM, defined as the log10-transformed EC50 in mol/L.

When experimental values are available for the compounds, the metrics listed in `test_metrics` can be
calculated for the same file with:

```bash
kmol eval predict_config.json
```

## Notes on application

The model is intended for screening applications, and predictions should be interpreted with
appropriate caution for compounds outside the chemical and toxicity ranges represented in the
training data.
