import inquirer
import sys
from blessed import Terminal

def DeletePreviousLine():
    sys.stdout.write('\033[1A')
    sys.stdout.write('\033[2K')

def MenuSelection(ListOfOptions, Title):
    questions = [
        inquirer.List(
            "Answer1",
            message=Title,
            choices=ListOfOptions,
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["Answer1"]