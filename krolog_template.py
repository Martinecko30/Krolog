from krolog_parser import parse
from krolog_tools import Fact, Rule, IndexedFact, Connection, is_var, is_value

TEMPLATE_USED = True # True, pokud jsi použil šablonu; False, pokud ne.

Facts = list[Fact]
Rules = list[Rule]
InFacts = list[IndexedFact]
ConnectNone = Connection | None
Solution = dict[str, str]
Solutions = list[Solution] | bool


def transform_connection_to_solution(question: IndexedFact, connection: Connection) -> Solution:
    result_dict = {}
    question_vars = {arg for arg in question.get_args() if is_var(arg)}

    for key_set, value in connection.classes:
        if value is not None:
            for key in key_set:
                if is_var(key) and key in question_vars:
                    result_dict[''.join([i for i in key if not i.isdigit()])] = value
    return result_dict


def equal_fact_question(fact: IndexedFact, question: IndexedFact,
                        connect: Connection) -> ConnectNone:
    """
        Vyhodnotí, zda je fakt sjednotitelný s danou otázkou. Za předpokladu
        rovností v connect.

        Můžeme-li ho sjednotit, sjednotíme a předáme nové propojení.
        Není-li to možné, předáme None.

        Příklady jsou ve vysvětlující doušce pro prolog_template v zadání.
    """
    if fact.get_name() != question.get_name() or fact.get_len() != question.get_len():
        return None

    new_connect = connect.copy()

    for fact_arg, question_arg in zip(fact.get_args(), question.get_args()):
        if is_value(fact_arg) and is_value(question_arg) and fact_arg != question_arg:
            return None

        if is_var(fact_arg) and is_var(question_arg) and fact_arg == question_arg:
            return None

        if not new_connect.add_equal(fact_arg, question_arg):
            return None

    return new_connect


def apply_rule(rule: Rule, question: IndexedFact, connect: Connection)\
    -> tuple[InFacts, ConnectNone]:
    """
        Vyhodnotí, zda je dané pravidlo použitelné pro danou otázku.

        Pokud ano, předá dvojici (seznam faktů-předpokladů,
            aktualizované connect)
        Pokud ne, předá dvojici ([], None)

        Příklady jsou ve vysvětlující doušce pro prolog_template v zadání.
    """
    truth_indexed = IndexedFact(rule.truth, question.get_index() + 1000)
    new_connect = equal_fact_question(truth_indexed, question, connect)

    if new_connect is None:
        return [], None

    premises = [
        IndexedFact(fact, truth_indexed.get_index())
        for fact in rule.when
    ]

    return premises, new_connect


def solve_problem(facts: Facts, rules: Rules, questions: InFacts)\
    -> Solutions:
    """
        Funkce, která vyřeší danou sadu otázek, jako výsledek předá buďto:
          bool - pokud otázky neobsahují proměnnou
              True - jedná se o pravdivé tvrzení
              False - nejedná se o pravdivé tvrzení
          seznam možných řešení - jinak
              řešení jsou ulozena ve slovniku: {promenna: hodnota, ...}
              pokud řešení neexistuje, dany seznam bude prazdny

        Příklady jsou ve vysvětlující doušce pro prolog_template v zadání.
    """
    def backtrack(remaining_questions: InFacts, current_connection: Connection, all_solutions: list[Connection]) -> None:
        if not remaining_questions:
            all_solutions.append(current_connection)
            return

        question = remaining_questions[0]
        rest_of_questions = remaining_questions[1:]

        # Unify facts
        for fact in facts:
            unification = equal_fact_question(IndexedFact(fact, question.get_index()), question, current_connection)
            if unification is not None:
                backtrack(rest_of_questions, unification, all_solutions)

        # Unify rules
        for rule in rules:
            premises, unification = apply_rule(rule, question, current_connection)
            if unification is not None:
                backtrack(premises + rest_of_questions, unification, all_solutions)

    solutions = []
    for question in questions:
        all_solutions = []
        backtrack([question], Connection(), all_solutions)
        solutions.extend(
            transform_connection_to_solution(question, solution)
            for solution in all_solutions if solution.classes
        )

    if any(is_var(arg) for q in questions for arg in q.get_args()):
        return solutions if solutions else []
    else:
        return bool(all_solutions)


def solve(facts: Facts, rules: Rules, questions: Facts) -> list[Solutions]:
    """
        Předá řešení všech otázek, podle výskytu .all společné, nebo oddělené.
    """
    indexed_questions = [IndexedFact(question, i) for i, question in enumerate(questions)]

    if any(fact.name == "all" and not fact.args for fact in facts):
        return [solve_problem(facts, rules, indexed_questions)]

    return [solve_problem(facts, rules, [indexed_question]) for indexed_question in indexed_questions]


# Solution developed using:
# https://is.muni.cz/el/fi/podzim2023/IB015/um/prednasky/IB015_10.pdf
if __name__ == "__main__":
    file_name = "test.txt"
    f, r, q = parse(file_name)
    print(solve(f, r, q))