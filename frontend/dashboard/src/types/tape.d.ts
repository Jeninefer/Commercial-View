declare module 'tape' {
    interface Test {
        ok(value: any, msg?: string): void;
        notOk(value: any, msg?: string): void;
        equal<T>(actual: T, expected: T, msg?: string): void;
        notEqual<T>(actual: T, expected: T, msg?: string): void;
        deepEqual<T>(actual: T, expected: T, msg?: string): void;
        notDeepEqual<T>(actual: T, expected: T, msg?: string): void;
        pass(msg?: string): void;
        fail(msg?: string): void;
        throws(fn: () => void, expected?: any, msg?: string): void;
        doesNotThrow(fn: () => void, msg?: string): void;
        error(err: Error | null, msg?: string): void;
        plan(n: number): void;
        end(): void;
    }

    function tape(name: string, cb: (t: Test) => void): void;
    function tape(name: string, opts: Record<string, any>, cb: (t: Test) => void): void;

    export = tape;
}

declare module 'has-tostringtag/shams' {
    function hasToStringTagShams(): boolean;
    export = hasToStringTagShams;
}
