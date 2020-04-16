console.log('a');
self.languagePluginUrl = 'http://localhost:8000/pyodide/pyodide_dev.js';
fff = self.importScripts;
self.importScripts = function(...args) {
  console.log('import scripts', args);
  fff.apply(this, args);
}
console.log('b');
importScripts('pyodide/pyodide_dev.js');
console.log('c');

// self.loader = {
//   open_url: function(url) {
//     let req = new XMLHttpRequest();
//     req.open('GET', url, false);
//     try {
//       req.send();
//       return [req.response, null]
//     } catch(e) {
//       return [null, e];
//     }
//   }
// };

// async function loadPythonFiles(...files) {
//   await languagePluginLoader;
//   let all_files = await Promise.all(
//     files.map(file => fetch(file).then(fetcher => fetcher.text())));
//   for (let file of all_files) {
//     // Run the files serially
//     await pyodide.runPythonAsync(file);
//   }
// }

// async function initPython() {
//   self.term = {
//     echoFormatted: function(text, color='') {
//       console.log('echo formatted', text, color)
//     },
//     printExitCode: function(code) {
//       console.log('print exit code', code);
//     }
//   };
//   await loadPythonFiles('module_loader.py', 'sandbox_interpreter.py')
//   return await pyodide.runPythonAsync(`Interpreter("${editor.currentFile}")`);
// }
// let init = initPython();

// self.postMessage({
//   'aloha': 'hey there'
// });

// self.onmessage = async function(e) {
//   await init;
//   console.log(e);
// }
