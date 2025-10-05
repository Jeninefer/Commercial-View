'use strict';

/**
 * Check if a value is a Number object or primitive
 * @param {any} value - The value to check
 * @returns {boolean} True if value is a number (primitive or object)
 */
module.exports = function isNumber(value) {
	if (typeof value === 'number') {
		return true;
	}
	if (!value || typeof value !== 'object') {
		return false;
	}
	// Check if it's a Number object
	try {
		Number.prototype.valueOf.call(value);
		return Object.prototype.toString.call(value) === '[object Number]';
	} catch (e) {
		return false;
	}
};
