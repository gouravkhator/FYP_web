# Movies Recommendation System

This is the final year project.

## Team Members

* Mainak Roy
* Gourav Khator
* Atraya Bose
* Aishik Roy

---
## Project Usage

### Installation and Post-Installation Setup Guide

```bash
pip install pipenv
```

Then clone the repo. Inside the cloned directory, run the following:

```bash
pipenv install
```

Then, add all the follwing input files in the path 'app/inputs/'.
* movies_metadata.csv
* links_small.csv

**Note: All the commands below should be run inside the created virtual environment.**

---

### Run Development Server

```bash
python main.py
```

### Simple Recommender System

**The below commands will generate .csv files in the 'app/outputs' directory for top movies of all genres.**

Run from cloned directory (main project directory):

```bash
python -m app.algos.simple_recom
```
