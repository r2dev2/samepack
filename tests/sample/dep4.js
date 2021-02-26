import { hello1 } from './dep1.js';
import { hello2 } from './dep2.js';

export function hello4() {
  const a = hello1() + hello2();
  return "hello from 4";
}
