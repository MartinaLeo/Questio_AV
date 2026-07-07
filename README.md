# Authorship Verification for Medieval Latin 
This repository contains a system for authorship verification of medieval Latin texts, implementing feature extraction, distributional random oversampling, and classification algorithms to determine text authorship.

## Project Structure

The project is organized into the following modules:

- **data_preparation**: Contains tools for corpus loading and text segmentation
- **feature_extraction**: Implements various feature extraction methods for text analysis
- **oversampling**: Contains the Distributional Random Oversampling (DRO) algorithm and supporting functions
- **main.py**: Main execution script for the authorship verification system

## Requirements

The project comes with a _requirements.txt_ file. 

In case you want to create your own environment, follow these steps: Create a conda environment and install spaCy's _la_core_web_lg_ core. This core requires older versions of numpy,
that should be installed before installing other packages such as scipy:

```bash
conda create -n questio python=3.10 -y
conda activate questio

pip install "numpy>=1.22.4,<1.29.0"
pip install scipy gensim scikit-learn nltk tqdm
pip install "spacy>=3.8.11,<3.9.0"

pip install \
"https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-3.9.5-py3-none-any.whl"
```

You should also download some _nltk_ models:

```python
import nltk
nltk.download('punkt_tab')
```

## Usage

The system can be run in three modes based on the `--test-document` argument:

1. Full Leave-One-Out:
This runs verification on all documents in the corpus.

2. Author-specific Leave-One-Out:
This only processes documents by the specified author.

3. Single Document Verification:
This verifies only the specified document.

The target author can be set with `--target`:
By default, target author is "Dante" and test-document is empty (full LOO).
