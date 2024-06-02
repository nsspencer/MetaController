PARTITION_NAME = "partition"
CHOSEN_NAME = "chosen"
GENERATED_FUNCTION_NAME = "call_fn"
CLASS_ARG_NAME = "self"
POSITIONAL_ARG_PREFIX = "_ctrl_arg_"
VAR_ARG_NAME = "args"
KWARG_NAME = "kwargs"
MANGLED_KWARG_NAME = "_mangled_ctrl_kwd_"
MAX_CHOSEN_ARG_NAME = "k"

ACTION_FN_NAME = "action"
FILTER_FN_NAME = "filter"
SORT_CMP_FN_NAME = "sort_cmp"
SORT_KEY_FN_NAME = "sort_key"
CONTROLLED_METHODS = set(
    [
        ACTION_FN_NAME,
        FILTER_FN_NAME,
        SORT_CMP_FN_NAME,
        SORT_KEY_FN_NAME,
    ]
)
