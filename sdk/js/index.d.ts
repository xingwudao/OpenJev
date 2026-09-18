export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export interface Choice<C extends Record<string, string> = Record<string, string>> {
  type: "choice";
  instructions: string;
  criteria: C;
}
export interface Score { type: "score"; instructions: string; criteria: string[] }
export interface Noul { type: "noul"; instructions: string; criteria?: string | Record<string, Json> }
export type Question = Choice | Score | Noul;
export type Answer<Q extends Question> = Q extends Choice<infer C>
  ? { type: "choice"; choice: keyof C & string; probabilities: Record<keyof C, number>; confidence: number }
  : Q extends Score
    ? { type: "score"; score: number; legend: Record<string, string>; probabilities: Record<string, number>; confidence: number }
    : { type: "noul"; noul: number };
export interface SystemOneRequest<Q extends Record<string, Question>> {
  state: string | Json[] | Record<string, Json>;
  model?: string;
  questions: Q;
}
export interface SystemOneResponse<Q extends Record<string, Question>> {
  model: string;
  answers: { [K in keyof Q]: Answer<Q[K]> };
  usage: { input_tokens: number; output_tokens: number };
}
export function choice<C extends Record<string, string>>(instructions: string, criteria: C): Choice<C>;
export function score(instructions: string, criteria: string[]): Score;
export function noul(instructions: string, criteria?: Noul["criteria"]): Noul;
export class OpenJevError extends Error { status: number; code: string; constructor(status: number, code: string, message: string) }
export class OpenJevClient {
  constructor(options?: { baseUrl?: string; timeout?: number });
  systemOne<Q extends Record<string, Question>>(request: SystemOneRequest<Q>): Promise<SystemOneResponse<Q>>;
}
