def is_var(s: str) -> bool:
    return s[0].isupper()


def is_value(s: str) -> bool:
    return not is_var(s)


def eq_val(a: str | None, b: str | None) -> tuple[bool, str | None]:
    if a is None:
        return True, b
    if b is None:
        return True, a
    return a == b, a


class Fact:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args

    def __str__(self):
        return f'.{self.name} ({self.args})'

class Rule:
    def __init__(self, truth: Fact, when: list[Fact]):
        self.truth = truth
        self.when = when

    def __str__(self):
        return f'!{self.truth} <= {[str(fact) for fact in self.when]}'


class IndexedFact:
    """
        Třída obalující třídu fact (přidává index k jeho proměnným).
        Podrobněji (i s příklady) je popsaná v zadání.
    """
    def __init__(self, fact: Fact, index: int):
        self.fact = fact
        self.index = index

    def get_arg(self, i: int) -> str:
        arg = self.fact.args[i]
        if is_value(arg):
            return arg
        return arg + str(self.index)

    def get_name(self) -> str:
        return self.fact.name

    def get_index(self) -> int:
        return self.index

    def get_len(self) -> int:
        return len(self.fact.args)

    def get_args(self):
        for i in range(self.get_len()):
            yield self.get_arg(i)

    def __str__(self):
        return f"{self.get_name()} ({self.get_index()}): {list(self.get_args())}"


class Connection:
    """
        Rozklad podle relace ekvivalence dané rovností proměnných,
        přičemž si ještě udržují info o případné rovnosti s hodnotou.

        Podrobněji (i s příklady) je tato třída popsaná v zadání.
    """
    def __init__(self):
        # [({Promenne spojene rovnosti}, jejich hodnota/None), ...]
        self.classes: list[tuple[set[str], str | None]] = []

    def find_class_index(self, var: str) -> int | None:
        for i in range(len(self.classes)):
            cl, _ = self.classes[i]
            if var in cl:
                return i
        return None

    def _merge(self, i: int, j: int) -> bool:
        cl_a, a = self.classes[i]
        cl_b, b = self.classes[j]
        eq, val = eq_val(a, b)
        if not eq:
            return False

        cl_a.update(cl_b)
        self.classes[i] = cl_a, val
        self.classes.pop(j)
        return True

    def _add_val(self, var: str, val: str | None) -> bool:
        if val is None:
            return True
        i = self.find_class_index(var)
        if i is None:
            self.classes.append(({var}, val))
            return True
        cl, v = self.classes[i]
        if v is not None and v != val:
            return False
        self.classes[i] = cl, val
        return True

    def _add_eq(self, a: str, b: str) -> bool:
        i = self.find_class_index(a)
        j = self.find_class_index(b)
        if i is None and j is None:
            self.classes.append(({a, b}, None))
            return True
        if i is None:
            self.classes[j][0].add(a)
            return True
        if j is None:
            self.classes[i][0].add(b)
            return True
        a_cl, _ = self.classes[i]
        b_cl, _ = self.classes[j]

        if b in a_cl:
            return True
        if len(a_cl) >= len(b_cl):
            return self._merge(i, j)
        return self._merge(j, i)

    def add_var_val(self, var: str, val: str) -> bool:
        """
            Přidá rovnost dvou proměnné a hodnoty. Případně vrátí False,
            pokud by to vedlo ke sporu.
        """
        return self._add_val(var, val)

    def add_var_var(self, a: str, b: str) -> bool:
        """
            Přidá rovnost dvou proměnných. Případně vrátí False, pokud by to
            vedlo ke sporu.
        """
        return self._add_eq(a, b)

    def add_equal(self, a: str, b: str) -> bool:
        """
            Vyhodnotí, zda je to možné a případně přidá rovnost mezi dvěma
            hodnotami nebo konstatntami v jakékoli kombinaci
            (X = alice; X = Z; cecil = Y; bob = alice).
            Byla-li rovnost přidána, předá True, jinak False.
            Například tato posloupnost volání:
            1. c.add_equal(X, alice) # True - přidá rovnost X = alice
            2. c.add_equal(X, cecil) # False - žádná rovnost se nepřidá,
                    # protože není možné aby alice = X = cecil.
            3. c.add_equal(Y, bob)   # přidá rovnost Y = bob a vrátí True.
            4. c.add_equal(Y, X)     # False - alice = X != Y = bob
            5. c.add_equal(Z, bob)   # True
            6. c.add_equal(Y, Z)     # True - bob = Y = Z = bob

            Výsledek print(c.classes) # [({X}, alice), ({Z, Y}, bob)]
        """
        if is_value(a):
            if is_value(b):
                return a == b
            return self.add_var_val(b, a)

        if is_value(b):
            return self.add_var_val(a, b)
        return self.add_var_var(a, b)

    def copy(self) -> 'Connection':
        """
            Hluboká kopie dané třídy.
        """
        connect = Connection()
        for clas, val in self.classes:
            connect.classes.append((clas.copy(), val))
        return connect

    def get_val(self, var: str) -> str | None:
        """
            Předá hodnotu proměnné, je-li definována, jinak None.
            Pokud je vložena hodnota, funkce vrátí ji.
            Pro příklad v add_equal:
            get_var(X)  # alice
            get_var(XX) # None
            get_var(Z)  # bob
            get_var(alice) # alice
        """
        if is_value(var):
            return var
        for cl, a in self.classes:
            if var in cl:
                return a
        return None

    def __str__(self):
        return f"Connection: {self.classes}"