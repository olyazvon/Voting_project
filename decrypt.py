import sys
from pysnark.runtime import PrivVal, PubVal
from phe import paillier

with open('paillier_public_key.txt') as f:
    n = int(f.read())

g = n + 1

with open('paillier_private_key.txt') as f:
    p = int(f.readline())
    q = int(f.readline())

def l_function(x, p):
    return (x - 1) // p

def h_function(x, xsquare):
    return invert(l_function(powmod(g, x - 1, xsquare), x), x)

def crt(mp, mq):
    u = mulmod(mq - mp, invert(p, q), q)
    return mp + (u * p)

def mulmod(a, b, c):
    return a * b % c

def powmod(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if (exponent % 2) == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result

def invert(a, b):
    r, s, _ = extended_euclidean_algorithm(a, b)
    return s % b

def extended_euclidean_algorithm(a, b):
    r0, r1 = a, b
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q*r1
        s0, s1 = s1, s0 - q*s1
        t0, t1 = t1, t0 - q*t1
    return r0, s0, t0


def raw_decrypt(cipher):
    decrypt_to_p = mulmod(
        l_function(powmod(cipher, p-1, p ** 2), p),
        h_function(p, p ** 2),
        p)
    decrypt_to_q = mulmod(
        l_function(powmod(cipher, q-1, q ** 2), q),
        h_function(q, q ** 2),
        q)
    return crt(decrypt_to_p, decrypt_to_q)


def decrypt_results(cipher):
    PubVal(int(sys.argv[2]))
    PubVal(int(sys.argv[3]))
    cipher = PubVal(cipher)
    #key = PrivVal(key)
    result = raw_decrypt(cipher)
    d = result // 10000
    r = result % 10000
    d.val()
    r.val()

decrypt_results(int(sys.argv[1]))
