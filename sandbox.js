'use strict'

let editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

window.loader = {
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


class PyEnv {

  static instance() {
    let currEnv = env;
    env = new PyEnv();
    return currEnv;
  }

  constructor() {
    this.worker = new Worker('./pyworker.js');
    this.worker.onmessage = (e) => {
      console.log('hi message', e);
      switch (e.data.action) {
        case 'echoFormatted':
          term.echoFormatted(e.data.text, e.data.color);
          break;
        case 'printExitCode':
          term.printExitCode(e.data.code);
          break;
      }
    };
    this.worker.onerror = function(e) {
      console.log('error :(', e);
    };
  }

  runShell(cmd, code) {
    let channel = new MessageChannel();
    this.worker.postMessage({
      action: 'runShell',
      file: editor.currentFile,
      cmd: cmd,
      code: code,
      returnPort: channel.port2,
    },
    [channel.port2]);
    return new Promise((resolve, reject) => {
      channel.port1.onmessage = resolve;
    });
  }

  runComplete(cmd, cursorPos, code) {
    let channel = new MessageChannel();
    this.worker.postMessage({
      action: 'runComplete',
      file: editor.currentFile,
      cmd: cmd,
      cursorPos: cursorPos,
      code: code,
      returnPort: channel.port2,
    },
    [channel.port2]);
    return new Promise((resolve, reject) => {
      channel.port1.onmessage = (e) => {
        console.log('Port message', e)
        resolve(e.data);
      };
    });
  }
}

let env = new PyEnv();

function synchronize(asyncFunc) {
  return function(...args) {
    let callback = args.pop();
    asyncFunc.apply(this, args).then(callback);
  };
}

async function initPython() {
  let term = $('#term').terminal(
    async (cmd) => {
      await PyEnv.instance().runShell(cmd, editor.getValue());
    },
    {
      greetings: `#! Welcome to the Hashbang playground (powered by Pyodide)`,
      prompt: "[[;orange;]$ ]",
      completion: async function(cmd) {
        let completions = await PyEnv.instance().runComplete(
          this.get_command(),
          this.before_cursor(false).length,
          editor.getValue());
        console.log('completions', completions);
        return completions;
      },
    }
  );
  term.echo(
`<p>Here you can try out the different commands in the hashbang test directory, or
paste your own code in the editor above. Below is a shell simulator that can
only execute the python command above, or run tab-completion on it.

<p>See
<a href="https://github.com/mauricelam/hashbang/blob/master/README.md" target="_blank">README</a>
for a quick overview of Hashbang, or refer to the
<a href="https://github.com/mauricelam/hashbang/wiki/API-reference" target="_blank">API reference</a>.
`,
      {raw: true})
  term.echoFormatted = function(text, color='') {
    if (!text) return;
    if (text.endsWith('\n')) {
      text = text.substring(0, text.length - 1);
    }
    text = $.terminal.escape_brackets(text);
    if (color) {
      this.echo(`[[;${color};]${text}]`);
    } else {
      this.echo(text);
    }
  };
  term.printExitCode = function(code) {
    this.echo(
      `<div align="right" style="color: ${code == 0 ? 'green' : 'orange'}">Exit code: ${code}</div>`,
      { raw: true })
  };

  window.term = term;
}
initPython();

// File browser
{
  const MY_TREE_ROOT = 'https://api.github.com/repos/mauricelam/hashbang/contents/tests';

  $('#file-tree').jstree({
    core: {
      data: synchronize(obj =>
        lsGithub((obj.original && obj.original.apiUrl) || MY_TREE_ROOT)),
      themes: {
        name: 'default-dark'
      }
    },
  });

  $('#file-tree').on('select_node.jstree', function (e, data) {
    if (data.node.original && data.node.original.type === 'dir') {
      data.instance.deselect_node(data.node);
    } else {
      setFile(data.node.original.downloadUrl);
    }
  });

  // Start with this file
  setFile('https://raw.githubusercontent.com/mauricelam/hashbang/master/tests/delegate/subcommands.py');
  // setFile('https://raw.githubusercontent.com/mauricelam/hashbang/master/tests/basic/remainder.py');

  async function setFile(downloadUrl) {
    let fetcher = await fetch(downloadUrl);
    let text = await fetcher.text();
    editor.setValue(text, -1);
    editor.currentFile = downloadUrl;
  }

  const ICON_MAP = {
    'dir': 'jstree-folder',
    'file': 'jstree-file',
  }

  async function lsGithub(url) {
    let fetcher = await fetch(url);
    let result = await fetcher.json();
    return result
      .filter(item => item.type === 'dir' || item.name.endsWith('.py'))
      .map(item => ({
        apiUrl: item.url,
        text: item.name,
        children: item.type === 'dir',
        downloadUrl: item.download_url,
        icon: ICON_MAP[item.type] || 'jstree-file',
        type: item.type,
      }));
  }

}
