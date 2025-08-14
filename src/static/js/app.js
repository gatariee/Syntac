const state = {
    current: { name: null, sub: null },
    containerPositions: {
        globals: { x: 0, y: 0 },
        extras: { x: 0, y: 0 },
        preview: { x: 0, y: 0 }
    },
    zIndexCounter: 100
};

const elements = {
    menu: document.getElementById('menu'),
    globalsW: document.getElementById('globals'),
    extrasW: document.getElementById('extras'),
    formG: document.getElementById('form-globals'),
    formE: document.getElementById('form-extras'),
    previewW: document.getElementById('preview'),
    previewContent: document.getElementById('preview-content'),
    searchBox: document.getElementById('search-box'),
    docW: document.getElementById('documentation'),
    docContent: document.getElementById('doc-content')
};

const initDraggable = () => {
    interact('#globals, #extras, #preview h3').draggable({
        listeners: {
            move: (event) => {
                const target = event.target.parentElement.id === 'preview'
                    ? event.target.parentElement
                    : event.target;

                if (!target || !state.containerPositions.hasOwnProperty(target.id)) return;

                const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

                target.style.transform = `translate(${x}px, ${y}px)`;
                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
                state.containerPositions[target.id] = { x, y };
            },
            start: (event) => {
                const target = event.target.parentElement.id === 'preview'
                    ? event.target.parentElement
                    : event.target;

                if (target) {
                    target.style.zIndex = state.zIndexCounter++;
                }
            }
        }
    });
};

const storage = {
    save: () => {
        const data = collectFormData();
        Object.keys(data)
            .filter(key => !key.startsWith('__'))
            .forEach(key => {
                localStorage.setItem('field_' + key, JSON.stringify(data[key]));
            });
    },

    load: () => {
        const savedState = {};
        const moduleGlobals = connectors?.[state.current.name]?.globals || [];
        const moduleExtras = connectors?.[state.current.name]?.subs
            ?.find(s => s.key === state.current.sub)?.extras || [];

        [...moduleGlobals, ...moduleExtras].forEach(field => {
            const savedValue = localStorage.getItem('field_' + field.name);
            if (savedValue !== null) {
                savedState[field.name] = JSON.parse(savedValue);
            }
        });

        return savedState;
    }
};

const buildMenu = (query = '') => {
    elements.menu.innerHTML = '';
    const lowerCaseQuery = query.toLowerCase();

    Object.keys(connectors).forEach(name => {
        const isModuleMatch = name.toLowerCase().includes(lowerCaseQuery);
        const matchingSubs = connectors?.[name]?.subs
            ?.filter(s => s.key.toLowerCase().includes(lowerCaseQuery)) || [];

        if (isModuleMatch || matchingSubs.length > 0) {
            const head = createMenuHeader(name);
            const subList = createSubList(name, query ? matchingSubs : connectors?.[name]?.subs || []);

            elements.menu.appendChild(head);
            elements.menu.appendChild(subList);
        }
    });
};

const createMenuHeader = (name) => {
    const head = document.createElement('li');
    head.className = 'heading active';
    head.textContent = name;
    head.onclick = () => head.classList.toggle('active');
    return head;
};

const createSubList = (name, subs) => {
    const subList = document.createElement('ul');
    subList.className = 'sub-list';

    subs.forEach(s => {
        const li = document.createElement('li');
        li.className = 'sub';
        li.textContent = s.key;
        li.dataset.connector = name;
        li.dataset.sub = s.key;
        li.onclick = () => selectSub(name, s.key);
        subList.appendChild(li);
    });

    return subList;
};

const selectSub = (name, sub) => {
    document.querySelectorAll('li.sub')
        .forEach(e => e.classList.remove('active'));

    const el = document.querySelector(
        `li.sub[data-connector="${name}"][data-sub="${sub}"]`
    );
    el?.classList.add('active');

    const prevConnector = state.current.name;
    state.current = { name, sub };

    localStorage.setItem('lastSelectedSub', JSON.stringify(state.current));

    if (name !== prevConnector) buildGlobals(name);
    buildExtras(name, sub);
    resetContainerPositions();
    updatePreview();

    const subModule = connectors?.[name]?.subs?.find(s => s.key === sub);
    if (subModule && subModule.doc) {
        elements.docContent.innerHTML = subModule.doc;
        elements.docW.style.display = '';
    } else {
        elements.docW.style.display = 'none';
    }
};

const resetContainerPositions = () => {
    state.containerPositions = {
        globals: { x: 0, y: 0 },
        extras: { x: 0, y: 0 },
        preview: { x: 0, y: 0 }
    };

    [elements.globalsW, elements.extrasW, elements.previewW].forEach(container => {
        container.style.transform = `translate(0px, 0px)`;
        container.setAttribute('data-x', 0);
        container.setAttribute('data-y', 0);
    });
};

const buildGlobals = (name) => {
    elements.formG.innerHTML = '';
    const globs = connectors?.[name]?.globals || [];
    const savedState = storage.load();

    if (!globs.length) {
        elements.globalsW.style.display = 'none';
        return;
    }

    elements.globalsW.style.display = '';
    globs.forEach(f => {
        const fieldHtml = createFieldHtml(f, savedState);
        elements.formG.insertAdjacentHTML('beforeend', fieldHtml);
    });

    elements.formG.oninput = () => {
        storage.save();
        updatePreview();
    };
};

const buildExtras = (name, sub) => {
    elements.formE.innerHTML = '';
    const extra = connectors?.[name]?.subs
        ?.find(s => s.key === sub)?.extras || [];
    const savedState = storage.load();

    if (!extra.length) {
        elements.extrasW.style.display = 'none';
        return;
    }

    elements.extrasW.style.display = '';
    extra.forEach(f => {
        const fieldHtml = createFieldHtml(f, savedState);
        elements.formE.insertAdjacentHTML('beforeend', fieldHtml);
    });

    elements.formE.oninput = () => {
        storage.save();
        updatePreview();
    };
};

const createFieldHtml = (field, savedValues = {}) => {
    const savedValue = savedValues[field.name];

    if (field.type === 'bool') {
        const isChecked = savedValue !== undefined ? savedValue : (field.default || false);
        return `
        <div class="field checkbox">
          <label>
            <input
              type="checkbox"
              name="${field.name}"
              ${isChecked ? 'checked' : ''}
            />
            ${field.name}
          </label>
        </div>
      `;
    }

    const value = savedValue !== undefined ? savedValue : (field.default || '');
    return `
      <div class="field">
        <label>${field.name} (${field.type})</label>
        <input
          type="text"
          name="${field.name}"
          value="${value}"
        />
      </div>
    `;
};

const collectFormData = () => {
    const data = {
        __connector: state.current.name,
        __sub: state.current.sub
    };

    [elements.globalsW, elements.extrasW].forEach(container => {
        container.querySelectorAll('input').forEach(input => {
            const name = input.name;
            if (input.type === 'checkbox') {
                data[name] = input.checked;
            } else if (input.value !== '') {
                data[name] = input.value;
            }
        });
    });

    return data;
};

const updatePreview = async () => {
    if (!state.current.name) return;

    elements.previewContent.value = elements.previewContent.value;

    try {
        const res = await fetch('/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collectFormData())
        });

        const js = await res.json();
        elements.previewContent.value = js.command || js.error;
    } catch (e) {
        elements.previewContent.value = e.message;
    }
};

const init = () => {
    initDraggable();
    buildMenu();
  
    const lastSelected = localStorage.getItem('lastSelectedSub');
    if (lastSelected) {
        const { name, sub } = JSON.parse(lastSelected);
        selectSub(name, sub);
    } else {
        elements.docW.style.display = 'none';
    }
  
    elements.searchBox.addEventListener('input', (e) => {
        buildMenu(e.target.value);
    });
  };

document.addEventListener('DOMContentLoaded', init);