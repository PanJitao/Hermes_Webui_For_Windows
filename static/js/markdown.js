    // Register highlight.js languages and configure marked
    (function() {
      const langs = {
        python:'python', javascript:'javascript', js:'javascript',
        typescript:'typescript', ts:'typescript', bash:'bash', sh:'bash',
        shell:'bash', powershell:'powershell', ps1:'powershell',
        json:'json', yaml:'yaml', yml:'yaml', xml:'xml', html:'xml',
        sql:'sql', css:'css', markdown:'markdown', md:'markdown',
        java:'java', go:'go', rust:'rust', rs:'rust', cpp:'cpp', c:'cpp',
        'c++':'cpp', diff:'diff',
      };
      // Configure marked to use highlight.js via the extension API
      if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
        const renderer = new marked.Renderer();
        renderer.code = function(obj) {
          const code = typeof obj === 'object' ? obj.text : obj;
          const lang = typeof obj === 'object' ? obj.lang : arguments[1];
          const mapped = langs[(lang||'').toLowerCase()];
          let highlighted = code;
          if (mapped && hljs.getLanguage(mapped)) {
            highlighted = hljs.highlight(code, { language: mapped }).value;
          } else {
            highlighted = hljs.highlightAuto(code).value;
          }
          return '<div class="code-wrap relative mb-3 rounded-lg overflow-hidden border border-gray-800">'
            + '<div class="flex items-center justify-between px-4 py-1.5 bg-gray-900 border-b border-gray-800">'
            + '<span class="text-[11px] text-gray-500 font-mono">' + (lang || 'text') + '</span>'
            + '<span class="copy-btn text-[11px] text-gray-500 hover:text-hermes-400 transition flex items-center gap-1 cursor-pointer select-none"'
            + ' data-code="' + code.replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '">'
            + '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>复制代码</span>'
            + '</div>'
            + '<pre><code class="hljs language-' + (lang||'text') + '">' + highlighted + '</code></pre>'
            + '</div>';
        };
        marked.setOptions({
          renderer: renderer,
          breaks: true,
          gfm: true,
        });
      }
      // Delegated click handler for copy buttons on code blocks
      document.addEventListener('click', function(e) {
        var btn = e.target.closest('.copy-btn');
        if (!btn) return;
        var code = btn.getAttribute('data-code');
        if (!code) return;
        // decodeURIComponent returns original code
        var decoded = decodeURIComponent(code);
        var ta = document.createElement('textarea');
        ta.value = decoded;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        var ok = document.createElement('span');
        ok.textContent = '✓';
        ok.style.cssText = 'color:#34d399;font-size:11px;margin-right:4px';
        btn.parentNode.insertBefore(ok, btn);
        setTimeout(function() { ok.remove(); }, 1200);
      });
    })();
