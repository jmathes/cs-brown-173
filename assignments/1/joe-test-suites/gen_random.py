from random import randint, choice

path = "/Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random/"

alphabet = "bcdfghjklmnpqrstvwxz"
identifiers = ["a"]


def get_new_identifier():
    global identifiers
    nid = ""
    while randint(1, 1 + len(nid)) == 1:
        letter = randint(0, len(alphabet) - 1)
        nid += alphabet[letter]

    identifiers.append(nid)
    return nid


def get_identifier():
    if randint(1, 3) == 1:
        nid = get_new_identifier()
    else:
        nid = choice(identifiers)
    return nid


def write_to_file(expression, verbose=True):
    fn = str(randint(10 ** 8, 10 ** 9 - 2)) + ".psl"
    with open(path + fn, "wb") as new_psl:
        new_psl.write(str(expression))


limit = 0

types_made = 1
ifs_made = 0
objects_made = 0


def get_random_type(exclude):
    global types_made
    types_made += 1
    global ifs_made
    global objects_made
    global limit
    limit += 1
    if randint(10, 15) < limit:
        return Bool
    valid_types = all_expressions - set(exclude)
    valid_types = [t for t in valid_types if getattr(t, "ready", True)]
    if DefVar in valid_types and DefFun in valid_types and randint(1, 4) > 3:
        return choice([DefFun, DefVar])

    if If in valid_types and choice([False, False, True]):
        ifs_made += 1
        return If
    if Lambda in valid_types and choice([False, False, True]):
        ifs_made += 1
        return Lambda
    if DefFun in valid_types and choice([False, False, True]):
        ifs_made += 1
        return DefFun

    if Greater in valid_types and choice([False, False, True]):
        objects_made += 1
        return Object
    if Less in valid_types and choice([False, False, True]):
        return AtWithIdentifier
    if Minus in valid_types and choice([False, False, True]):
        return AtWithIdentifier
    if Equals in valid_types and choice([False, False, True]):
        return AtWithString
    if Plus in valid_types and choice([False, False, True]):
        return AtWithIdentifier

    return choice(list(valid_types))


def get_maybebracey_body(expr, wrap=None):
    if wrap is None:
        wrap = "{}"
    if isinstance(expr, Def):
        lastbit = "%s" % expr
    else:
        lastbit = "%s%s%s" % (wrap[0], expr, wrap[1])
    return lastbit


def get_random_expression(exclude=None):
    # if randint(1, 5) == 1:
    #     exclude = []
    return get_random_type(exclude or [])()


def get_usually_false(exclude):
    if randint(1, 6) < 6:
        condition = Bool()
        condition.val = False
    else:
        condition = get_random_expression(exclude)
    return condition


class Expression(object):
    def __init__(self):
        self.subs = []


def ap(st):
    return "(%s)" % st


def np(st):
    return st


def mp(st):
    return ap(st)
    if choice([True, False]):
        return ap(st)
    return st


def commastring(subs, j=None):
    if j is None:
        j = ", "
    return j.join([str(s) for s in subs])


class Number(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.val = randint(0, 1000)

    def __repr__(self):
        return np(str(self.val))


class String(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.val = get_identifier()

    def __repr__(self):
        return np('"%s"' % self.val)


class Bool(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.val = choice([True, False])

    def __repr__(self):
        return np("true" if self.val else "false")


class Chain(Expression):
    def __init__(self):
        Expression.__init__(self)
        valid_types = list(all_expressions - set())
        xtype = get_random_type([Chain, DefFun, DefVar])
        while not getattr(xtype, "ready", True):
            xtype = choice(valid_types)

        new_exp = xtype()
        self.subs.append(new_exp)
        xtype = get_random_type([Chain, DefFun, DefVar])
        while not getattr(xtype, "ready", True):
            xtype = choice(valid_types)

        new_exp = xtype()
        self.subs.append(new_exp)
        while randint(3, 3 + len(self.subs)) <= 3:
            xtype = get_random_type([Chain, DefFun, DefVar])
            while not getattr(xtype, "ready", True):
                xtype = choice(valid_types)

            new_exp = xtype()
            self.subs.append(new_exp)

    def __repr__(self):
        return np(commastring(self.subs, ";") + ";")


class If(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs = [
            choice([])
            get_random_expression([DefFun, DefVar]),
            Bool(),
            Bool(),
            ]

    def __repr__(self):
        return ap("if (%s) then %s else %s" % (
            self.subs[0],
            get_maybebracey_body(self.subs[1], wrap="()"),
            get_maybebracey_body(self.subs[2], wrap="()"),
            ))


class For(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs = [
            get_random_expression([DefFun, DefVar]),
            get_usually_false([Chain, DefFun, DefVar]),
            get_random_expression([Chain, DefFun, DefVar]),
            get_random_expression(),
            ]

    def __repr__(self):
        lastbit = get_maybebracey_body(self.subs[-1])
        return np("for(%s; %s; %s) " % tuple(self.subs[:-1]) + lastbit)


class While(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs = [
            get_usually_false([Chain, DefFun, DefVar]),
            get_random_expression(),
            ]

    def __repr__(self):
        lastbit = get_maybebracey_body(self.subs[-1])
        return np("while(%s) " % tuple(self.subs[:-1]) + lastbit)


class Lambda(Expression):
    def __init__(self):
        Expression.__init__(self)
        for i in xrange(randint(0, len(identifiers))):
            self.subs.append(Identifier())
        self.subs.append(get_random_expression())

    def __repr__(self):
        lastbit = get_maybebracey_body(self.subs[-1])

        return np("lambda (%s) " % (
            commastring(self.subs[:-1])) + lastbit)


class Application(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Lambda())
        for i in xrange(randint(0, len(identifiers))):
            self.subs.append(get_random_expression([Chain, DefFun, DefVar]))

    def __repr__(self):
        return np("(%s)(%s)" % (self.subs[0], commastring(self.subs[1:])))


class Def(Expression):
    pass


class DefFun(Def):
    def __init__(self):
        Def.__init__(self)
        for i in xrange(randint(0, len(identifiers))):
            self.subs.append(Identifier())
        self.subs.append(Number())
        self.subs.append(Number())
        # self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
        # self.subs.append(get_random_expression())

    def __repr__(self):
        lastbit = get_maybebracey_body(self.subs[-1])

        return "deffun %s (%s) %s in %s" % (
            self.subs[0],
            commastring(self.subs[1:-2]),
            self.subs[-2], lastbit)


class DefVar(Def):
    def __init__(self, skip=False):
        if skip:
            return
        Def.__init__(self)
        self.subs.append(Identifier())
        self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
        self.subs.append(get_random_expression())

    def __repr__(self):
        lastbit = get_maybebracey_body(self.subs[-1])

        return "defvar %s = (%s) in " % tuple(self.subs[:-1]) + lastbit


class Object(Expression):
    def __init__(self):
        Expression.__init__(self)
        while randint(1, 3) > 1:
            self.subs.append(Identifier(force_new=True))
            self.subs.append(get_random_expression([Chain, DefFun, DefVar]))

    def __repr__(self):
        rep = "{"
        for i in xrange(len(self.subs) / 2):
            if i != 0:
                rep += ", "
            rep += "%s: %s" % (self.subs[i * 2], self.subs[i * 2 + 1])
        rep += "}"
        return ap(rep)


class AtWithIdentifier(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Object())

        self.subs.append(Identifier())

        while randint(1, 2) > 1:
            self.subs.append(Identifier())

    def __repr__(self):
        first = "%s@%s" % (self.subs[0], self.subs[1])
        first += "(%s)" % (commastring(self.subs[1:]))
        return np(first)


class AtWithString(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Object())

        self.subs.append(get_random_expression([
            Chain, DefFun, DefVar,
            While, For]))

        while randint(1, 2) > 1:
            self.subs.append(Identifier())

    def __repr__(self):
        first = "%s@[%s]" % (self.subs[0], self.subs[1])
        first += "(%s)" % (commastring(self.subs[1:]))
        return np(first)


class DotWithIdentifier(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Object())

        self.subs.append(Identifier())

    def __repr__(self):
        first = "%s.%s" % (self.subs[0], self.subs[1])
        return np(first)


class DotWithIdentifierFun(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Object())

        self.subs.append(Identifier())

    def __repr__(self):
        first = "%s.%s" % (self.subs[0], self.subs[1])
        first += "(%s)" % (commastring(self.subs[1:]))
        return np(first)


class DotWithString(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Object())

        self.subs.append(get_random_expression([
            Chain, DefFun, DefVar,
            While, For]))

    def __repr__(self):
        first = "%s[%s]" % (self.subs[0], self.subs[1])
        return np(first)


class DotWithStringFun(Expression):
    def __init__(self):
        Expression.__init__(self)
        if choice([True, False]):
            self.subs.append(Identifier())
        else:
            self.subs.append(Object())

        self.subs.append(get_random_expression([
            Chain, DefFun, DefVar,
            While, For]))

        while randint(1, 2) > 1:
            self.subs.append(Identifier())

    def __repr__(self):
        first = "%s[%s]" % (self.subs[0], self.subs[1])
        first += "(%s)" % (commastring(self.subs[1:]))
        return np(first)


class Assign(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(
            choice([Identifier,
                DotWithString,
                DotWithIdentifier])())

        self.subs.append(get_random_expression([Chain, DefFun, DefVar]))

    def __repr__(self):
        return np("%s = %s" % tuple(self.subs))


class PlusEquals(Assign):
    def __repr__(self):
        return np("%s += %s" % tuple(self.subs))


class MinusEquals(Assign):
    def __repr__(self):
        return np("%s -= %s" % tuple(self.subs))


class PostIncrement(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(Identifier())

    def __repr__(self):
        return ap("%s++" % tuple(self.subs))


class PostDecrement(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(Identifier())

    def __repr__(self):
        return ap("%s--" % tuple(self.subs))


class PreIncrement(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(Identifier())

    def __repr__(self):
        return ap("++%s" % tuple(self.subs))


class PreDecrement(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(Identifier())

    def __repr__(self):
        return ap("--%s" % tuple(self.subs))


class Less(Expression):
    def __init__(self):
        Expression.__init__(self)
        for i in xrange(2):
            if randint(1, 30) == 30:
                self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
            else:
                self.subs.append(choice([Number, Identifier])())

    def __repr__(self):
        return np("<(%s, %s)" % tuple(self.subs))


class Greater(Expression):
    def __init__(self):
        Expression.__init__(self)
        for i in xrange(2):
            if randint(1, 8) == 1:
                self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
            else:
                self.subs.append(choice([Number, Identifier])())

    def __repr__(self):
        return np(">(%s, %s)" % tuple(self.subs))


class Plus(Expression):
    def _add_sub(self):
        if randint(1, 8) == 1:
            self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
        else:
            self.subs.append(choice([self.style, Identifier])())

    def __init__(self):
        Expression.__init__(self)
        self.style = choice([String, Number])
        if randint(1, 30) < 30:
            self._add_sub()
        while choice([True, False]):
            self._add_sub()

    def __repr__(self):
        return np("+(%s)" % commastring(self.subs))


class Minus(Expression):
    def _add_sub(self):
        if randint(1, 8) == 1:
            self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
        else:
            self.subs.append(choice([Number, Identifier])())

    def __init__(self):
        Expression.__init__(self)
        if randint(1, 8) == 1:
            self._add_sub()
        while choice([True, False]):
            self._add_sub()

    def __repr__(self):
        return np("+(%s)" % commastring(self.subs))


class Equals(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(get_random_expression([Chain, DefFun, DefVar]))
        self.subs.append(get_random_expression([Chain, DefFun, DefVar]))

    def __repr__(self):
        return np("==(%s, %s)" % tuple(self.subs))


class Print(Expression):
    def __init__(self):
        Expression.__init__(self)
        self.subs.append(get_random_expression([Chain, DefFun, DefVar]))

    def __repr__(self):
        return np("print(%s)" % tuple(self.subs))


class Identifier(Expression):
    def __init__(self, force_new=False, skip=False):
        if skip:
            return
        Expression.__init__(self)
        if force_new:
            self.name = get_new_identifier()
        else:
            self.name = get_identifier()

    def __repr__(self):
        return np(self.name)

l_all_expressions = [
    Number,
    String,
    Bool,
    Chain,
    If,
    For,
    While,
    Lambda,
    Application,
    DefFun,
    DefVar,
    Object,
    AtWithIdentifier,
    AtWithString,
    DotWithIdentifier,
    DotWithIdentifierFun,
    DotWithString,
    DotWithStringFun,
    Assign,
    PlusEquals,
    MinusEquals,
    PostIncrement,
    PostDecrement,
    PreIncrement,
    PreDecrement,
    Less,
    Greater,
    Plus,
    Minus,
    Equals,
    Print,
    Identifier,
]
all_expressions = set(l_all_expressions)

newest = Number
# myexp = get_random_type([])()
myexp = If()
if len(identifiers) > 0:
    ident_obj = Identifier(skip=True)
    ident_obj.name = identifiers[0]
    dv = DefVar(skip=True)
    dv.subs = [
        ident_obj,
        choice([Bool, Number])(),
        myexp,
        ]
    myexp = dv
    for ident in identifiers[1:]:
        ident_obj = Identifier(skip=True)
        ident_obj.name = ident
        dv = DefVar(skip=True)
        dv.subs = [
            ident_obj,
            choice([Bool, Number, String])(),
            myexp,
            ]
        myexp = dv

# print "Ifs: %s/%s (%s)" % (ifs_made, types_made, 1.0 * ifs_made / types_made)
# print "Obj: %s/%s (%s)" % (objects_made, types_made, 1.0 * objects_made / types_made)


write_to_file(myexp)
