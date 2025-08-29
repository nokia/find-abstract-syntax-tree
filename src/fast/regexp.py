#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Functions used to craft automata from regular expressions."""

from string import printable
from pybgl import (
    Automaton,
    compile_dfa,
)


def make_re_hex_digit(lower_case: bool = True, upper_case: bool = True) -> str:
    """
    Builds the regular expression catching hexadecimal values.

    Args:
        lower_case (bool): Pass ``False`` to discard lower case values.
        upper_case (bool): Pass ``False`` to discard upper case values.

    Returns:
        The string storing the regular expression.
    """
    return r"[0-9%s%s]" % (
        "a-f" if lower_case else "",
        "A-F" if upper_case else ""
    )


def make_re_ipv6(lower_case: bool = True, upper_case: bool = True) -> str:
    """
    Builds the regular expression catching IPv6 addresses.

    Note this is not an exact match contrary to
    :py:class:`make_re_ipv6_strict`, but the resulting automaton is
    significantly faster (and should be accurate
    enough for most of practical use cases).

    Args:
        lower_case (bool): Pass ``False`` to discard lower case values.
        upper_case (bool): Pass ``False`` to discard upper case values.

    Returns:
        The string storing the regular expression.
    """
    assert lower_case or upper_case
    hex4 = "[%s%s0-9]{0,4}" % (
        "a-f" if lower_case else "",
        "A-F" if upper_case else ""
    )
    ipv6_sep = ":"
    return "((" + hex4 + ")?(" + ipv6_sep + hex4 + ")+" + ipv6_sep + hex4 + ")"


# Avoid to use it (long to compile, long to compute language_density)
def make_re_ipv6_strict(*args, **kwargs) -> str:
    """
    Builds the regular expression catching IPv6 addresses.

    Args:
        args: See :py:func:`make_re_hex_digit`.
        kwargs: See :py:func:`make_re_hex_digit`.

    Returns:
        The string storing the regular expression.
    """
    re_seg = make_re_hex_digit(*args, **kwargs) + r"{1,4}"
    return "(%s)" % "|".join([
        "(" + re_seg + ":){7,7}" + re_seg,
        # 1:2:3:4:5:6:7:8
        "(" + re_seg + ":){1,7}:",
        # 1::                                 1:2:3:4:5:6:7::
        "(" + re_seg + ":){1,6}:" + re_seg,
        # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
        "(" + re_seg + ":){1,5}(:" + re_seg + "){1,2}",
        # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
        "(" + re_seg + ":){1,4}(:" + re_seg + "){1,3}",
        # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
        "(" + re_seg + ":){1,3}(:" + re_seg + "){1,4}",
        # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
        "(" + re_seg + ":){1,2}(:" + re_seg + "){1,5}",
        # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
        re_seg + ":((:" + re_seg + "){1,6})",
        # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
        ":((:" + re_seg + "){1,7}|:)",
        #: :2:3:4:5:6:7:8   : :2:3:4:5:6:7:8 : :8      : :
        # fe80::7:8%eth0 fe80::7:8%1
        # (link-local IPv6 addresses with zone index)
        "fe80:(:" + re_seg + "){0,4}%[0-9a-zA-Z]{1,}",
        #: :255.255.255.255 : :ffff:255.255.255.255 : :ffff:0:255.255.255.255
        # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
        "::(ffff(:0{1,4}){0,1}:){0,1}" + RE_IPV4,
        #  2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
        # (IPv4-Embedded IPv6 Address)
        "(re_seg:){1,4}:" + RE_IPV4
    ])


RE_0_32 = r"(3[0-2]|[0-2]?[0-9])"
RE_0_128 = r"(12[0-8]|1[0-1][0-9]|([0-9]{1,2}))"
RE_0_255 = r"(25[0-5]|(2[0-4]|[0-1]{0,1}[0-9]){0,1}[0-9])"
RE_ALNUM = r"[a-zA-Z0-9]+"
RE_ANY = r"(\S|\s)+"  # The metacharacter "." is not yet supported in pybgl
RE_BOOL = r"0|1"
RE_DELIMITER = r"[-]+|[+]+|[=]+|[@]+|[~]+|[#]+"
RE_SIGN = r"(-|[+])?"
RE_UINT = r"[0-9]+"
RE_INT = RE_SIGN + RE_UINT
RE_FLOAT = RE_SIGN + RE_UINT + r"([.]" + RE_UINT + ")?"
RE_HEXA = make_re_hex_digit() + r"+"
RE_IPV4 = r"((" + RE_0_255 + "[.]){3}" + RE_0_255 + ")"
RE_IPV6 = make_re_ipv6()  # make_re_ipv6_strict()
RE_LETTERS = r"[a-zA-Z]+"
RE_NET_IPV4 = "/".join([RE_IPV4, RE_0_32])
RE_NET_IPV6 = "/".join([RE_IPV6, RE_0_128])
RE_PATH = r"(/[-/:._a-zA-Z0-9]+)"
RE_SPACES = r"\s+"
RE_WORD = r"\S+"

MAP_NAME_RE = {
    "alnum": RE_ALNUM,
    "any": RE_ANY,
    "bool": RE_BOOL,
    "delimiter": RE_DELIMITER,
    "float": RE_FLOAT,
    "hexa": RE_HEXA,
    "int": RE_INT,
    "ipv4": RE_IPV4,
    "ipv6": RE_IPV6,
    "letters": RE_LETTERS,
    "net_ipv4": RE_NET_IPV4,
    "net_ipv6": RE_NET_IPV6,
    "path": RE_PATH,
    "uint": RE_UINT,
    "spaces": RE_SPACES,
    "word": RE_WORD,
}


def get_pattern_names() -> list:
    """
    Retrieves the list of patterns involved in the default pattern collection.

    Returns:
        A list of string, where each string correspond to a pattern name
        involved in the default pattern collection (``MAP_NAME_RE``).
    """
    return list(MAP_NAME_RE.keys())


def make_map_name_dfa(names: iter = None) -> dict:
    """
    Builds a dictionary that maps a list of pattern name with the
    corresponding :py:class:`Automaton` instance built according to
    regular expressions.

    Args:
        names (list): A list of string, where each string identifies
            a pattern names (by default, every keys of ``map_name_re``
            is considered).

    Returns:
        The dictionary mapping each pattern name with its
        corresponding DFA.
    """
    if not names:
        names = list(MAP_NAME_RE.keys())
    map_name_dfa = dict()
    for name in names:
        try:
            regex = MAP_NAME_RE[name]
            map_name_dfa[name] = compile_dfa(regex)
        except Exception as e:
            raise Exception("Error when processing %r: %s" % (name, e))
    return map_name_dfa


def make_dfa_empty() -> Automaton:
    """
    Builds the :py:class:`Automaton` corresponding to the empty language.

    Returns:
        The corresponding :py:class:`Automaton`.
    """
    dfa_empty = Automaton(1)
    dfa_empty.set_final(0, False)
    return dfa_empty


def make_dfa_any(
    alphabet: iter = None,
    separator_alphabet: iter = None
) -> Automaton:
    """
    Builds the DFA corresponding to the any non-separator character.

    Args:
        alphabet (iter): The characters involved in the alphabet.
            Default to ``string.printable``).
        separator (iter): The characters corresponding to separators.
            Defaults to ``{" ", "\\t", "\\n"}``.

    Returns:
        The corresponding :py:class:`Automaton`.
    """
    if not alphabet:
        alphabet = set(printable)
    if not separator_alphabet:
        separator_alphabet = {" ", "\t", "\n"}
    dfa_any = Automaton(2)
    dfa_any.set_final(1)
    restricted_alphabet = sorted(set(alphabet) - set(separator_alphabet))
    for a in restricted_alphabet:
        dfa_any.add_edge(0, 1, a)
        dfa_any.add_edge(1, 1, a)
    return dfa_any
