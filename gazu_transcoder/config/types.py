from typing import TypedDict


class FunctionTargetConfig(TypedDict):
    define_key: str
    return_key: str
    argument_separator: str
    open_body: str
    close_body: str


class AssignementTargetConfig(TypedDict):
    assign_key: str
    multiple_assign_begin: str
    multiple_assign_end: str
    multiple_assign_join: str


class OperatorTargetConfig(TypedDict):
    # Binary operators
    add: str
    sub: str
    mult: str
    mat_mult: str
    div: str
    mod: str
    pow: str
    l_shift: str
    r_shift: str
    bit_or: str
    bit_xor: str
    bit_and: str
    bit_and: str
    floor_div: str
    # Boolean operators
    and_op: str
    or_op: str
    # Comparison operators
    equal: str
    not_equal: str
    lower_than: str
    lower_than_equal: str
    greater_than: str
    greater_than_equal: str
    is_op: str
    is_not_op: str
    in_op: str
    not_in_op: str


class PropertyAccessTargetConfig(TypedDict):
    subscript_open: str
    subscript_close: str
    attribute: str


class LiteralsTargetConfig(TypedDict):
    list_begin: str
    list_end: str
    list_join: str
    tuple_begin: str
    tuple_end: str
    tuple_join: str
    dict_begin: str
    dict_end: str
    dict_join: str
    dict_assign: str


class FlowTargetConfig(TypedDict):
    while_key: str
    while_begin: str
    while_end: str
    while_open_body: str
    while_close_body: str
    if_key: str
    if_begin: str
    if_end: str
    if_open_body: str
    if_close_body: str
    foreach_key: str
    foreach_begin: str
    foreach_end: str
    foreach_open_body: str
    foreach_close_body: str
    foreach_separator: str


class TranslationTargetConfig(TypedDict):
    function: FunctionTargetConfig
    assignement: AssignementTargetConfig
    operator: OperatorTargetConfig
    access: PropertyAccessTargetConfig
    literals: LiteralsTargetConfig
    flow: FlowTargetConfig
