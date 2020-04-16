self.languagePluginUrl = 'http://localhost:8000/pyodide/pyodide_dev.js';
importScripts('pyodide/pyodide_dev.js');

self.loader = {
  open_url: function(url) {
    let req = new XMLHttpRequest();
    req.open('GET', url, false);
    try {
      req.send();
      return [req.response, null]
    } catch(e) {
      return [null, e];
    }
  }
};

async function loadPythonFiles(...files) {
  await languagePluginLoader;
  let all_files = await Promise.all(
    files.map(file => fetch(file).then(fetcher => fetcher.text())));
  for (let file of all_files) {
    // Run the files serially
    await pyodide.runPythonAsync(file);
  }
}

async function initPython() {
  self.term = {
    echoFormatted: function(text, color='') {
      self.postMessage({
        'action': 'echoFormatted',
        'text': text,
        'color': color,
      })
      console.log('echo formatted', text, color)
    },
    printExitCode: function(code) {
      self.postMessage({
        'action': 'printExitCode',
        'code': code,
      })
      console.log('print exit code', code);
    }
  };
  await loadPythonFiles('module_loader.py', 'sandbox_interpreter.py')
}
let init = initPython();

self.onmessage = function(e) {
  handleMessage(e.data);
}

async function handleMessage(message) {
  await init;
  let interpreter = await pyodide.runPythonAsync(`Interpreter("${message.file}")`);
  switch (message.action) {
    case 'runShell':
      interpreter.runshell(message.cmd, message.code);
      message.returnPort.postMessage('done');
      break;
    case 'runComplete':
      console.log('runComplete', message.cmd, message.cursorPos);
      let completions = interpreter.runcomplete(message.cmd, message.cursorPos, message.code);
      message.returnPort.postMessage(completions);
      break;
  }
}
