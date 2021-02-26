import { hello1 } from './dep1.js';
import Dep2 from './dep2.js'
import { hello3 } from `./dep3.js`
import { hello4 } from "./dep4.js";

console.log(hello1());
console.log(Dep2.hello2());
console.log(hello3());
console.log(hello4());
