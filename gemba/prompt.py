import re
from termcolor import colored


def parse_and_check_numerical_answer(answer, min=None, max=None):
    attempt = parse_numerical_answer(answer, min, max)
    if attempt is not None:
        if attempt < min or attempt > max:
            return None
        return attempt

    return None


def parse_numerical_answer(answer, min=None, max=None):
    # get all numbers in a string
    numbers = re.findall(r'\d+', answer)
    if len(numbers) == 1:
        return int(numbers[0])

    # check if the answer is in form ['100'] and extract the number
    r1 = re.match(r"^\[['\"][0-9]*['\"]\]$", answer)
    if r1 is not None:
        return int(answer[2:-2])

    if max is not None:
        # check if the answer is in a form of 0/100
        r2 = re.match(rf"^[0-9]*/{max}$", answer)
        if r2 is not None:
            return int(answer.split("/")[0])

    return None


def validate_number(x, min=0, max=100):
    attempt = parse_and_check_numerical_answer(x, min, max)
    if attempt is not None:
        return attempt
    return None


def parse_classes(answer, classes):
    final_class = None
    for i in range(len(classes)):
        if classes[i].lower() in answer.lower():
            if final_class is None:
                final_class = i
            else:
                print(colored(f"Two classes found in answer {answer}", "red"))
                return None

    return final_class


def validate_stars(x):
    x = x.lower()
    # try to find all possible answers as sometimes it seems to be explaining itself
    possible_answers = set()

    # check if string x contains * characters
    if "*" in x:
        possible_answers.add(x.count("*"))
    if "★" in x:
        possible_answers.add(x.count("★"))

    x = f" {x} ".replace("\n", " ")
    # possible answers: "five stars", "5 stars", "five", "five starts: perfect translation", ...
    if " one " in x or "1 star" in x:
        possible_answers.add(1)
    if " two " in x or "2 star" in x:
        possible_answers.add(2)
    if " three " in x or "3 star" in x:
        possible_answers.add(3)
    if " four " in x or "4 star" in x:
        possible_answers.add(4)
    if " five " in x or "5 star" in x:
        possible_answers.add(5)

    numerical = parse_numerical_answer(x)
    if numerical is not None:
        possible_answers.add(numerical)

    if len(possible_answers) == 1:
        answer = possible_answers.pop()
        if 1 <= answer <= 5:
            return answer
    return None


language_codes = {
    "en": "English",
    "de": "German",
}

prompts = {
    "doc-GEMBA-DA_ref": {
        "prompt": 'Score the last sentence of the following translation from {source_lang} to {target_lang} with respect to the human reference on a continuous scale 0 to 100 where score of zero means "no meaning preserved, not fluent, not coherent" and score of one hundred means "perfect fluency, coherence and meaning".\n\n{source_lang} source: "{source_seg}"\n{target_lang} human reference: {reference_seg}\n{target_lang} machine translation: "{target_seg}"\nScore: ',
        "validate_answer": lambda x: validate_number(x),
        "use_ref": True},

    "doc-GEMBA-SQM_ref": {
        "prompt": 'Score the last sentence of the following machine translation from {source_lang} to {target_lang} with respect to the human reference on a continuous scale from 0 to 100 that starts with "No meaning preserved, not fluent, not coherent", goes through "Some meaning preserved, lacking fluency and coherence", then "Most meaning preserved, few mistakes, mostly fluent and coherent", up to "Perfect fluency, coherence and meaning".\n\n{source_lang} source: "{source_seg}"\n{target_lang} human reference: "{reference_seg}"\n{target_lang} machine translation: "{target_seg}"\nScore (0-100): ',
        "validate_answer": lambda x: validate_number(x),
        "use_ref": True},

    "sent-GEMBA_DA_ref": {
        "prompt": 'Score the following translation from {source_lang} to {target_lang} with respect to the human reference on a continuous scale 0 to 100 where score of zero means "no meaning preserved" and score of one hundred means "perfect meaning and grammar".\n\n{source_lang} source: "{source_seg}"\n{target_lang} human reference: {reference_seg}\n{target_lang} machine translation: "{target_seg}"\nScore: ',
        "validate_answer": lambda x: validate_number(x),
        "use_ref": True},

    "sent-GEMBA_SQM_ref": {
        "prompt": 'Score the following machine translation from {source_lang} to {target_lang} with respect to the human reference on a continuous scale from 0 to 100 that starts with "No meaning preserved", goes through "Some meaning preserved", then "Most meaning preserved and few grammar mistakes", up to "Perfect meaning and grammar".\n\n{source_lang} source: "{source_seg}"\n{target_lang} human reference: "{reference_seg}"\n{target_lang} machine translation: "{target_seg}"\nScore (0-100): ',
        "validate_answer": lambda x: validate_number(x),
        "use_ref": True},
}
