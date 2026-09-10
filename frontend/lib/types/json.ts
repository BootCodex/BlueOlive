/**
 * A real union type for "arbitrary JSON-shaped value of unknown structure",
 * for API response data that isn't modeled as a concrete interface. Prefer
 * this over `unknown` for such data: TypeScript has a quirk where optional
 * chaining (`doc?.field`) on an `unknown`-typed property collapses to the
 * near-useless type `{}` instead of `unknown`, breaking normal narrowing.
 * A real union like this one doesn't hit that quirk.
 */
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | JsonValue[]
  | { [key: string]: JsonValue };

export type JsonObject = Record<string, JsonValue>;
