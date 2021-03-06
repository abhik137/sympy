from sympy import (abc, Add, cos, Derivative, diff, exp, Float, Function,
    I, Integer, log, Mul, oo, Poly, Rational, S, sin, sqrt, Symbol, symbols,
    Wild, pi
)
from sympy.utilities.pytest import XFAIL


def test_symbol():
    x = Symbol('x')
    a, b, c, p, q = map(Wild, 'abcpq')

    e = x
    assert e.match(x) == {}
    assert e.matches(x) == {}
    assert e.match(a) == {a: x}

    e = Rational(5)
    assert e.match(c) == {c: 5}
    assert e.match(e) == {}
    assert e.match(e + 1) is None


def test_add():
    x, y, a, b, c = map(Symbol, 'xyabc')
    p, q, r = map(Wild, 'pqr')

    e = a + b
    assert e.match(p + b) == {p: a}
    assert e.match(p + a) == {p: b}

    e = 1 + b
    assert e.match(p + b) == {p: 1}

    e = a + b + c
    assert e.match(a + p + c) == {p: b}
    assert e.match(b + p + c) == {p: a}

    e = a + b + c + x
    assert e.match(a + p + x + c) == {p: b}
    assert e.match(b + p + c + x) == {p: a}
    assert e.match(b) is None
    assert e.match(b + p) == {p: a + c + x}
    assert e.match(a + p + c) == {p: b + x}
    assert e.match(b + p + c) == {p: a + x}

    e = 4*x + 5
    assert e.match(4*x + p) == {p: 5}
    assert e.match(3*x + p) == {p: x + 5}
    assert e.match(p*x + 5) == {p: 4}


def test_power():
    x, y, a, b, c = map(Symbol, 'xyabc')
    p, q, r = map(Wild, 'pqr')

    e = (x + y)**a
    assert e.match(p**q) == {p: x + y, q: a}
    assert e.match(p**p) is None

    e = (x + y)**(x + y)
    assert e.match(p**p) == {p: x + y}
    assert e.match(p**q) == {p: x + y, q: x + y}

    e = (2*x)**2
    assert e.match(p*q**r) == {p: 4, q: x, r: 2}

    e = Integer(1)
    assert e.match(x**p) == {p: 0}


def test_match_exclude():

    x = Symbol('x')
    y = Symbol('y')
    p = Wild("p", exclude=[x, y])
    q = Wild("q", exclude=[x, y])
    r = Wild("r", exclude=[x, y])

    e = 3/(4*x + 5)
    assert e.match(3/(p*x + q)) == {p: 4, q: 5}

    e = 3/(4*x + 5)
    assert e.match(p/(q*x + r)) == {p: 3, q: 4, r: 5}

    e = 2/(x + 1)
    assert e.match(p/(q*x + r)) == {p: 2, q: 1, r: 1}

    e = 1/(x + 1)
    assert e.match(p/(q*x + r)) == {p: 1, q: 1, r: 1}

    e = 4*x + 5
    assert e.match(p*x + q) == {p: 4, q: 5}

    e = 4*x + 5*y + 6
    assert e.match(p*x + q*y + r) == {p: 4, q: 5, r: 6}


def test_mul():
    x, y, a, b, c = map(Symbol, 'xyabc')
    p, q = map(Wild, 'pq')

    e = 4*x
    assert e.match(p*x) == {p: 4}
    assert e.match(p*y) is None
    assert e.match(e + p*y) == {p: 0}

    e = a*x*b*c
    assert e.match(p*x) == {p: a*b*c}
    assert e.match(c*p*x) == {p: a*b}

    e = (a + b)*(a + c)
    assert e.match((p + b)*(p + c)) == {p: a}

    e = x
    assert e.match(p*x) == {p: 1}

    e = exp(x)
    assert e.match(x**p*exp(x*q)) == {p: 0, q: 1}

    e = I*Poly(x, x)
    assert e.match(I*p) == {p: Poly(x, x)}


def test_mul_noncommutative():
    x, y = symbols('x y')
    A, B = symbols('A B', commutative=False)
    u, v = symbols('u v', cls=Wild)
    w = Wild('w', commutative=False)

    assert (u*v).matches(x) in ({v: x, u: 1}, {u: x, v: 1})
    assert (u*v).matches(x*y) in ({v: y, u: x}, {u: y, v: x})
    assert (u*v).matches(A) is None
    assert (u*v).matches(A*B) is None
    assert (u*v).matches(x*A) is None
    assert (u*v).matches(x*y*A) is None
    assert (u*v).matches(x*A*B) is None
    assert (u*v).matches(x*y*A*B) is None

    assert (v*w).matches(x) is None
    assert (v*w).matches(x*y) is None
    assert (v*w).matches(A) == {w: A, v: 1}
    assert (v*w).matches(A*B) == {w: A*B, v: 1}
    assert (v*w).matches(x*A) == {w: A, v: x}
    assert (v*w).matches(x*y*A) == {w: A, v: x*y}
    assert (v*w).matches(x*A*B) == {w: A*B, v: x}
    assert (v*w).matches(x*y*A*B) == {w: A*B, v: x*y}

    assert (v*w).matches(-x) is None
    assert (v*w).matches(-x*y) is None
    assert (v*w).matches(-A) == {w: A, v: -1}
    assert (v*w).matches(-A*B) == {w: A*B, v: -1}
    assert (v*w).matches(-x*A) == {w: A, v: -x}
    assert (v*w).matches(-x*y*A) == {w: A, v: -x*y}
    assert (v*w).matches(-x*A*B) == {w: A*B, v: -x}
    assert (v*w).matches(-x*y*A*B) == {w: A*B, v: -x*y}


def test_complex():
    a, b, c = map(Symbol, 'abc')
    x, y = map(Wild, 'xy')

    assert (1 + I).match(x + I) == {x: 1}
    assert (a + I).match(x + I) == {x: a}
    assert (2*I).match(x*I) == {x: 2}
    assert (a*I).match(x*I) == {x: a}
    assert (a*I).match(x*y) == {x: I, y: a}
    assert (2*I).match(x*y) == {x: 2, y: I}

    #Result is ambiguous, so we need to use Wild's exclude keyword
    x = Wild('x', exclude=[I])
    y = Wild('y', exclude=[I])
    assert (a + b*I).match(x + y*I) == {x: a, y: b}


def test_functions():
    from sympy.core.function import WildFunction
    x = Symbol('x')
    g = WildFunction('g')
    p = Wild('p')
    q = Wild('q')

    f = cos(5*x)
    notf = x
    assert f.match(p*cos(q*x)) == {p: 1, q: 5}
    assert f.match(p*g) == {p: 1, g: cos(5*x)}
    assert notf.match(g) is None


@XFAIL
def test_functions_X1():
    from sympy.core.function import WildFunction
    x = Symbol('x')
    g = WildFunction('g')
    p = Wild('p')
    q = Wild('q')

    f = cos(5*x)
    assert f.match(p*g(q*x)) == {p: 1, g: cos, q: 5}


def test_interface():
    x, y = map(Symbol, 'xy')
    p, q = map(Wild, 'pq')

    assert (x + 1).match(p + 1) == {p: x}
    assert (x*3).match(p*3) == {p: x}
    assert (x**3).match(p**3) == {p: x}
    assert (x*cos(y)).match(p*cos(q)) == {p: x, q: y}

    assert (x*y).match(p*q) in [{p:x, q:y}, {p:y, q:x}]
    assert (x + y).match(p + q) in [{p:x, q:y}, {p:y, q:x}]
    assert (x*y + 1).match(p*q) in [{p:1, q:1 + x*y}, {p:1 + x*y, q:1}]


def test_derivative1():
    x, y = map(Symbol, 'xy')
    p, q = map(Wild, 'pq')

    f = Function('f', nargs=1)
    fd = Derivative(f(x), x)

    assert fd.match(p) == {p: fd}
    assert (fd + 1).match(p + 1) == {p: fd}
    assert (fd).match(fd) == {}
    assert (3*fd).match(p*fd) is not None
    p = Wild("p", exclude=[x])
    q = Wild("q", exclude=[x])
    assert (3*fd - 1).match(p*fd + q) == {p: 3, q: -1}


def test_derivative_bug1():
    f = Function("f")
    x = Symbol("x")
    a = Wild("a", exclude=[f, x])
    b = Wild("b", exclude=[f])
    pattern = a * Derivative(f(x), x, x) + b
    expr = Derivative(f(x), x) + x**2
    d1 = {b: x**2}
    d2 = pattern.xreplace(d1).matches(expr, d1)
    assert d2 is None


def test_derivative2():
    f = Function("f")
    x = Symbol("x")
    a = Wild("a", exclude=[f, x])
    b = Wild("b", exclude=[f])
    e = Derivative(f(x), x)
    assert e.match(Derivative(f(x), x)) == {}
    assert e.match(Derivative(f(x), x, x)) is None
    e = Derivative(f(x), x, x)
    assert e.match(Derivative(f(x), x)) is None
    assert e.match(Derivative(f(x), x, x)) == {}
    e = Derivative(f(x), x) + x**2
    assert e.match(a*Derivative(f(x), x) + b) == {a: 1, b: x**2}
    assert e.match(a*Derivative(f(x), x, x) + b) is None
    e = Derivative(f(x), x, x) + x**2
    assert e.match(a*Derivative(f(x), x) + b) is None
    assert e.match(a*Derivative(f(x), x, x) + b) == {a: 1, b: x**2}


def test_match_deriv_bug1():
    n = Function('n')
    l = Function('l')

    x = Symbol('x')
    p = Wild('p')

    e = diff(l(x), x)/x - diff(diff(n(x), x), x)/2 - \
        diff(n(x), x)**2/4 + diff(n(x), x)*diff(l(x), x)/4
    e = e.subs(n(x), -l(x)).doit()
    t = x*exp(-l(x))
    t2 = t.diff(x, x)/t
    assert e.match( (p*t2).expand() ) == {p: -Rational(1)/2}


def test_match_bug2():
    x, y = map(Symbol, 'xy')
    p, q, r = map(Wild, 'pqr')
    res = (x + y).match(p + q + r)
    assert (p + q + r).subs(res) == x + y


def test_match_bug3():
    x, a, b = map(Symbol, 'xab')
    p = Wild('p')
    assert (b*x*exp(a*x)).match(x*exp(p*x)) is None


def test_match_bug4():
    x = Symbol('x')
    p = Wild('p')
    e = x
    assert e.match(-p*x) == {p: -1}


def test_match_bug5():
    x = Symbol('x')
    p = Wild('p')
    e = -x
    assert e.match(-p*x) == {p: 1}


def test_match_bug6():
    x = Symbol('x')
    p = Wild('p')
    e = x
    assert e.match(3*p*x) == {p: Rational(1)/3}


def test_behavior1():
    x = Symbol('x')
    p = Wild('p')
    e = 3*x**2
    a = Wild('a', exclude=[x])
    assert e.match(a*x) is None
    assert e.match(p*x) == {p: 3*x}


def test_behavior2():
    x = Symbol('x')
    p = Wild('p')

    e = Rational(6)
    assert e.match(2*p) == {p: 3}

    e = 3*x + 3 + 6/x
    a = Wild('a', exclude=[x])
    assert e.expand().match(a*x**2 + a*x + 2*a) is None
    assert e.expand().match(p*x**2 + p*x + 2*p) == {p: 3/x}


def test_match_polynomial():
    x = Symbol('x')
    a = Wild('a', exclude=[x])
    b = Wild('b', exclude=[x])
    c = Wild('c', exclude=[x])
    d = Wild('d', exclude=[x])

    eq = 4*x**3 + 3*x**2 + 2*x + 1
    pattern = a*x**3 + b*x**2 + c*x + d
    assert eq.match(pattern) == {a: 4, b: 3, c: 2, d: 1}
    assert (eq - 3*x**2).match(pattern) == {a: 4, b: 0, c: 2, d: 1}
    assert (x + sqrt(2) + 3).match(a + b*x + c*x**2) == \
        {b: 1, a: sqrt(2) + 3, c: 0}


def test_exclude():
    x, y, a = map(Symbol, 'xya')
    p = Wild('p', exclude=[1, x])
    q = Wild('q', exclude=[x])
    r = Wild('r', exclude=[sin, y])

    assert sin(x).match(r) is None
    assert cos(y).match(r) is None

    e = 3*x**2 + y*x + a
    assert e.match(p*x**2 + q*x + r) == {p: 3, q: y, r: a}

    e = x + 1
    assert e.match(x + p) is None
    assert e.match(p + 1) is None
    assert e.match(x + 1 + p) == {p: 0}

    e = cos(x) + 5*sin(y)
    assert e.match(r) is None
    assert e.match(cos(y) + r) is None
    assert e.match(r + p*sin(q)) == {r: cos(x), p: 5, q: y}


def test_floats():
    a, b = map(Wild, 'ab')

    e = cos(0.12345, evaluate=False)**2
    r = e.match(a*cos(b)**2)
    assert r == {a: 1, b: Float(0.12345)}


def test_Derivative_bug1():
    f = Function("f")
    x = abc.x
    a = Wild("a", exclude=[f(x)])
    b = Wild("b", exclude=[f(x)])
    eq = f(x).diff(x)
    assert eq.match(a*Derivative(f(x), x) + b) == {a: 1, b: 0}


def test_match_wild_wild():
    p = Wild('p')
    q = Wild('q')
    r = Wild('r')

    assert p.match(q + r) in [ {q: p, r: 0}, {q: 0, r: p} ]
    assert p.match(q*r) in [ {q: p, r: 1}, {q: 1, r: p} ]

    p = Wild('p')
    q = Wild('q', exclude=[p])
    r = Wild('r')

    assert p.match(q + r) == {q: 0, r: p}
    assert p.match(q*r) == {q: 1, r: p}

    p = Wild('p')
    q = Wild('q', exclude=[p])
    r = Wild('r', exclude=[p])

    assert p.match(q + r) is None
    assert p.match(q*r) is None


def test_combine_inverse():
    x, y = symbols("x y")
    assert Mul._combine_inverse(x*I*y, x*I) == y
    assert Mul._combine_inverse(x*I*y, y*I) == x
    assert Mul._combine_inverse(oo*I*y, y*I) == oo
    assert Mul._combine_inverse(oo*I*y, oo*I) == y
    assert Add._combine_inverse(oo, oo) == S(0)
    assert Add._combine_inverse(oo*I, oo*I) == S(0)


def test_issue_674():
    x = symbols('x')
    z, phi, r = symbols('z phi r')
    c, A, B, N = symbols('c A B N', cls=Wild)
    l = Wild('l', exclude=(0,))

    eq = z * sin(2*phi) * r**7
    matcher = c * sin(phi*N)**l * r**A * log(r)**B

    assert eq.match(matcher) == {c: z, l: 1, N: 2, A: 7, B: 0}
    assert (-eq).match(matcher) == {c: -z, l: 1, N: 2, A: 7, B: 0}
    assert (x*eq).match(matcher) == {c: x*z, l: 1, N: 2, A: 7, B: 0}
    assert (-7*x*eq).match(matcher) == {c: -7*x*z, l: 1, N: 2, A: 7, B: 0}

    matcher = c*sin(phi*N)**l * r**A

    assert eq.match(matcher) == {c: z, l: 1, N: 2, A: 7}
    assert (-eq).match(matcher) == {c: -z, l: 1, N: 2, A: 7}
    assert (x*eq).match(matcher) == {c: x*z, l: 1, N: 2, A: 7}
    assert (-7*x*eq).match(matcher) == {c: -7*x*z, l: 1, N: 2, A: 7}


def test_issue_784():
    from sympy.abc import gamma, mu, x
    f = (-gamma * (x - mu)**2 - log(gamma) + log(2*pi))/2
    a, b, c = symbols('a b c', cls=Wild, exclude=(gamma,))

    assert f.match(a * log(gamma) + b * gamma + c) == \
        {a: -S(1)/2, b: -(mu - x)**2/2, c: log(2*pi)/2}
    assert f.expand().collect(gamma).match(a * log(gamma) + b * gamma + c) == \
        {a: -S(1)/2, b: (-(x - mu)**2/2).expand(), c: (log(2*pi)/2).expand()}


def test_issue_1319():
    x = Symbol('x')
    a, b, c = symbols('a b c', cls=Wild, exclude=(x,))
    f, g = symbols('f g', cls=Function)

    eq = diff(g(x)*f(x).diff(x), x)

    assert eq.match(
        g(x).diff(x)*f(x).diff(x) + g(x)*f(x).diff(x, x) + c) == {c: 0}
    assert eq.match(a*g(x).diff(
        x)*f(x).diff(x) + b*g(x)*f(x).diff(x, x) + c) == {a: 1, b: 1, c: 0}


def test_issue_1601():
    f = Function('f')
    x = Symbol('x')
    a, b = symbols('a b', cls=Wild, exclude=(f(x),))

    p = a*f(x) + b
    eq1 = sin(x)
    eq2 = f(x) + sin(x)
    eq3 = f(x) + x + sin(x)
    eq4 = x + sin(x)

    assert eq1.match(p) == {a: 0, b: sin(x)}
    assert eq2.match(p) == {a: 1, b: sin(x)}
    assert eq3.match(p) == {a: 1, b: x + sin(x)}
    assert eq4.match(p) == {a: 0, b: x + sin(x)}


def test_issue_2069():
    a, b, c = symbols('a b c', cls=Wild)
    x = Symbol('x')
    f = Function('f')

    assert x.match(a) == {a: x}
    assert x.match(a*f(x)**c) == {a: x, c: 0}
    assert x.match(a*b) == {a: 1, b: x}
    assert x.match(a*b*f(x)**c) == {a: 1, b: x, c: 0}

    assert (-x).match(a) == {a: -x}
    assert (-x).match(a*f(x)**c) == {a: -x, c: 0}
    assert (-x).match(a*b) == {a: -1, b: x}
    assert (-x).match(a*b*f(x)**c) == {a: -1, b: x, c: 0}

    assert (2*x).match(a) == {a: 2*x}
    assert (2*x).match(a*f(x)**c) == {a: 2*x, c: 0}
    assert (2*x).match(a*b) == {a: 2, b: x}
    assert (2*x).match(a*b*f(x)**c) == {a: 2, b: x, c: 0}

    assert (-2*x).match(a) == {a: -2*x}
    assert (-2*x).match(a*f(x)**c) == {a: -2*x, c: 0}
    assert (-2*x).match(a*b) == {a: -2, b: x}
    assert (-2*x).match(a*b*f(x)**c) == {a: -2, b: x, c: 0}


def test_issue_1460():
    x = Symbol('x')
    e = Symbol('e')
    w = Wild('w', exclude=[x])
    y = Wild('y')

    # this is as it should be

    assert (3/x).match(w/y) == {w: 3, y: x}
    assert (3*x).match(w*y) == {w: 3, y: x}
    assert (x/3).match(y/w) == {w: 3, y: x}
    assert (3*x).match(y/w) == {w: S(1)/3, y: x}

    # these could be allowed to fail

    assert (x/3).match(w/y) == {w: S(1)/3, y: 1/x}
    assert (3*x).match(w/y) == {w: 3, y: 1/x}
    assert (3/x).match(w*y) == {w: 3, y: 1/x}

    # Note that solve will give
    # multiple roots but match only gives one:
    #
    # >>> solve(x**r-y**2,y)
    # [-x**(r/2), x**(r/2)]

    r = Symbol('r', rational=True)
    assert (x**r).match(y**2) == {y: x**(r/2)}
    assert (x**e).match(y**2) == {y: sqrt(x**e)}

    # since (x**i = y) -> x = y**(1/i) where i is an integer
    # the following should also be valid as long as y is not
    # zero when i is negative.

    a = Wild('a')

    e = S(0)
    assert e.match(a) == {a: e}
    assert e.match(1/a) is None
    assert e.match(a**.3) is None

    e = S(3)
    assert e.match(1/a) == {a: 1/e}
    assert e.match(1/a**2) == {a: 1/sqrt(e)}
    e = pi
    assert e.match(1/a) == {a: 1/e}
    assert e.match(1/a**2) == {a: 1/sqrt(e)}
    assert (-e).match(sqrt(a)) is None
    assert (-e).match(a**2) == {a: I*sqrt(pi)}


def test_issue_1784():
    a = Wild('a')
    x = Symbol('x')

    e = [i**2 for i in (x - 2, 2 - x)]
    p = [i**2 for i in (x - a, a- x)]
    for eq in e:
        for pat in p:
            assert eq.match(pat) == {a: 2}


def test_issue_1220():
    x, y = symbols('x y')

    p = -x*(S(1)/8 - y)
    ans = set([S.Zero, y - S(1)/8])

    def ok(pat):
        assert set(p.match(pat).values()) == ans

    ok(Wild("coeff", exclude=[x])*x + Wild("rest"))
    ok(Wild("w", exclude=[x])*x + Wild("rest"))
    ok(Wild("coeff", exclude=[x])*x + Wild("rest"))
    ok(Wild("w", exclude=[x])*x + Wild("rest"))
    ok(Wild("e", exclude=[x])*x + Wild("rest"))
    ok(Wild("ress", exclude=[x])*x + Wild("rest"))
    ok(Wild("resu", exclude=[x])*x + Wild("rest"))


def test_issue_679():
    p, c, q = symbols('p c q', cls=Wild)
    x = Symbol('x')

    assert (sin(x)**2).match(sin(p)*sin(q)*c) == {q: x, c: 1, p: x}
    assert (2*sin(x)).match(sin(p) + sin(q) + c) == {q: x, c: 0, p: x}


def test_issue_784():
    mu, gamma, x = symbols('mu gamma x')
    f = (- gamma * (x-mu)**2 - log(gamma) + log(2*pi)) / 2
    g1 = Wild('g1', exclude=[gamma])
    g2 = Wild('g2', exclude=[gamma])
    g3 = Wild('g3', exclude=[gamma])
    assert f.expand().match(g1 * log(gamma) + g2 * gamma + g3) == \
    {g3: log(2)/2 + log(pi)/2, g1: -S(1)/2, g2: -mu**2/2 + mu*x - x**2/2}


def test_issue_3004():
    x = Symbol('x')
    a = Wild('a')
    assert (-I*x*oo).match(I*a*oo) == {a: -x}


def test_issue_3539():
    a = Wild('a')
    x = Symbol('x')
    assert (x - 2).match(a - x) is None
    assert (6/x).match(a*x) is None
    assert (6/x**2).match(a/x) == {a: 6/x}
