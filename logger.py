import sys
import re
from datetime import date
from colorama import init

from loguru import logger

init(autoreset=True)


def logging_setup():
    logger.level("SUCCESS", color="<green>")
    logger.level("INFO", color="<blue>")
    logger.level("ERROR", color="<red>")

    format_file = "{time:HH:mm:ss.SS} | <level>{level}</level> | {name}:{function}:{line} | {message}"
    format_stdout = "{time:HH:mm:ss.SS} | <level>{level}</level> | {message}"

    file_path = "logs/"

    logger.remove()

    logger.add(file_path + f"out_{date.today().strftime('%m-%d')}.log", colorize=True,
               format=format_file, encoding="utf-8", level="INFO")

    logger.add(sys.stdout, colorize=True, format=format_stdout, level="INFO")


def clean_brackets(raw_str):
    clean_text = re.sub(brackets_regex, '', raw_str)
    return clean_text


brackets_regex = re.compile(r'<.*?>')

logging_setup()
