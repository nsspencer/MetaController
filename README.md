# Meta Controller

## Claims:

1) The right structure is important for modeling problems
2) Tightly coupled code is hard to read, reason about, update, and maintain
3) Python is a highly dynamic programming language, which should make it pair well to solving highly dynamic problems
4) Decoupled code is better than coupled code
5) Declarative programming is better than imparative programming
6) Most code has a dynamic lifetime (many changes); updates & maintenance can be a big time sink


## Code Generation Design choices:

### Arguments:

* All position only or non defaulted arguments must be named the same in each controlled method that uses them.
* You may use the same keyword argument among mulitple controlled methods as long as the default argument is equivalent (==)
* All defaulted arguments are converted to keyword only arguments and cannot be set positionally in the call method of the controller. Keyword only arguments 
* arg unpack and kwarg unpack must use the same name across all controlled methods

Arguments are resolved in the following order:
Pre controller
filter
sort_key
sort_cmp
action
fold
post_controller

### Controlled methods

*get_elements* starts off as the argument name of the partition.

#### Pre Controller

* always a function call before any other code is run
* This method receives no arguments
* warn if this method has a return, since its ignored

#### Filter

This method receives one argument, chosen.
Warn if this function does not return something

Original:
def filter(chosen) -> bool:
    return chosen % 2 == 0

* if code is equivalent to 1 expression that returns a boolean that can be represented in one line, inline it in a generator expression or a list comprehension.

Generated:
(chosen for chosen in partition if chosen % 2 == 0)
OR:
[chosen for chosen in partition if chosen % 2 == 0]

* else, find all return statements in filter, replace with an if-then-yield statement, and wrap the entire thing in a for loop passing in the partition.
For example:

Generated:
def generated_filter_yielder(partition):
    for chosen in partition:
        if (chosen % 2 == 0):
            yield chosen

This wraps the *get_elements* ast and becomes the new *get_elements*

* If optimizations == False: use lambda method with filter() builtin 

#### Sorting

* If DoOne: Use min() or heapq.nsmallest(1), or max() or heapq.nlargest(1) if reversed
* If DoK: Use heapq.nsmallest(k), or heapq.nlargest(k) if reversed
* If DoAll: Use sorted(), or sorted(reverse=True) if reversed

For sort_key:
* This method receives 1 argument, chosen.
* If return value from sort_key is the same value as the one passed in, and no side effects took place, assume there is no key and we are using the __lt__ or __gt__ defined in the chosen class instance.
* Else, use key=... in any three of the functions listed above

For sort_cmp:
* This method receives 2 arguments, A and B.
* Use key=functools.cmp_to_key(sort_cmp)

In the case that we use a key=... and the controlled method is passed additional arguments, wrap the method in a closure that has access to all non-local scope arguments and return a call to it as the key=closure(*NO_ARGS*, *NO_KWARGS*). 

If *get_elements* is a generator () expression, make it a list comprehension [] instead for speed.

This wraps the *get_elements* ast and becomes the new *get_elements*

Warn if this function does not return something

* If optimizations == False: always pass the sort method this key=...

#### Action

This method receives 1 argument, chosen.

If action returns a value:

* If code is equivalent to one expression: inline it with the *get_elements* ast. If *get_elements* is a generator expression, convert to a list comprehension and replace the return value with the inline action code.

* Else, if action has no arguments: use list(map(self.action))

If action does not return a value:

* Use an generated for loop in a closure at the top of the call method, inlining the action code directly in the for loop

If optimizations == False: use lambda method with map() builtin if action returns a value, else still use generated for loop in a closure but just call the action() method and pass chosen and each argument to it

#### Fold

* Only valid if action has a return

* this method receives 1 argument, results (from actions)
* call fold() directly and pass in the results from all the actions

Warn if this function does not return something

#### Post Controller

* This method receives no arguments
* warn if this method has a return, since its ignored

#### Generated Call Method

if action returns nothing:
    return None
elif fold is not defined:
    return list of action return values
else:
    return result from fold method