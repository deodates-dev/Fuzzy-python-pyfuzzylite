"""
 pyfuzzylite (TM), a fuzzy logic control library in Python.
 Copyright (C) 2010-2017 FuzzyLite Limited. All rights reserved.
 Author: Juan Rada-Vilela, Ph.D. <jcrada@fuzzylite.com>

 This file is part of pyfuzzylite.

 pyfuzzylite is free software: you can redistribute it and/or modify it under
 the terms of the FuzzyLite License included with the software.

 You should have received a copy of the FuzzyLite License along with
 pyfuzzylite. If not, see <http://www.fuzzylite.com/license/>.

 pyfuzzylite is a trademark of FuzzyLite Limited
 fuzzylite is a registered trademark of FuzzyLite Limited.
"""

import typing
from typing import Optional

from .operation import Op

if typing.TYPE_CHECKING:
    from .activation import Activation  # noqa: F401
    from .defuzzifier import Defuzzifier  # noqa: F401
    from .engine import Engine
    from .norm import Norm  # noqa: F401
    from .rule import Rule, RuleBlock
    from .term import Term
    from .variable import InputVariable, OutputVariable, Variable


class Exporter(object):
    pass


class FllExporter(Exporter):
    __slots__ = ["indent", "separator"]

    def __init__(self, indent: str = "  ", separator: str = "\n") -> None:
        self.indent = indent
        self.separator = separator

    def to_string(self, instance: object) -> str:
        from .engine import Engine
        if isinstance(instance, Engine):
            return self.engine(instance)

        from .variable import InputVariable, OutputVariable, Variable
        if isinstance(instance, InputVariable):
            return self.input_variable(instance)
        if isinstance(instance, OutputVariable):
            return self.output_variable(instance)
        if isinstance(instance, Variable):
            return self.variable(instance)

        from .term import Term
        if isinstance(instance, Term):
            return self.term(instance)

        from .defuzzifier import Defuzzifier  # noqa: F811
        if isinstance(instance, Defuzzifier):
            return self.defuzzifier(instance)

        from .rule import RuleBlock, Rule
        if isinstance(instance, RuleBlock):
            return self.rule_block(instance)
        if isinstance(instance, Rule):
            return self.rule(instance)

        from .norm import Norm  # noqa: F811
        if isinstance(instance, Norm):
            return self.norm(instance)

        from .activation import Activation  # noqa: F811
        if isinstance(instance, Activation):
            return self.activation(instance)

        raise ValueError(f"expected a fuzzylite object, but found '{type(instance).__name__}'")

    def engine(self, engine: 'Engine') -> str:
        result = [f"Engine: {engine.name}"]
        if engine.description:
            result.append(f"description: {engine.description}")
        for input_variable in engine.input_variables:
            result.append(self.input_variable(input_variable))
        for output_variable in engine.output_variables:
            result.append(self.output_variable(output_variable))
        for rule_block in engine.rule_blocks:
            result.append(self.rule_block(rule_block))
        return self.separator.join(result)

    def variable(self, v: 'Variable') -> str:
        result = [f"Variable: {v.name}"]
        if v.description:
            result.append(f"{self.indent}description: {v.description}")
        result.extend([
            f"{self.indent}enabled: {str(v.enabled).lower()}",
            f"{self.indent}range: {' '.join([Op.str(v.minimum), Op.str(v.maximum)])}",
            f"{self.indent}lock-range: {str(v.enabled).lower()}",
            *[f"{self.indent}{self.term(term)}" for term in v.terms]
        ])
        return self.separator.join(result)

    def input_variable(self, iv: 'InputVariable') -> str:
        result = [f"InputVariable: {iv.name}"]
        if iv.description:
            result.append(f"{self.indent}description: {iv.description}")
        result.extend([
            f"{self.indent}enabled: {str(iv.enabled).lower()}",
            f"{self.indent}range: {' '.join([Op.str(iv.minimum), Op.str(iv.maximum)])}",
            f"{self.indent}lock-range: {str(iv.lock_range).lower()}",
            *[f"{self.indent}{self.term(term)}" for term in iv.terms]
        ])
        return self.separator.join(result)

    def output_variable(self, ov: 'OutputVariable') -> str:
        result = [f"OutputVariable: {ov.name}"]
        if ov.description:
            result.append(f"{self.indent}description: {ov.description}")
        result.extend([
            f"{self.indent}enabled: {str(ov.enabled).lower()}",
            f"{self.indent}range: {' '.join([Op.str(ov.minimum), Op.str(ov.maximum)])}",
            f"{self.indent}lock-range: {str(ov.lock_range).lower()}",
            f"{self.indent}aggregation: {self.norm(ov.aggregation)}",
            f"{self.indent}defuzzifier: {self.defuzzifier(ov.defuzzifier)}",
            f"{self.indent}default: {Op.str(ov.default_value)}",
            f"{self.indent}lock-previous: {str(ov.lock_previous).lower()}",
            *[f"{self.indent}{self.term(term)}" for term in ov.terms]
        ])
        return self.separator.join(result)

    def rule_block(self, rb: 'RuleBlock') -> str:
        result = [f"RuleBlock: {rb.name}"]
        if rb.description:
            result.append(f"{self.indent}description: {rb.description}")
        result.extend([
            f"{self.indent}enabled: {str(rb.enabled).lower()}",
            f"{self.indent}conjunction: {self.norm(rb.conjunction)}",
            f"{self.indent}disjunction: {self.norm(rb.disjunction)}",
            f"{self.indent}implication: {self.norm(rb.implication)}",
            f"{self.indent}activation: {self.activation(rb.activation)}",
            *[f"{self.indent}{self.rule(rule)}" for rule in rb.rules]
        ])
        return self.separator.join(result)

    def term(self, term: 'Term') -> str:
        result = ["term:", Op.as_identifier(term.name), term.class_name]
        parameters = term.parameters()
        if parameters:
            result.append(parameters)
        return " ".join(result)

    def norm(self, norm: Optional['Norm']) -> str:
        return norm.class_name if norm else "none"

    def activation(self, activation: Optional['Activation']) -> str:
        return activation.class_name if activation else "none"

    def defuzzifier(self, defuzzifier: Optional['Defuzzifier']) -> str:
        if not defuzzifier:
            return "none"
        from .defuzzifier import IntegralDefuzzifier, WeightedDefuzzifier
        result = [defuzzifier.class_name]
        if isinstance(defuzzifier, IntegralDefuzzifier):
            result.append(str(defuzzifier.resolution))
        elif isinstance(defuzzifier, WeightedDefuzzifier):
            result.append(defuzzifier.type.name)
        return " ".join(result)

    def rule(self, rule: 'Rule') -> str:
        return f"rule: {rule.text}"
