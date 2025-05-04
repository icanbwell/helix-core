from enum import Enum


class StringMatchType(Enum):
    NoMatch = "no-match"
    Exact = "exact-match"
    Partial = "partial-match"
    Synonym = "synonym-match"
