import {validateNavigationUrl} from './navigation-url.mjs';

// Input is the bounded, fresh data tree from html_tree.py, not arbitrary DOM.
// Output navigation records belong to a client handler, never sender attributes.
export function bindNavigation(tree) {
 const diagnostics=[];
 function visit(node) {
  if(typeof node==='string')return node;
  const {navigationCandidate,...rest}=node;
  const result={...rest,children:node.children.map(visit)};
  if(Object.hasOwn(node,'navigationCandidate')) {
   if(node.element!=='a')diagnostics.push('navigation-on-non-link');
   else {
    const destination=validateNavigationUrl(navigationCandidate);
    if(destination.state==='destination')result.navigation={href:destination.href,origin:destination.origin};
    else diagnostics.push('rejected-navigation');
   }
  }
  return result;
 }
 return {tree:tree.map(visit),diagnostics};
}
