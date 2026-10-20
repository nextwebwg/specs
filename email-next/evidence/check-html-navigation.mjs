import {bindNavigation} from './html-navigation.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
process.stdout.write(JSON.stringify(bindNavigation(JSON.parse(input))));
