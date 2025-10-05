declare module 'tape' {
    export interface Test {
        ok(value: any, msg?: string): void;
        notOk(value: any, msg?: string): void;
        error(err: Error | string | null, msg?: string): void;
        equal<T>(actual: T, expected: T, msg?: string): void;
        notEqual<T>(actual: T, expected: T, msg?: string): void;
        deepEqual<T>(actual: T, expected: T, msg?: string): void;
        notDeepEqual<T>(actual: T, expected: T, msg?: string): void;
        pass(msg?: string): void;
        fail(msg?: string): void;
        end(): void;
    }

    function test(name: string, cb: (t: Test) => void): void;
    function test(name: string, opts: Record<string, any>, cb: (t: Test) => void): void;

    export = test;
}

declare module 'has-tostringtag/shams' {
    function hasToStringTagShams(): boolean;
    export = hasToStringTagShams;
}
