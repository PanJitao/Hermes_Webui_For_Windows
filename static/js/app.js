      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            hermes: { 50:'#eef2ff',100:'#e0e7ff',200:'#c7d2fe',300:'#a5b4fc',400:'#818cf8',500:'#6366f1',600:'#4f46e5',700:'#4338ca',800:'#3730a3',900:'#312e81',950:'#1e1b4b' },
            accent: { 50:'#eef2ff',100:'#e0e7ff',200:'#c7d2fe',300:'#a5b4fc',400:'#818cf8',500:'#6366f1',600:'#4f46e5',700:'#4338ca',800:'#3730a3',900:'#312e81',950:'#1e1b4b' },
          }
        }
      }
    }

    function app() {
      return {
        page: 'dashboard',
        nav: [
          { id: 'dashboard',     label: '仪表盘',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/></svg>' },
          { id: 'config',        label: '配置管理',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>' },
          { id: 'conversations', label: '对话历史',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>' },
          { id: 'chat',          label: '在线对话',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>' },
          { id: 'skills',        label: '技能管理',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>' },
          { id: 'cron',          label: '定时任务',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>' },
          { id: 'logs',          label: '日志查看',     icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>' },
        ],

        // Dashboard
        status: {},
        currentModel: '',
        modelProviders: [],
        modelSwitchMsg: '',
        modelSwitchOk: false,
        newProvider: { name: '', model: '', base_url: '', api_key: '' },
        // Health monitoring
        gatewayStatus: 'unknown',
        toastMsg: '',
        toastOk: true,
        _lastGatewayStatus: null,
        get statusItems() {
          const s = this.status;
          return [
            { key: 'home',    label: 'Hermes Home',  ok: s.hermes_home_exists },
            { key: 'config',  label: 'config.yaml',  ok: s.config_yaml_exists },
            { key: 'env',     label: '.env',         ok: s.env_exists },
            { key: 'db',      label: 'state.db',     ok: s.state_db_exists },
            { key: 'skills',  label: 'skills/',      ok: s.skills_dir_exists },
            { key: 'cron',    label: 'cron/',        ok: s.cron_dir_exists },
            { key: 'logs',    label: 'logs/',        ok: s.logs_dir_exists },
            { key: 'soul',    label: 'SOUL.md',      ok: s.soul_md_exists },
          ];
        },

        // Config
        configRaw: '',
        configLoadErr: '',
        configSections: [],
        configLoading: false,
        showRawConfig: false,
        expandedSections: [],
        envVars: [],
        envVisibility: {},
        envCopied: {},

        // Conversations
        conversations: [],
        convLoading: false,
        convError: '',
        convSearch: '',
        convTotal: 0,
        convTotalTokens: 0,
        selectedConvId: null,
        selectedConvMessages: [],
        dbSchema: null,

        // Chat
        chatMessages: [],
        chatInput: '',
        chatLoading: false,
        hermesPath: null,
        apiServerRunning: false,
        chatStreamText: '',
        chatAttachments: [],
        chatSessions: [],
        chatSessionsLoading: false,
        showChatSessions: false,
        chatActiveSessionId: null,
        chatActiveTitle: '',
        chatRenaming: false,
        chatRenameText: '',

        // Skills
        skills: [],
        skillCategories: [],
        skillFilter: '',
        skillSearch: '',
        skillsLoading: false,
        selectedSkill: null,
        editingSkill: null,
        editingContent: '',
        deletingSkill: null,
        showSkillCreate: false,
        showSkillImport: false,
        newSkill: { category: '', name: '', content: '' },
        importSkill: { category: '', name: '' },
        importSkillFile: null,
        skillNotifyMsg: '',
        skillNotifyOk: false,
        get filteredSkills() {
          let list = this.skills;
          if (this.skillFilter) {
            list = list.filter(s => s.category === this.skillFilter);
          }
          if (this.skillSearch) {
            const q = this.skillSearch.toLowerCase();
            list = list.filter(s =>
              (s.title || '').toLowerCase().includes(q) ||
              (s.name || '').toLowerCase().includes(q) ||
              (s.category || '').toLowerCase().includes(q) ||
              (s.summary || '').toLowerCase().includes(q) ||
              (s.description || '').toLowerCase().includes(q)
            );
          }
          return list;
        },

        // Cron
        cronJobs: [],
        cronLoading: false,
        selectedCron: null,

        // Logs
        logFiles: [],
        logLoading: false,
        logContent: null,
        logContentName: '',

        // ========== Init ==========
        _loaded: {},  // track which pages have been loaded
        async init() {
          // marked.js + hljs configured in <script> block at top of page
          await this.loadStatus();
          this.loadConfig();
          this.loadEnv();
          this.loadModels();
          this.checkHermes();
          this.checkApiServer();
          this.monitorHealth();
          // Poll health every 10s
          setInterval(() => this.monitorHealth(), 10000);
          // Watch page changes and auto-load data
          this.$watch('page', (val) => {
            if (this._loaded[val]) return;
            this._loaded[val] = true;
            switch(val) {
              case 'config':         this.loadConfigStructured(); break;
              case 'conversations': this.loadConversations(); break;
              case 'skills':        this.loadSkills(); break;
              case 'cron':          this.loadCron(); break;
              case 'logs':          this.loadLogs(); break;
            }
          });
        },

        // ========== Helpers ==========
        renderMarkdown(text) {
          if (!text) return '';
          try {
            const r = new marked.Renderer();
            r.code = function(obj) {
              const code = typeof obj === 'object' ? obj.text : obj;
              const lang = typeof obj === 'object' ? obj.lang : arguments[1];
              const map = {js:'javascript',py:'python',sh:'bash',ts:'typescript',yml:'yaml'};
              const lg = (lang || '').toLowerCase();
              const mapped = map[lg] || lg;
              let hl = code;
              if (typeof hljs !== 'undefined') {
                if (mapped && hljs.getLanguage(mapped)) {
                  hl = hljs.highlight(code, {language: mapped}).value;
                } else {
                  hl = hljs.highlightAuto(code).value;
                }
              }
              return '<div class="code-wrap relative mb-3 rounded-lg overflow-hidden border border-gray-800">'
                + '<div class="flex items-center justify-between px-4 py-1.5 bg-gray-900 border-b border-gray-800">'
                + '<span class="text-[11px] text-gray-500 font-mono">' + (lang || 'text') + '</span>'
                + '<span class="copy-btn text-[11px] text-gray-500 hover:text-hermes-400 transition flex items-center gap-1 cursor-pointer select-none"'
                + ' data-code="' + encodeURIComponent(code) + '">'
                + '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>复制代码</span>'
                + '</div>'
                + '<pre><code class="hljs language-' + (lang || 'text') + '">' + hl + '</code></pre>'
                + '</div>';
            };
            return marked.parse(text, { renderer: r, breaks: true, gfm: true });
          } catch(e) { return text; }
        },

        async checkApiServer() {
          try {
            const data = await this.api('/chat/status');
            this.apiServerRunning = data.running || false;
          } catch (e) {
            this.apiServerRunning = false;
          }
        },
        async monitorHealth() {
          try {
            const data = await this.api('/health/monitor');
            const prev = this._lastGatewayStatus;
            this.gatewayStatus = data.gateway || 'unknown';
            this.apiServerRunning = data.gateway === 'connected';
            // Show global toast on status change
            if (prev && prev !== this.gatewayStatus) {
              if (this.gatewayStatus === 'connected') {
                this.showToast('✅ Gateway 已重新连接', true);
              } else if (this.gatewayStatus === 'disconnected') {
                this.showToast('⚠️ Gateway 已断开连接', false);
              } else if (this.gatewayStatus === 'timeout') {
                this.showToast('⏱️ Gateway 连接超时', false);
              }
            }
            this._lastGatewayStatus = this.gatewayStatus;
          } catch (e) {
            this.gatewayStatus = 'unknown';
          }
        },
        showToast(msg, ok) {
          this.toastMsg = msg;
          this.toastOk = ok;
          clearTimeout(this._toastTimer);
          this._toastTimer = setTimeout(() => { this.toastMsg = ''; }, 5000);
        },
        async api(path, opts = {}) {
          const res = await fetch('/api' + path, {
            headers: { 'Content-Type': 'application/json' },
            ...opts,
          });
          if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || res.statusText);
          }
          return await res.json();
        },

        formatTime(ts) {
          if (!ts) return '';
          // ts is a Unix timestamp (float)
          const d = new Date(ts * 1000);
          const now = new Date();
          const diffMs = now - d;
          const diffDays = Math.floor(diffMs / 86400000);

          const time = d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });

          if (diffDays === 0) return '今天 ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
          if (diffDays === 1) return '昨天 ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
          if (diffDays < 7) return diffDays + '天前';
          return time;
        },

        formatTokens(n) {
          if (!n) return '0';
          if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
          if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
          return String(n);
        },

        // ========== Dashboard ==========
        async loadStatus() {
          try {
            this.status = await this.api('/status');
          } catch (e) {
            this.status = { error: e.message };
          }
        },

        // ========== Models ==========
        async loadModels() {
          try {
            const data = await this.api('/models');
            this.currentModel = data.current || '';
            this.modelProviders = data.providers || [];
          } catch (e) {
            this.modelProviders = [];
          }
        },
        async switchModel(provider) {
          this.modelSwitchMsg = '';
          try {
            const data = await this.api('/models/switch', {
              method: 'PUT',
              body: JSON.stringify({
                model: provider.model,
                provider: provider.provider || 'custom',
                base_url: provider.base_url || '',
              }),
            });
            this.currentModel = data.current_model;
            this.modelSwitchOk = true;
            this.modelSwitchMsg = '✓ 已切换到 ' + data.current_model;
            this.status.current_model = data.current_model;
            setTimeout(() => { this.modelSwitchMsg = ''; }, 3000);
          } catch (e) {
            this.modelSwitchOk = false;
            this.modelSwitchMsg = '切换失败: ' + e.message;
          }
        },
        async addProvider() {
          const p = this.newProvider;
          if (!p.model || !p.base_url) {
            this.modelSwitchOk = false;
            this.modelSwitchMsg = '请填写模型名和 API Base URL';
            return;
          }
          try {
            await this.api('/models/providers', {
              method: 'POST',
              body: JSON.stringify(p),
            });
            this.newProvider = { name: '', model: '', base_url: '', api_key: '' };
            await this.loadModels();
            this.modelSwitchOk = true;
            this.modelSwitchMsg = '✓ 提供商已添加';
            setTimeout(() => { this.modelSwitchMsg = ''; }, 3000);
          } catch (e) {
            this.modelSwitchOk = false;
            this.modelSwitchMsg = '添加失败: ' + e.message;
          }
        },

        // ========== Config ==========
        async loadConfig() {
          try {
            this.configLoadErr = '';
            const data = await this.api('/config');
            this.configRaw = data.raw || (data.config ? JSON.stringify(data.config, null, 2) : '');
          } catch (e) {
            this.configLoadErr = e.message;
          }
        },
        async saveConfig() {
          try {
            let config;
            try { config = JSON.parse(this.configRaw); }
            catch { alert('请输入有效的 JSON 格式'); return; }
            await this.api('/config', { method: 'PUT', body: JSON.stringify({ config }) });
            alert('配置已保存');
            await this.loadConfig();
          } catch (e) { alert('保存失败: ' + e.message); }
        },
        async loadEnv() {
          try {
            const data = await this.api('/config/env');
            this.envVars = data.variables || [];
          } catch (e) { this.envVars = []; }
        },
        async copyEnvVar(v) {
          try {
            await navigator.clipboard.writeText(v.value);
            this.envCopied[v.key] = true;
            setTimeout(() => { this.envCopied[v.key] = false; }, 2000);
          } catch (e) {
            // Fallback for older browsers
            const ta = document.createElement('textarea');
            ta.value = v.value;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            this.envCopied[v.key] = true;
            setTimeout(() => { this.envCopied[v.key] = false; }, 2000);
          }
        },

        // Structured Config
        async loadConfigStructured() {
          this.configLoading = true;
          try {
            const data = await this.api('/config/structured');
            this.configSections = data.sections || [];
            // Auto-expand first 3 sections
            this.expandedSections = this.configSections.slice(0, 3).map(s => s.id);
          } catch (e) {
            this.configSections = [];
          }
          this.configLoading = false;
        },
        toggleSection(id) {
          const idx = this.expandedSections.indexOf(id);
          if (idx >= 0) {
            this.expandedSections.splice(idx, 1);
          } else {
            this.expandedSections.push(id);
          }
        },
        async updateConfigField(section, key, value) {
          // Build the update payload
          const path = [...section.path];
          // For object type, we update the full object with one field changed
          const newValue = { ...(section.value || {}) };
          if (value === null || value === '' || value === undefined) {
            delete newValue[key];
          } else {
            newValue[key] = value;
          }
          try {
            await this.api('/config/section', {
              method: 'PUT',
              body: JSON.stringify({
                section_id: section.id,
                path: path,
                value: newValue,
              }),
            });
            // Update local state
            section.value = newValue;
            this.showConfigMsg('✓ 已更新 ' + section.title + ' / ' + key, true);
          } catch (e) {
            this.showConfigMsg('保存失败: ' + e.message, false);
          }
        },
        async removeListItem(section, idx) {
          const newValue = [...(section.value || [])];
          newValue.splice(idx, 1);
          try {
            await this.api('/config/section', {
              method: 'PUT',
              body: JSON.stringify({
                section_id: section.id,
                path: section.path,
                value: newValue,
              }),
            });
            section.value = newValue;
            this.showConfigMsg('✓ 已移除', true);
          } catch (e) {
            this.showConfigMsg('操作失败: ' + e.message, false);
          }
        },
        editProvider(section, idx) {
          // If already editing this provider, save it
          if (this.editingProvider && this.editingProvider.sectionId === section.id && this.editingProvider.idx === idx) {
            this.saveProvider(section, idx);
            return;
          }
          // Otherwise, enter edit mode
          const item = section.value[idx] || {};
          this.editingProvider = {
            sectionId: section.id,
            idx: idx,
            name: item.name || '',
            model: item.model || '',
            base_url: item.base_url || '',
            api_key: item.api_key || '',
          };
        },
        async saveProvider(section, idx) {
          // Build updated values from edit state or fallback to current section data
          const edit = this.editingProvider;
          const item = (section.value || [])[idx] || {};
          const newValue = [...(section.value || [])];
          const updated = {
            name: (edit && edit.name) || item.name || '',
            model: (edit && edit.model) || item.model || '',
            base_url: (edit && edit.base_url) || item.base_url || '',
            api_key: (edit && edit.api_key && edit.api_key.trim()) || item.api_key || '',
          };
          newValue[idx] = updated;
          try {
            await this.api('/config/section', {
              method: 'PUT',
              body: JSON.stringify({
                section_id: section.id,
                path: section.path,
                value: newValue,
              }),
            });
            section.value = newValue;
            this.editingProvider = null;
            this.showConfigMsg('✓ 已保存 ' + updated.name, true);
          } catch (e) {
            this.showConfigMsg('保存失败: ' + e.message, false);
          }
        },
        copyProviderKey(section, idx) {
          const item = section.value[idx];
          const key = item?.api_key || '';
          if (!key) {
            this.showConfigMsg('⚠️ 无 API Key 可复制', false);
            return;
          }
          try {
            navigator.clipboard.writeText(key);
          } catch(e) {
            const ta = document.createElement('textarea');
            ta.value = key;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
          }
          this.providerKeyCopied[section.id + '-' + idx] = true;
          setTimeout(() => { this.providerKeyCopied[section.id + '-' + idx] = false; }, 2000);
        },
        configMsg: '',
        configMsgOk: false,
        editingProvider: null,
        providerKeyVisible: {},
        providerKeyCopied: {},
        showConfigMsg(msg, ok) {
          this.configMsg = msg;
          this.configMsgOk = ok;
          setTimeout(() => { this.configMsg = ''; }, 3000);
        },

        // ========== Conversations ==========
        async loadConversations() {
          this.convLoading = true;
          this.convError = '';
          try {
            const params = new URLSearchParams({ limit: '100' });
            if (this.convSearch) params.set('search', this.convSearch);
            const data = await this.api('/conversations?' + params.toString());
            this.conversations = data.conversations || [];
            this.convTotal = data.total || this.conversations.length;
            this.convTotalTokens = this.conversations.reduce(
              (sum, c) => sum + (c.input_tokens || 0) + (c.output_tokens || 0), 0
            );
          } catch (e) {
            this.convError = e.message;
            this.conversations = [];
          }
          this.convLoading = false;
        },
        async loadConversationDetail(sessionId) {
          this.selectedConvId = sessionId;
          try {
            const data = await this.api('/conversations/' + encodeURIComponent(sessionId));
            this.selectedConvMessages = data.messages || [];
          } catch (e) {
            this.selectedConvMessages = [{ role: 'system', content: '加载失败: ' + e.message }];
          }
        },

        async continueConversation(conv) {
          // Load conversation messages and switch to chat page
          this.page = 'chat';
          this.chatMessages = [];
          this.chatLoading = true;

          try {
            const data = await this.api('/conversations/' + encodeURIComponent(conv.id));
            const messages = data.messages || [];

            // Convert messages to chat format
            for (const msg of messages) {
              if (msg.role === 'user' && msg.content) {
                this.chatMessages.push({ role: 'user', text: msg.content });
              } else if (msg.role === 'assistant' && msg.content) {
                this.chatMessages.push({ role: 'assistant', text: msg.content });
              }
            }

            // Add a system message indicating this is a continued conversation
            if (this.chatMessages.length > 0) {
              this.chatMessages.push({
                role: 'system',
                text: `── 以上为历史消息（来自会话: ${conv.title || conv.id}，模型: ${conv.model}）──\n请在下方继续对话：`,
              });
            }

            this.scrollToBottom();
          } catch (e) {
            this.chatMessages.push({ role: 'assistant', text: '[加载失败] ' + e.message });
          }

          this.chatLoading = false;
        },
        async renameHistoryConv(conv) {
          var title = (conv._newTitle || '').trim();
          if (!title) { conv._renaming = false; return; }
          try {
            await this.api('/conversations/' + encodeURIComponent(conv.id) + '/rename', {
              method: 'PUT', body: JSON.stringify({ title: title }),
            });
            // Replace objects for Alpine reactivity
            var sid = conv.id;
            this.conversations = this.conversations.map(function(c) {
              return c.id === sid ? Object.assign({}, c, { title: title, _renaming: false }) : c;
            });
            this.chatSessions = this.chatSessions.map(function(s) {
              return s.id === sid ? Object.assign({}, s, { preview: title }) : s;
            });
            if (sid === this.chatActiveSessionId) { this.chatActiveTitle = title; }
          } catch(e) { this.showToast('重命名失败: ' + e.message, false); }
        },

        // ========== Chat ==========
        async checkHermes() {
          try {
            const data = await this.api('/chat/hermes-path');
            this.hermesPath = data.path;
          } catch (e) { this.hermesPath = null; }
        },
        async sendChat() {
          let msg = this.chatInput.trim();
          // Disable if no text and no attachments
          if ((!msg && this.chatAttachments.length === 0) || this.chatLoading) return;
          // Prepend file paths to message
          if (this.chatAttachments.length > 0) {
            const paths = this.chatAttachments.map(a => a.path).join('\n');
            msg = paths + (msg ? '\n' + msg : '');
            this.chatAttachments = [];
          }
          this.chatMessages.push({ role: 'user', text: msg });
          this.chatInput = '';
          this.chatLoading = true;
          this.chatStreamText = '';
          this.scrollToBottom();

          // Build history for context (only user + assistant messages, last 20)
          const history = this.chatMessages
            .filter(m => m.role === 'user' || m.role === 'assistant')
            .slice(0, -1)  // exclude the just-added user message
            .slice(-20)
            .map(m => ({ role: m.role, content: m.text }));

          // Add streaming assistant message placeholder
          const streamIdx = this.chatMessages.length;
          this.chatMessages.push({ role: 'assistant', text: '', streaming: true });

          try {
            const res = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message: msg, history }),
            });
            if (!res.ok) {
              const err = await res.json().catch(() => ({ detail: res.statusText }));
              throw new Error(err.detail || res.statusText);
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let fullText = '';
            let buffer = '';

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              buffer += decoder.decode(value, { stream: true });

              // Process complete SSE lines
              const lines = buffer.split('\n');
              buffer = lines.pop() || '';  // keep incomplete line in buffer

              for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                  const data = JSON.parse(line.slice(6));
                  if (data.type === 'delta') {
                    fullText += data.content;
                    this.chatMessages[streamIdx].text = fullText;
                    this.chatStreamText = fullText;
                    this.scrollToBottom();
                  } else if (data.type === 'error') {
                    fullText += '\n\n⚠️ **错误**: ' + data.message;
                    this.chatMessages[streamIdx].text = fullText;
                  } else if (data.type === 'done' || data.type === 'finish') {
                    // Stream complete
                  }
                } catch {}
              }
            }
          } catch (e) {
            this.chatMessages[streamIdx].text = fullText || ('⚠️ **连接错误**: ' + e.message);
          }

          // Remove streaming flag
          this.chatMessages[streamIdx].streaming = false;
          this.chatLoading = false;
          this.chatStreamText = '';
          this.scrollToBottom();
        },
        scrollToBottom() {
          this.$nextTick(() => {
            const box = this.$refs.chatBox;
            if (box) box.scrollTop = box.scrollHeight;
          });
        },
        async copyAssistantMsg(msg, mode) {
          // mode: 'text' = strip markdown, 'markdown' = preserve raw
          const text = mode === 'markdown' ? msg.text : (msg.text || '').replace(/#{1,6}\s?/g, '').replace(/\*{1,3}([^*]+)\*{1,3}/g, '$1').replace(/`{1,3}[^`]*`{1,3}/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/^[*-]\s/gm, '').replace(/^>\s/gm, '').replace(/\n{3,}/g, '\n\n').trim();
          try {
            await navigator.clipboard.writeText(text);
            msg._copied = true;
            setTimeout(() => { msg._copied = false; }, 2000);
          } catch(e) {
            const ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            msg._copied = true;
            setTimeout(() => { msg._copied = false; }, 2000);
          }
        },
        async regenerateAnswer(msg, idx) {
          if (this.chatLoading) return;
          // Find the user message before this assistant message
          let userMsg = null;
          for (let j = idx - 1; j >= 0; j--) {
            if (this.chatMessages[j].role === 'user') { userMsg = this.chatMessages[j]; break; }
          }
          if (!userMsg) return;
          // Track iteration
          msg.iteration = (msg.iteration || 0) + 1;
          // Remove only this assistant message (not user message)
          this.chatMessages.splice(idx);
          // Call API directly — don't push a new user message
          await this.sendChatDirect(userMsg.text);
        },
        async sendChatDirect(userText) {
          this.chatLoading = true;
          this.chatStreamText = '';
          this.scrollToBottom();
          const history = this.chatMessages
            .filter(m => m.role === 'user' || m.role === 'assistant')
            .slice(-20)
            .map(m => ({ role: m.role, content: m.text }));
          const streamIdx = this.chatMessages.length;
          this.chatMessages.push({ role: 'assistant', text: '', streaming: true });
          try {
            const res = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message: userText, history }),
            });
            if (!res.ok) throw new Error((await res.json().catch(()=>({detail:res.statusText}))).detail||res.statusText);
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let full = '', buf = '';
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              buf += decoder.decode(value, { stream: true });
              const lines = buf.split('\n'); buf = lines.pop() || '';
              for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                  const d = JSON.parse(line.slice(6));
                  if (d.type === 'delta') { full += d.content; this.chatMessages[streamIdx].text = full; this.chatStreamText = full; this.scrollToBottom(); }
                  else if (d.type === 'error') { full += '\n\n⚠️ **错误**: ' + d.message; this.chatMessages[streamIdx].text = full; }
                } catch {}
              }
            }
          } catch (e) {
            this.chatMessages[streamIdx].text = full || ('⚠️ **错误**: ' + e.message);
          }
          this.chatMessages[streamIdx].streaming = false;
          this.chatLoading = false;
          this.chatStreamText = '';
          this.scrollToBottom();
        },

        // ========== File Upload ==========
        async uploadChatFile(event) {
          const file = event.target.files[0];
          if (!file) return;
          const formData = new FormData();
          formData.append('file', file);
          try {
            const res = await fetch('/api/chat/upload', { method: 'POST', body: formData });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || res.statusText);
            this.chatAttachments.push({ name: data.filename, path: data.saved_path });
          } catch (e) {
            this.showToast('上传失败: ' + e.message, false);
          }
          event.target.value = '';
        },
        newConversation() {
          // Auto-save current conversation before clearing
          if (this.chatMessages.length > 1) { this.saveConversation(); }
          this.chatMessages = [];
          this.chatInput = '';
          this.chatAttachments = [];
          this.chatStreamText = '';
          this.chatActiveSessionId = null;
          this.chatActiveTitle = '';
        },
        async saveConversation() {
          var msgs = this.chatMessages.filter(function(m) { return m.role === 'user' || m.role === 'assistant'; });
          if (msgs.length === 0) return;
          try {
            var body = { messages: msgs };
            if (this.chatActiveSessionId) body.session_id = this.chatActiveSessionId;
            if (this.chatActiveTitle) body.title = this.chatActiveTitle;
            var result = await this.api('/chat/save-conversation', {
              method: 'POST', body: JSON.stringify(body),
            });
            if (result.success) {
              this.chatActiveSessionId = result.session_id;
              this.chatActiveTitle = result.title;
              this.loadChatSessions();
            }
          } catch(e) {}
        },
        async loadChatSessions() {
          this.chatSessionsLoading = true;
          try {
            const data = await this.api('/conversations?limit=20');
            this.chatSessions = (data.conversations || []).map(function(s) {
              var preview = (s.title || s.first_user_msg || '').substring(0, 60);
              var time = '';
              if (s.started_at) { try { time = new Date(s.started_at * 1000).toLocaleString(); } catch(e) { time = s.started_at; } }
              return { id: s.id, preview: preview, time: time, count: s.message_count || 0, model: s.model || '' };
            });
          } catch(e) { this.chatSessions = []; }
          this.chatSessionsLoading = false;
        },
        async loadChatSession(id) {
          if (this.chatLoading) return;
          try {
            const data = await this.api('/conversations/' + encodeURIComponent(id));
            if (!data.messages) return;
            var msgs = data.messages.filter(function(m) { return m.role === 'user' || m.role === 'assistant' || m.role === 'system'; });
            var mapped = msgs.map(function(m) { return { role: m.role, text: m.content || '' }; });
            this.chatMessages = mapped;
            this.chatActiveSessionId = id;
            this.chatActiveTitle = (data.session && data.session.title) || '';
            this.showChatSessions = false;
            this.$nextTick(function() { this.scrollToBottom(); }.bind(this));
          } catch(e) { this.showToast('加载对话失败: ' + e.message, false); }
        },
        async renameActiveSession() {
          var title = (this.chatRenameText || '').trim();
          if (!title) { this.chatRenaming = false; return; }
          try {
            await this.api('/conversations/' + encodeURIComponent(this.chatActiveSessionId) + '/rename', {
              method: 'PUT', body: JSON.stringify({ title: title }),
            });
            this.chatActiveTitle = title;
            this.chatRenaming = false;
            // Sync to chat sessions panel (replace object for Alpine reactivity)
            this.chatSessions = this.chatSessions.map(function(s) {
              return s.id === this.chatActiveSessionId ? Object.assign({}, s, { preview: title }) : s;
            }.bind(this));
            // Sync to history page
            this.conversations = this.conversations.map(function(c) {
              return c.id === this.chatActiveSessionId ? Object.assign({}, c, { title: title }) : c;
            }.bind(this));
          } catch(e) { this.showToast('重命名失败: ' + e.message, false); }
        },
        async renameChatSession(s) {
          var title = (s._newTitle || '').trim();
          if (!title) { s._renaming = false; return; }
          try {
            await this.api('/conversations/' + encodeURIComponent(s.id) + '/rename', {
              method: 'PUT', body: JSON.stringify({ title: title }),
            });
            // Replace objects for Alpine reactivity
            this.chatSessions = this.chatSessions.map(function(x) {
              return x.id === s.id ? Object.assign({}, x, { preview: title, _renaming: false }) : x;
            });
            if (s.id === this.chatActiveSessionId) { this.chatActiveTitle = title; }
            this.conversations = this.conversations.map(function(c) {
              return c.id === s.id ? Object.assign({}, c, { title: title }) : c;
            });
          } catch(e) { this.showToast('重命名失败: ' + e.message, false); }
        },

        // ========== Skills ==========
        async loadSkills() {
          this.skillsLoading = true;
          try {
            const data = await this.api('/skills');
            this.skills = data.skills || [];
            this.skillCategories = data.categories || [];
          } catch (e) {
            this.skills = [];
            this.skillCategories = [];
          }
          this.skillsLoading = false;
        },

        async viewSkillDetail(skill) {
          this.selectedSkill = skill;
          this.editingSkill = null;
          this.deletingSkill = null;
          // Fetch full detail with all_files
          try {
            const data = await this.api('/skills/' + encodeURIComponent(skill.category) + '/' + encodeURIComponent(skill.name));
            this.selectedSkill = data;
          } catch (e) {
            // keep the card-level data
          }
        },

        async toggleSkill(skill) {
          const newState = !skill.enabled;
          try {
            await this.api('/skills/' + encodeURIComponent(skill.category) + '/' + encodeURIComponent(skill.name) + '/toggle', {
              method: 'PUT',
              body: JSON.stringify({ enabled: newState }),
            });
            skill.enabled = newState;
            this.showNotify('✓ ' + skill.name + ' 已' + (newState ? '启用' : '禁用'), true);
            if (this.selectedSkill?.name === skill.name && this.selectedSkill?.category === skill.category) {
              this.selectedSkill.enabled = newState;
            }
          } catch (e) {
            this.showNotify('操作失败: ' + e.message, false);
          }
        },

        startEditSkill(skill) {
          if (!skill || !skill.content) {
            this.showNotify('⚠️ 该技能没有可编辑的 SKILL.md 内容', false);
            return;
          }
          this.editingSkill = skill;
          this.editingContent = skill.content;
          this.selectedSkill = null;
          this.deletingSkill = null;
        },

        async saveSkillContent() {
          const skill = this.editingSkill;
          if (!skill) return;
          try {
            await this.api('/skills/' + encodeURIComponent(skill.category) + '/' + encodeURIComponent(skill.name) + '/content', {
              method: 'PUT',
              body: JSON.stringify({ content: this.editingContent }),
            });
            // Update local data
            skill.content = this.editingContent;
            if (this.selectedSkill?.name === skill.name) {
              this.selectedSkill.content = this.editingContent;
            }
            this.editingSkill = null;
            this.showNotify('✓ SKILL.md 已保存', true);
            await this.loadSkills();
          } catch (e) {
            this.showNotify('保存失败: ' + e.message, false);
          }
        },

        confirmDeleteSkill(skill) {
          this.deletingSkill = skill;
          this.editingSkill = null;
          this.selectedSkill = null;
        },

        async deleteSkill() {
          const skill = this.deletingSkill;
          if (!skill) return;
          try {
            await this.api('/skills/' + encodeURIComponent(skill.category) + '/' + encodeURIComponent(skill.name), {
              method: 'DELETE',
            });
            this.deletingSkill = null;
            this.showNotify('✓ 已删除 ' + skill.category + '/' + skill.name, true);
            await this.loadSkills();
          } catch (e) {
            this.showNotify('删除失败: ' + e.message, false);
          }
        },

        async createSkill() {
          const s = this.newSkill;
          if (!s.category || !s.name) {
            this.showNotify('请填写分类和技能名称', false);
            return;
          }
          try {
            await this.api('/skills', {
              method: 'POST',
              body: JSON.stringify(s),
            });
            this.showSkillCreate = false;
            this.newSkill = { category: '', name: '', content: '' };
            this.showNotify('✓ 技能 ' + s.category + '/' + s.name + ' 已创建', true);
            await this.loadSkills();
          } catch (e) {
            this.showNotify('创建失败: ' + e.message, false);
          }
        },

        async importSkill() {
          const s = this.importSkill;
          if (!s.category || !s.name || !this.importSkillFile) {
            this.showNotify('请填写分类、名称并选择文件', false);
            return;
          }
          try {
            const formData = new FormData();
            formData.append('category', s.category);
            formData.append('name', s.name);
            formData.append('file', this.importSkillFile);
            const res = await fetch('/api/skills/import', {
              method: 'POST',
              body: formData,
            });
            if (!res.ok) {
              const err = await res.json().catch(() => ({ detail: res.statusText }));
              throw new Error(err.detail || res.statusText);
            }
            this.showSkillImport = false;
            this.importSkill = { category: '', name: '' };
            this.importSkillFile = null;
            this.showNotify('✓ 已导入到 ' + s.category + '/' + s.name, true);
            await this.loadSkills();
          } catch (e) {
            this.showNotify('导入失败: ' + e.message, false);
          }
        },

        showNotify(msg, ok) {
          this.skillNotifyMsg = msg;
          this.skillNotifyOk = ok;
          setTimeout(() => { this.skillNotifyMsg = ''; }, 4000);
        },

        formatFileSize(bytes) {
          if (!bytes) return '0 B';
          if (bytes < 1024) return bytes + ' B';
          if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
          return (bytes / 1048576).toFixed(1) + ' MB';
        },

        // ========== Cron ==========
        async loadCron() {
          this.cronLoading = true;
          try {
            const data = await this.api('/cron');
            this.cronJobs = data.jobs || [];
          } catch (e) { this.cronJobs = []; }
          this.cronLoading = false;
        },

        // ========== Logs ==========
        async loadLogs() {
          this.logLoading = true;
          try {
            const data = await this.api('/logs');
            this.logFiles = data.logs || [];
          } catch (e) { this.logFiles = []; }
          this.logLoading = false;
        },
        async loadLogContent(filename) {
          try {
            const data = await this.api('/logs/' + encodeURIComponent(filename));
            this.logContent = data.content;
            this.logContentName = filename;
          } catch (e) {
            this.logContent = '加载失败: ' + e.message;
            this.logContentName = filename;
          }
        },
      };
    }
