/* eslint strict: 0 */
'use strict';

/** @type {import('tape')} */
var test = require('tape');
var isNumber = require('is-number-object');
var hasToStringTag = require('has-tostringtag/shams')();

/**
 * Tests for non-number values
 * @param {import('tape').Test} t - The test object
 */
test('not Numbers', function (t) {
    // @ts-expect-error
    t.notOk(isNumber(), 'undefined is not Number');
    t.notOk(isNumber(null), 'null is not Number');
    t.notOk(isNumber(false), 'false is not Number');
    t.notOk(isNumber(true), 'true is not Number');
    t.notOk(isNumber('foo'), 'string is not Number');
    t.notOk(isNumber([]), 'array is not Number');
    t.notOk(isNumber({}), 'object is not Number');
    t.notOk(isNumber(function () { }), 'function is not Number');
    t.notOk(isNumber(/a/g), 'regex literal is not Number');
    t.notOk(isNumber(new RegExp('a', 'g')), 'regex object is not Number');
    t.notOk(isNumber(new Date()), 'new Date() is not Number');
    t.end();
});

/**
 * Tests for Symbol.toStringTag behavior
 * @param {import('tape').Test} t - The test object
 */
test('@@toStringTag', { skip: !hasToStringTag }, function (t) {
    /** @type {{ toString(): string; valueOf(): number; [Symbol.toStringTag]?: string; }} */
    var fakeNumber = {
        toString: function () { return '7'; },
        valueOf: function () { return 42; }
    };
    fakeNumber[Symbol.toStringTag] = 'Number';
    t.notOk(isNumber(fakeNumber), 'fake Number with @@toStringTag "Number" is not Number');
    t.end();
});

/**
 * Tests for actual number values
 * @param {import('tape').Test} t - The test object
 */
test('Numbers', function (t) {
    t.ok(isNumber(42), 'number literal is Number');
    t.ok(isNumber(Object(42)), 'Number object is Number');
    t.ok(isNumber(NaN), 'NaN is Number');
    t.ok(isNumber(Infinity), 'Infinity is Number');
    t.end();
});
