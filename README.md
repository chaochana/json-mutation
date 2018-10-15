**JSON MUTATOR PROXY**

JSON MUTATOR PROXY is a test tool to mutate JSON response for Mutation Testing : https://en.wikipedia.org/wiki/Mutation_testing

This proxy basically adds fault to JSON response; remove a node, modify a value, etc. Then the response is 'Mutant' one.
When good test suite is executed against mutant one and give fail result, your system test suite does already cover it.

\* base on https://gist.github.com/jwustrack/0c7cb063a28ce14766d421e8d8a12fcc
