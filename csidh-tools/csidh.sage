
class CSIDH:
    def __init__(self, p, primes):
        self.p = p
        self.primes = primes
        self.Fp = GF(p)

    def get_public(self, private):
        """Computation of CSIDH public key

        We need to compute an Elliptic curve that is reached after
        $a_i$ isogenies of degree $l_i$ for $1 <= i <= r$

        We start at predefined curve $y^2 = x^3 + x$

        :private: secret exponent vector $(a_1, ..., a_r)$ for
        $a_i \in [-m, m]$
        :return: Elliptic curve represented by Montgomery coefficient
        """
        assert len(private) == len(self.primes)

        return self.group_action(0, private)

    def group_action(self, A, e):
        assert len(e) == len(self.primes)
        # We begin at the Elliptic curve y^2 = x^3 + A*x^2 + x
        # It should be validated that the curve is supersingular
        # before doing any computation. That could be apparently
        # done via sampling random points and checking that all
        # primes $l_i$ appear in group order, and/or using Hasse
        # interval
        E = EllipticCurve(self.Fp, [0, A, 0, 1, 0])
        # We loop until we have no more isogenies to perform,
        # that is if the vector e is zero.
        #
        # The reason we do all the isogenies of same sign should
        # be because of optimization reasons, we could always do it
        # in a way where we compute for each $l_i$-isogeny separately,
        # but here it is done so that we create a point T, of degree
        # prod(l_i having same sign in the exponent) and computing
        # with this point all the $l_i$-isogenies, thus spending
        # less time on finding points and doing scalar multiplications
        while any([e_i != 0 for e_i in e]):
            x = self.Fp.random_element()
            s = 1 if self.Fp(x**3 + A*x**2 + x).is_square() else -1
            S = [i for i in range(len(e)) if e[i] != 0 and sign(e[i]) == s]

            if S == []:
                continue

            if s == -1:
                E = E.quadratic_twist()

            P = E.random_element()
            while P.is_zero():
                P = E.random_element()

            k = prod([self.primes[i] for i in S])
            T = ((self.p + 1) // k) * P

            for i in S:
                assert k % self.primes[i] == 0

                R = (k // self.primes[i]) * T
                if R.is_zero():
                    continue
                phi = E.isogeny(R)
                E, T = phi.codomain(), phi(T)
                k = k // self.primes[i]
                e[i] = e[i] - s

            if s == -1:
                E = E.quadratic_twist()
                

        return E.montgomery_model().a2()

if __name__ == '__main__':
    csidh = CSIDH(419, [3,5,7])
    key = [10,-6,2]
    public = csidh.group_action(0, key)
    print("Public key = ", public)
    m = 4
    distance = 4
    res = {}
    cnt = 0
    for x in range(-m,m+1):
        three_isog = "" if x == 0 else "("+ ("-" if x > 0 else "+") *abs(x)  + ")" + "3"
        for y in range(-m,m+1):
            five_isog = "" if y == 0 else "("+ ("-" if y > 0 else "+") *abs(y) + ")" + "5"
            for z in range(-m,m+1):
                seven_isog = "" if z == 0 else "("+ ("-" if z > 0 else "+") *abs(z)  + ")" + "7"
                only_one_degree = (x and not y and not z) or (not x and y and not z) or (not x and not y and z)
                if abs(x) + abs(y) + abs(z) <= distance and only_one_degree:
                    cnt += 1
                    e = csidh.group_action(public, [x,y,z])
                    print(x,y,z,e)
                    x= x * -1
                    y= y * -1
                    z= z * -1
                    if e in res:
                        new = (res[e][0] + f"/{three_isog}{five_isog}{seven_isog}", res[e][1] + [3**x*5**y*7**z])
                        res[e] = new
                    else:
                        res[e] = (f"{three_isog}{five_isog}{seven_isog}", [3**x*5**y*7**z])
    for k,v in res.items():
        print(k,v)
    print(len(res), cnt)
         
    
