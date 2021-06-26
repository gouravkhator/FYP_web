# Movies Recommendation System

This is the final year project.

## Team Members with their University Roll Numbers

- Mainak Roy (13000117095)
- Gourav Khator (13000117104)
- Atraya Bose (13000117116)
- Aishik Roy (13000117133)

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

- movies_metadata.csv
- links_small.csv
- links.csv
- credits.csv
- keywords.csv
- ratings_small.csv

**Note: All the commands below should be run inside the created virtual environment.**

### Activate the Virtual Environment

```bash
pipenv shell
```

---

## Standalone Movie Recommender Algorithms/Models

### Simple Recommender System

**The below command will generate .csv files in the 'app/outputs' directory for top movies of all genres.**

Run from cloned directory (main project directory):

```bash
python -m app.algos.simple_recom
```

### Content Based Recommender System

**The below command will generate .csv file in the 'app/outputs' directory for metadata_smd that will be used for further processing.**

The below command also acts as a CLI tool. So, running that, actually asks for user input for his/her favourite movie and the respective filters that they can modify in CLI itself.

Run from cloned directory (main project directory):

```bash
python -m app.algos.metadata_recom
```

### Hybrid Based Recommender System

The below command acts as a CLI tool. So, running that, actually asks for user input for his user id as saved in csv file, his watched favourite movies and the respective filters that they can modify in CLI itself.

Run from cloned directory (main project directory):

```bash
python -m app.algos.hybrid_recom
```

### Run Development Server

```bash
python main.py
```

**Note: If the output csv files are not present, then it would create the outputs directory and would generate all output files for further processing.**

So, this may take some time to go to some url which needs processing of large datasets (if they don't exist).
