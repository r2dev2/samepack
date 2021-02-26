import { hello1 } from './dep1.js';
import { hello4 } from './dep4.js';

const secret = 3;

export function hello3() {
  const a = hello1();
  const b = hello4();
  return `hello from ${secret}`;
}
