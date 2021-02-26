import { hello1 } from './dep1.js';

export function hello2() {
  const a = hello1()
  return "hello from 2";
}
