function component() {
   let element = document.createElement('div');
   element.innerHTML = 'Hello, world!';

   return element;
}

document.body.appendChild(component());

