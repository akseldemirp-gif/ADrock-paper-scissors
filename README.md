# Aksel's Rock Paper Scissors

A command-line Python game where you play rock, paper, scissors against the computer. Includes automated tests and a reusable winner-determination function.

## Prerequisites

- Anaconda or Miniconda
- Git

## Setup

Clone the repository and navigate into it:

```bash
git clone https://github.com/akseldemirp-gif/ADrock-paper-scissors.git
cd ADrock-paper-scissors
```

Create the virtual environment (first time only):

```bash
conda create -n rps-env python=3.11
```

Activate the environment whenever you work on this project:

```bash
conda activate rps-env
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Game

From the repository's root directory, with the environment active:

```bash
python -m app.rps
```

Enter `rock`, `paper`, or `scissors` when prompted. The computer randomly chooses an option, and the game displays the result.

Rock beats scissors, scissors beats paper, and paper beats rock. Matching choices produce a tie. Invalid choices display an error message; run the program again to retry.

## Run Tests

From the repository's root directory, with the environment active:

```bash
pytest
```

The tests import `determine_winner` from the application code and check all nine possible matchups across three test functions: ties, user wins, and computer wins.

## Project Structure

- `app/rps.py`: Game logic and command-line interaction.
- `app/__init__.py`: Marks the app directory as a Python package.
- `test/rps_test.py`: Automated tests for the winner logic.
- `conftest.py`: Supports test imports with the project's test setup.
- `requirements.txt`: Required third-party packages.