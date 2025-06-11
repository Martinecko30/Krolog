from krolog_tools import Fact, Rule


def parse_fact(text: str) -> Fact:
    text = text.lstrip(".")
    if ("(" in text):
        args = text[text.index("(")+1:-1].split(",")
        name = text[:text.index("(")]
    else:
        args = []
        name = text

    args = list(map(lambda x: x.strip(), args))
    return(Fact(name, args))


def parse_rule(text: str) -> Rule:
    text = text.lstrip("!")
    parts = text.split("<=")
    truth = parse_fact(parts[0].strip())
    args = parts[1].split("&")
    when = [parse_fact(x.strip()) for x in args]
    return Rule(truth, when)


def parse(file: str) -> tuple[list[Fact], list[Rule], list[Fact]]:
    facts: list[Fact] = []
    rules: list[Rule] = []
    questions: list[Fact] = []
    with open(file, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if (line.startswith(".")):  # Fact
            facts.append(parse_fact(line))

        if (line.startswith("!")):  # Rule
            rules.append(parse_rule(line))

        if (line.startswith("?")):  # Question
            questions.append(parse_fact(line.lstrip("?")))

    return facts, rules, questions
