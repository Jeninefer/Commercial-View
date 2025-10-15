# Code Citations

## is-number-object

**Source**: <https://github.com/inspect-js/is-number-object/blob/cb8423cd42bded7c9321e785a97c5305c2706b02/test/index.js>  
**License**: MIT

### Test Suite Pattern

The test suite from is-number-object includes tests for various non-number values:

```javascript
test('not Numbers', function (t) {
  // @ts-expect-error
  t.notOk(isNumber(), 'undefined is not Number');
  t.notOk(isNumber(null), 'null is not Number');
  t.notOk(isNumber(false), 'false is not Number');
  t.notOk(isNumber(true), 'true is not Number');
  t.notOk(isNumber('foo'), 'string is not Number');
  t.notOk(isNumber([]), 'array is not Number');
  t.notOk(isNumber({}), 'object is not Number');
  t.notOk(isNumber(function () {}), 'function is not Number');
  t.notOk(isNumber(/a/g), 'regex literal is not Number');
  t.notOk(isNumber(new RegExp('a', 'g')), 'regex object is not Number');
  t.notOk(isNumber(new Date()), 'new Date() is not Number');
  t.end();
});

test('@@toStringTag', { skip: !hasToStringTag }, function (t) {
  var fakeNumber = {
    toString: function () { return '7'; },
    valueOf: function () { return 42; }
  };
  fakeNumber[Symbol.toStringTag] = 'Number';
  t.notOk(isNumber(fakeNumber), 'fake Number with @@toStringTag "Number" is not Number');
  t.end();
});

test('Numbers', function (t) {
  t.ok(isNumber(42), 'number is Number');
  t.ok(isNumber(Object(42)), 'number object is Number');
  t.ok(isNumber(NaN), 'NaN is Number');
  t.ok(isNumber(Infinity), 'Infinity is Number');
  t.end();
});

<<<<<<< Updated upstream
```bash
=======
```text
>>>>>>> Stashed changes

This pattern has been adapted in our test implementation to validate similar behavior in our number detection utilities.
