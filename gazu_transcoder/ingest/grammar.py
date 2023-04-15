import ast
import re
from typing import Type

from gazu_transcoder.utils.logger import logger
from gazu_transcoder.config.types import TranslationTargetConfig


def get_attribute_templated_source(
    expression: ast.Attribute, config: TranslationTargetConfig
):
    return config["access"]["attribute"].join(
        [get_expression_templated_source(expression.value, config), expression.attr]
    )


def get_boolop_templated_source(
    expression: ast.BoolOp, config: TranslationTargetConfig
):
    operator = config["operator"]["and_op" if expression.op is ast.And else "or_op"]
    return operator.join(
        [get_expression_templated_source(value, config) for value in expression.values]
    )


def get_binop_templated_source(expression: ast.BinOp, config: TranslationTargetConfig):
    # We convert the name of the class to snake case in order to get the key that correspond to the config
    operator = config["operator"].get(
        re.sub(r"(?<!^)(?=[A-Z])", "_", type(expression.op).__name__).lower()
    )
    if operator is None:
        logger.error(
            "Could not build binop templated source: Unhandled operator %s",
            expression.op,
        )
        return ""
    return operator.join(
        [
            get_expression_templated_source(expression.left, config),
            get_expression_templated_source(expression.right, config),
        ]
    )


def get_compare_templated_source(
    expression: ast.Compare, config: TranslationTargetConfig
):
    # The name of the operator classes does not match the keys in the config
    config_map: dict[Type[ast.cmpop], str] = {
        ast.Eq: "equal",
        ast.NotEq: "not_equal",
        ast.Lt: "lower_than",
        ast.LtE: "lower_than_equal",
        ast.Gt: "greater_than",
        ast.GtE: "greater_than_equal",
        ast.Is: "is_op",
        ast.IsNot: "is_not_op",
        ast.In: "in_op",
        ast.NotIn: "not_in_op",
    }
    if len(expression.ops) > 1 or len(expression.comparators) > 1:
        logger.error(
            "Could not build comparison template: Comparison with multiple operators not supported"
        )
        return ""

    operator = config["operator"].get(config_map[type(expression.ops[0])])
    if operator is None:
        logger.error(
            "Could not build binop templated source: Unhandled operator %s",
            expression.ops[0],
        )
        return ""
    return operator.join(
        [
            get_expression_templated_source(expression.left, config),
            get_expression_templated_source(expression.comparators[0], config),
        ]
    )


def get_contant_templated_source(expression: ast.Constant, _: TranslationTargetConfig):
    return str(expression.value)


def get_dict_templated_source(expression: ast.Dict, config: TranslationTargetConfig):
    keypairs = []
    for key, value in zip(expression.keys, expression.values):
        if key is None:
            logger.error(
                "Could not build dict templated source %s: Values without keys not supported",
                expression,
            )
            continue
        keypairs.append(
            get_expression_templated_source(key, config)
            + config["literals"]["dict_assign"]
            + get_expression_templated_source(value, config)
        )

    return (
        config["literals"]["dict_begin"]
        + config["literals"]["dict_join"].join(keypairs)
        + config["literals"]["dict_end"]
    )


def get_list_templated_source(expression: ast.List, config: TranslationTargetConfig):
    return (
        config["literals"]["list_begin"]
        + config["literals"]["list_join"].join(
            [get_expression_templated_source(item, config) for item in expression.elts]
        )
        + config["literals"]["list_end"]
    )


def get_tuple_templated_source(expression: ast.Tuple, config: TranslationTargetConfig):
    return (
        config["literals"]["tuple_begin"]
        + config["literals"]["tuple_join"].join(
            [get_expression_templated_source(item, config) for item in expression.elts]
        )
        + config["literals"]["tuple_end"]
    )


def get_subscript_templated_source(
    expression: ast.Subscript, config: TranslationTargetConfig
):
    return (
        get_expression_templated_source(expression.value, config)
        + config["access"]["subscript_open"]
        + get_expression_templated_source(expression.slice, config)
        + config["access"]["subscript_close"]
    )


def get_name_templated_source(expression: ast.Name, _: TranslationTargetConfig):
    return expression.id


def get_call_templated_source(expression: ast.Call, config: TranslationTargetConfig):
    return (
        get_expression_templated_source(expression.func, config)
        + f"({config['function']['argument_separator'].join([get_expression_templated_source(arg, config) for arg in expression.args])})"
    )


def get_expression_templated_source(
    expression: ast.expr, config: TranslationTargetConfig
):
    if isinstance(expression, ast.Call):
        return get_call_templated_source(expression, config)
    if isinstance(expression, ast.Name):
        return get_name_templated_source(expression, config)
    if isinstance(expression, ast.Constant):
        return get_contant_templated_source(expression, config)
    if isinstance(expression, ast.Attribute):
        return get_attribute_templated_source(expression, config)
    if isinstance(expression, ast.BinOp):
        return get_binop_templated_source(expression, config)
    if isinstance(expression, ast.BoolOp):
        return get_boolop_templated_source(expression, config)
    if isinstance(expression, ast.Compare):
        return get_compare_templated_source(expression, config)
    if isinstance(expression, ast.Subscript):
        return get_subscript_templated_source(expression, config)
    if isinstance(expression, ast.Dict):
        return get_dict_templated_source(expression, config)
    if isinstance(expression, ast.List):
        return get_list_templated_source(expression, config)
    if isinstance(expression, ast.Tuple):
        return get_tuple_templated_source(expression, config)

    logger.error(
        "Could not build expression template for expression %s: Unhandled expression type (%s)",
        expression,
        type(expression),
    )
    return ""


def get_assign_templated_source(statement: ast.Assign, config: TranslationTargetConfig):
    target = config["assignement"]["multiple_assign_join"].join(
        [
            get_expression_templated_source(target, config)
            for target in statement.targets
        ]
    )
    if config["assignement"].get("multiple_assign_begin") and config["assignement"].get(
        "multiple_assign_end"
    ):
        target = (
            config["assignement"]["multiple_assign_begin"]
            + target
            + config["assignement"]["multiple_assign_end"]
        )

    return config["assignement"]["assign_key"].join(
        [target, get_expression_templated_source(statement.value, config)]
    )


def get_expr_templated_source(statement: ast.Expr, config: TranslationTargetConfig):
    return get_expression_templated_source(statement.value, config)


def get_return_templated_source(statement: ast.Return, config: TranslationTargetConfig):
    if statement.value:
        return config["function"]["return_key"] + get_expression_templated_source(
            statement.value, config
        )
    else:
        return config["function"]["return_key"]


def get_function_definition_templated_source(
    statement: ast.FunctionDef, config: TranslationTargetConfig
):
    # The name, the arguments, and the openning of the body (ex: def hello(foo, bar):)
    source = (
        config["function"]["define_key"]
        + statement.name
        + config["function"]["argument_separator"].join(
            [arg.arg for arg in statement.args.args]
        )
        + config["function"]["open_body"]
    )
    # The actual body of the function
    for index, body_statement in enumerate(statement.body):
        # Skip the docstring
        if isinstance(body_statement, ast.Expr) and index == 0:
            continue
        source += "\n\t" + get_statement_templated_source(body_statement, config)
    return source + config["function"]["close_body"]


def get_foreach_templated_source(statement: ast.For, config: TranslationTargetConfig):
    # The foreach statement
    source = (
        config["flow"]["foreach_key"]
        + config["flow"]["foreach_begin"]
        + get_expression_templated_source(statement.target, config)
        + config["flow"]["foreach_separator"]
        + get_expression_templated_source(statement.iter, config)
        + config["flow"]["foreach_end"]
        + config["flow"]["foreach_open_body"]
    )
    # The actual body of the loop
    for index, body_statement in enumerate(statement.body):
        # Skip the docstring
        if isinstance(body_statement, ast.Expr) and index == 0:
            continue
        source += "\n\t" + get_statement_templated_source(body_statement, config)
    return source + config["flow"]["foreach_close_body"]


def get_if_templated_source(statement: ast.If, config: TranslationTargetConfig):
    # The if statement
    source = (
        config["flow"]["if_key"]
        + config["flow"]["if_begin"]
        + get_expression_templated_source(statement.test, config)
        + config["flow"]["if_end"]
        + config["flow"]["if_open_body"]
    )
    # The actual body of the loop
    for index, body_statement in enumerate(statement.body):
        # Skip the docstring
        if isinstance(body_statement, ast.Expr) and index == 0:
            continue
        source += "\n\t" + get_statement_templated_source(body_statement, config)
    source += config["flow"]["if_close_body"]
    return source


def get_while_templated_source(statement: ast.While, config: TranslationTargetConfig):
    # The if statement
    source = (
        config["flow"]["while_key"]
        + config["flow"]["while_begin"]
        + get_expression_templated_source(statement.test, config)
        + config["flow"]["while_end"]
        + config["flow"]["while_open_body"]
    )
    # The actual body of the loop
    for index, body_statement in enumerate(statement.body):
        # Skip the docstring
        while isinstance(body_statement, ast.Expr) and index == 0:
            continue
        source += "\n\t" + get_statement_templated_source(body_statement, config)
    source += config["flow"]["while_close_body"]
    return source


def get_statement_templated_source(
    statement: ast.stmt, config: TranslationTargetConfig
):
    if isinstance(statement, ast.Return):
        return get_return_templated_source(statement, config)
    if isinstance(statement, ast.Expr):
        return get_expr_templated_source(statement, config)
    if isinstance(statement, ast.Assign):
        return get_assign_templated_source(statement, config)
    if isinstance(statement, ast.FunctionDef):
        return get_function_definition_templated_source(statement, config)
    if isinstance(statement, ast.For):
        return get_foreach_templated_source(statement, config)
    if isinstance(statement, ast.If):
        return get_if_templated_source(statement, config)
    if isinstance(statement, ast.While):
        return get_while_templated_source(statement, config)

    logger.error(
        "Could not build statement template for expression %s: Unhandled statement type (%s)",
        statement,
        type(statement),
    )
    return ""
