#!/usr/bin/env pytest
# -*- coding: utf-8 -*-

from fast.regexp import *


def test_make_dfa_any():
    g = make_dfa_any()
    assert g.accepts("abc123")
    assert not g.accepts("abc de 123")
    assert not g.accepts("abc\t123")
    assert g.accepts("#!~@")

def test_re_0_n():
    map_max_re = {
        32 : RE_0_32,
        128 : RE_0_128,
        255 : RE_0_255,
    }
    for (n, regexp) in map_max_re.items():
        g = compile_dfa(regexp)
        for i in range(n + 1):
            assert g.accepts(str(i))
        assert not g.accepts("-1")
        assert not g.accepts(str(n+1))

def test_re_alnum():
    g = compile_dfa(RE_ALNUM)
    assert g.accepts("0")
    assert g.accepts("12")
    assert not g.accepts("-123")
    assert g.accepts("abc")
    assert g.accepts("x0y1z")

def test_re_delimiters():
    g = compile_dfa(RE_DELIMITER)
    assert g.accepts("---")
    assert g.accepts("======")

def test_re_hexa():
    g = compile_dfa(RE_HEXA)
    assert g.accepts("0")
    assert g.accepts("12")
    assert not g.accepts("-123")
    assert not g.accepts("+123")
    assert g.accepts("aa1234ff")
    assert not g.accepts("aa1234ffx")

def test_re_float():
    g = compile_dfa(RE_FLOAT)
    assert g.accepts("1")
    assert g.accepts("1.2")
    assert g.accepts("12.34")
    assert g.accepts("-12.34")
    assert not g.accepts(".34")
    assert not g.accepts("12.")

def test_re_int():
    g = compile_dfa(RE_INT)
    assert g.accepts("0")
    assert g.accepts("12")
    assert g.accepts("-123")
    assert g.accepts("+123")
    assert not g.accepts("123.4")

def test_re_ipv4():
    g = compile_dfa(RE_IPV4)
    assert g.accepts("192.168.0.255")
    assert g.accepts("190.068.0.255")
    assert g.accepts("0.0.0.0")
    assert g.accepts("255.255.255.255")
    assert not g.accepts("256.0.0.0")
    assert not g.accepts("0.256.0.0")
    assert not g.accepts("0.0.256.0")
    assert not g.accepts("0.0.0.256")

def test_re_ipv6():
    g = compile_dfa(RE_IPV6)
    assert g.accepts("::1")
    assert g.accepts("2a02:a802:23::1")
    assert g.accepts("2a01:e35:2e49:10c0:eeb3:6f16:6bd4:d833")
    assert g.accepts("2A01:E35:2E49:10C0:EEB3:6F16:6BD4:D833")
    assert not g.accepts("2A01:X35:2E49:10C0:EEB3:6F16:6BD4:D833")
    assert not g.accepts(":")
    assert not g.accepts("A")
    assert not g.accepts(":A")
    assert not g.accepts("1")
    assert not g.accepts(":1")

def test_re_net_ipv4():
    g = compile_dfa(RE_NET_IPV4)
    assert g.accepts("0.0.0.0") is False
    assert g.accepts("0.0.0.0/0") is True
    assert g.accepts("192.168.1.0/24") is True
    assert g.accepts("192.168.1.183/32") is True
    assert g.accepts("192.168.1.256/32") is False
    assert g.accepts("192.168.1.183/33") is False

def test_re_net_ipv6():
    g = compile_dfa(RE_NET_IPV6)
    assert g.accepts("2a02:a802:23::1") is False
    assert g.accepts("2a02:a802:23::1/44") is True
    assert g.accepts("2a02:a802:23::1/128") is True
    assert g.accepts("2a02:a802:23::1/0") is True
    assert g.accepts("2A02:A802:23::1/128") is True
    assert g.accepts("2x02:a802:23::1/128") is False
    assert g.accepts("2a02:a802:23::1/129") is False

def test_re_path():
    g = compile_dfa(RE_PATH)
    assert not g.accepts("aaa/bbb")
    assert g.accepts("/aaa/bbb")
    assert g.accepts("/my_folder0/my-subdir1")

def test_re_spaces():
    g = compile_dfa(RE_SPACES)
    assert g.accepts("  ")
    assert g.accepts("  \t  ")
    assert not g.accepts(" x \t y ")

def test_re_word():
    g = compile_dfa(RE_WORD)
    assert g.accepts("abc")
    assert not g.accepts("abc de")
    assert g.accepts("12")

def test_re_uint():
    g = compile_dfa(RE_UINT)
    assert g.accepts("0")
    assert g.accepts("12")
    assert not g.accepts("-123")
    assert not g.accepts("+123")
    assert not g.accepts("123.4")
